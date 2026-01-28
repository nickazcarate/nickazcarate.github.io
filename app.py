from __future__ import annotations
from urllib.parse import urlparse, parse_qs
import json
import os
import re
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Tuple

import pandas as pd
import streamlit as st
from rapidfuzz import process, fuzz

import requests

import base64
import requests
from urllib.parse import urlparse, parse_qs, unquote


st.set_page_config(page_title="Drag Race Bracket Scorer", layout="wide")

STATE_PATH = "season_state.json"
SCORES_CSV_PATH = "scores.csv"

def parse_checkbox_option_from_column(col_name: str, base_label: str) -> Optional[str]:
    """
    Google Forms checkbox exports usually create columns like:
      "<Question text> [Option text]"
    This tries to extract "Option text".
    """
    c = norm_text(col_name)
    b = norm_text(base_label)
    if not c or not b:
        return None

    # If it starts with the base question text, strip it off
    if c.startswith(b):
        tail = c[len(b):].strip()
        # common separators: space, dash, colon, brackets
        tail = tail.lstrip(" -–—:").strip()

        # Sometimes it appears like "[Option]" or "(Option)"
        tail = tail.strip()
        tail = re.sub(r'^[\[\(]\s*', '', tail)
        tail = re.sub(r'\s*[\]\)]$', '', tail).strip()

        return tail if tail else None

    return None

def is_checkbox_group(base_label: str, cols_in_group: List[str]) -> bool:
    """
    Heuristic: checkbox groups often have MANY columns and the column names
    look like "<question> <option>" (question repeated in each column).
    """
    if len(cols_in_group) < 2:
        return False

    b = norm_text(base_label)
    starts = sum(1 for c in cols_in_group if norm_text(c).startswith(b))
    # if most columns start with the base label, likely checkbox-style
    return starts >= max(2, int(0.7 * len(cols_in_group)))

def derive_option_universe(base_label: str, cols_in_group: List[str]) -> List[str]:
    """
    Extract option names for checkbox columns.
    Fallback: if extraction fails, use the raw column names as options.
    """
    opts = []
    for c in cols_in_group:
        opt = parse_checkbox_option_from_column(c, base_label)
        if opt:
            opts.append(opt)

    # If nothing extracted, fallback to using columns themselves
    if not opts:
        opts = [norm_text(c) for c in cols_in_group if norm_text(c)]

    # stable dedupe
    seen = set()
    out = []
    for o in opts:
        k = norm_key(o)
        if k and k not in seen:
            seen.add(k)
            out.append(o)
    return out


def award_new_bonuses(state: dict, contestants: List[str]) -> Dict[str, int]:
    """
    Find season-timing questions across all episodes that:
      - have correct_answers filled
      - are not paid yet
      - have stored season_picks
    Compute points and add them to state["bonus_by_user"].
    Returns newly_awarded_by_user for UI display.
    """
    state.setdefault("bonus_by_user", {})
    newly_awarded: Dict[str, int] = {}

    for src_ep_id, src_ep_data in state.get("episodes", {}).items():
        questions = src_ep_data.get("questions", {})
        season_picks = src_ep_data.get("season_picks", {})

        for qid, qd in questions.items():
            # Backward compatible defaults
            qd2 = dict(qd)
            qd2.setdefault("paid", False)
            q = QuestionSpec(**qd2)

            if q.timing != "season":
                continue
            if q.no_correct_answer:
                # mark paid so it doesn't keep resurfacing
                if not q.paid:
                    q.paid = True
                    questions[qid] = asdict(q)
                continue
            if q.paid:
                continue
            if not q.correct_answers:
                continue  # still unknown
            if qid not in season_picks:
                continue  # no stored picks yet (episode never scored)

            # Award for each user who answered back then
            for username, picks in season_picks[qid].items():
                pts, _ = score_question_picks(picks, q, contestants, ep=None)
                pts = float(pts)

                if pts:
                    state["bonus_by_user"][username] = float(state["bonus_by_user"].get(username, 0.0)) + pts
                    newly_awarded[username] = float(newly_awarded.get(username, 0.0)) + pts

            # Mark question paid so it won’t award again
            q.paid = True
            questions[qid] = asdict(q)

    return newly_awarded

def store_season_picks(state: dict, ep: EpisodeSpec, df: pd.DataFrame) -> None:
    ep_entry = state["episodes"].setdefault(ep.episode_id, {})
    season_picks = ep_entry.setdefault("season_picks", {})  # qid -> username -> picks(list)

    for qid, q in ep.questions.items():
        if q.timing != "season":
            continue

        season_picks.setdefault(qid, {})
        for _, r in df.iterrows():
            username = effective_username(r, ep.username_col)
            if not username:
                continue
            season_picks[qid][username] = get_row_picks(r, q.columns)

def write_scores_csv(state: dict) -> pd.DataFrame:
    """
    Builds and writes the wide season scores CSV to disk.
    Returns the dataframe for convenience.
    """
    scores_df = build_scores_csv_from_state(state)
    scores_df.to_csv(SCORES_CSV_PATH, index=False)
    return scores_df


def github_upsert_file(owner, repo, branch, path, content_bytes, token, commit_message):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
    }

    # Get existing file SHA (if it exists)
    r = requests.get(url, headers=headers, params={"ref": branch})
    sha = None
    if r.status_code == 200:
        sha = r.json().get("sha")
    elif r.status_code not in (404,):
        raise RuntimeError(f"GitHub GET failed: {r.status_code} {r.text}")

    payload = {
        "message": commit_message,
        "content": base64.b64encode(content_bytes).decode("utf-8"),
        "branch": branch,
    }
    if sha:
        payload["sha"] = sha

    r2 = requests.put(url, headers=headers, json=payload)
    if r2.status_code not in (200, 201):
        raise RuntimeError(f"GitHub PUT failed: {r2.status_code} {r2.text}")
    return r2.json()


def ep_col_name(ep_id: str) -> str:
    ep_id = str(ep_id).strip()
    # If you want literally "Ep #2", use: return f"Ep #{ep_id}"
    return f"Ep {ep_id}"


def build_scores_csv_from_state(state: dict) -> pd.DataFrame:
    episodes = state.get("episodes", {})
    bonus_by_user = state.get("bonus_by_user", {})  # username -> bonus

    if not episodes and not bonus_by_user:
        return pd.DataFrame(columns=["Username", "Bonus", "Episode Total", "Grand Total"])

    def sort_key(x):
        try:
            return (0, int(str(x)))
        except Exception:
            return (1, str(x))

    ep_ids = sorted(episodes.keys(), key=sort_key)

    # episode totals per user
    per_user_ep = {}
    for ep_id in ep_ids:
        rows = episodes.get(ep_id, {}).get("last_scored_rows", [])
        for r in rows:
            u = canonical_username(r.get("username", ""))
            if not u:
                continue
            per_user_ep.setdefault(u, {})
            per_user_ep[u][ep_id] = float(per_user_ep[u].get(ep_id, 0.0)) + float(r.get("total", 0.0))

    # union of users from episodes + bonuses
    users = set(per_user_ep.keys()) | set(canonical_username(u) for u in bonus_by_user.keys())

    out_rows = []
    for u in sorted(users):
        row = {"Username": u}
        episode_total = 0

        for ep_id in ep_ids:
            v = float(per_user_ep.get(u, {}).get(ep_id, 0.0))
            row[ep_col_name(ep_id)] = v
            episode_total += v

        bonus = float(bonus_by_user.get(u, 0.0))
        row["Bonus"] = bonus
        row["Episode Total"] = episode_total
        row["Grand Total"] = episode_total + bonus
        out_rows.append(row)

    df = pd.DataFrame(out_rows)
    df = df.sort_values(["Grand Total", "Username"], ascending=[False, True])
    return df


# -------------------------
# Normalization & Matching
# -------------------------

import unicodedata

def normalize_unicode_punct(s: str) -> str:
    """
    Normalize curly quotes/dashes to plain ASCII + collapse whitespace.
    Also fixes common mojibake when it slipped through.
    """
    s = norm_text(s)
    if not s:
        return ""

    # If mojibake slipped through, try to repair it
    if "â" in s or "�" in s:
        try:
            repaired = s.encode("latin-1", errors="ignore").decode("utf-8", errors="ignore")
            if repaired:
                s = repaired
        except Exception:
            pass

    # Normalize unicode form
    s = unicodedata.normalize("NFKC", s)

    # Replace smart quotes/dashes with ASCII
    trans = {
        "\u2018": "'",  # left single quote
        "\u2019": "'",  # right single quote
        "\u201C": '"',  # left double quote
        "\u201D": '"',  # right double quote
        "\u2013": "-",  # en dash
        "\u2014": "-",  # em dash
        "\u2212": "-",  # minus sign
        "\u00A0": " ",  # non-breaking space
    }
    s = s.translate(str.maketrans(trans))

    # Collapse whitespace
    s = re.sub(r"\s+", " ", s).strip()
    return s

OTHER_SENTINELS_RAW = {
    "Other (Please Add in Next Question)",
    "Other",
    "Other (Please Add)",
}

OTHER_SENTINELS_KEY = {  # normalized keys
    "".join(ch.lower() for ch in s.strip() if ch.isalnum() or ch.isspace()).strip()
    for s in OTHER_SENTINELS_RAW
}

FREE_TEXT_USERNAME_COL = "Username (If not in above drop down)"


def fix_mojibake(s: str) -> str:
    s = norm_text(s)
    if not s:
        return s

    if "â" in s or "�" in s:
        try:
            repaired = s.encode("latin-1", errors="ignore").decode("utf-8", errors="ignore")
            if repaired and repaired.count("�") <= s.count("�"):
                return repaired
        except Exception:
            pass
    return s


def canonical_username(u: str) -> str:
    u = fix_mojibake(u)
    # Normalize unicode (handles curly quotes, weird spaces, etc.)
    u = unicodedata.normalize("NFKC", u)
    u = u.strip()
    # Collapse internal whitespace
    u = re.sub(r"\s+", " ", u)
    return u


def effective_username(row: pd.Series, username_col: str) -> str:
    """
    Use dropdown Username unless it's 'Other...' OR blank,
    then use free-text Username (If not in above drop down).
    """
    u = canonical_username(row.get(username_col, ""))
    u_key = norm_key(u)

    alt = canonical_username(row.get(FREE_TEXT_USERNAME_COL, ""))

    # If dropdown is Other OR blank, prefer alt if present
    if (not u) or (u_key in OTHER_SENTINELS_KEY):
        if alt:
            return alt

    return u

import re
import unicodedata
import pandas as pd

def norm_text(x) -> str:
    """
    Convert any value to a safe string:
      - None/NaN -> ""
      - strip
    DOES NOT do unicode punctuation normalization.
    """
    if x is None:
        return ""
    try:
        # pd.isna(None) is False, pd.isna("foo") is False, pd.isna(np.nan) is True
        if pd.isna(x):
            return ""
    except Exception:
        pass
    return str(x).strip()


def norm_key(x: str) -> str:
    s = normalize_unicode_punct(x)
    return "".join(ch.lower() for ch in s if ch.isalnum() or ch.isspace()).strip()

def fuzzy_match(name: str, choices: List[str], score_cutoff: int = 86) -> str:
    """Return best matching choice, or original string if no good match."""
    name = norm_text(name)
    if not name:
        return ""
    # Exact-ish first
    nk = norm_key(name)
    for c in choices:
        if norm_key(c) == nk:
            return c
    best = process.extractOne(name, choices, scorer=fuzz.WRatio)
    if best and best[1] >= score_cutoff:
        return best[0]
    return name

def extract_points(header: str) -> Optional[int]:
    """
    Try to parse "(5 Points)" / "(5 points)" from column header.
    Returns int or None.
    """
    h = norm_text(header)
    m = re.search(r"\(\s*(\d+)\s*points?\s*\)", h, flags=re.IGNORECASE)
    if m:
        return int(m.group(1))
    return None

def strip_pick_suffix(header: str) -> str:
    """
    Group related columns by removing suffix patterns like:
    - "(Pick #1)", "(Pick #2)"
    - "(Guess #1)"
    - " - Pick #1" etc.
    Also trims trailing whitespace.
    """
    h = norm_text(header)

    # Remove trailing (Pick #N) or (Guess #N) or similar
    h = re.sub(r"\(\s*(pick|guess)\s*#?\s*\d+\s*\)\s*$", "", h, flags=re.IGNORECASE)

    # Remove trailing "Pick #N" without parentheses
    h = re.sub(r"\s*[-–—]?\s*(pick|guess)\s*#?\s*\d+\s*$", "", h, flags=re.IGNORECASE)

    return h.strip()

def extract_pick_index(header: str) -> int:
    """
    If header contains Pick/Guess #N, return N else 1.
    Used for ordering columns within a grouped question.
    """
    h = norm_text(header)
    m = re.search(r"(pick|guess)\s*#?\s*(\d+)", h, flags=re.IGNORECASE)
    if m:
        return int(m.group(2))
    return 1

def guess_username_column(columns: List[str]) -> str:
    """
    Heuristic: choose a column containing 'username' in header, else fallback to first.
    """
    keys = [(c, norm_key(c)) for c in columns]
    for c, k in keys:
        if "username" in k:
            return c
    # sometimes it's "Name" or similar
    for c, k in keys:
        if k in ("name", "player", "player name"):
            return c
    return columns[0]


# -------------------------
# Data model
# -------------------------
@dataclass
class QuestionSpec:
    qid: str
    label: str                      # human-readable
    columns: List[str]              # df columns that hold picks for this question
    qtype: str = "contestant"       # contestant|text
    timing: str = "episode"         # episode|season
    points_per_pick: float = 0.0
    allow_duplicate_picks: bool = False
    no_correct_answer: bool = False # if True: always scores 0 (e.g., "no winner this week")
    correct_answers: List[str] = field(default_factory=list)  # empty = pending/unknown
    notes: str = ""                 # optional
    paid: bool = False  # NEW: for season questions, has bonus been awarded already?
    checkbox_scoring: bool = False
    option_universe: List[str] = field(default_factory=list)

@dataclass
class EpisodeSpec:
    episode_id: str
    username_col: str
    questions: Dict[str, QuestionSpec]  # qid -> spec


# -------------------------
# Persistence
# -------------------------
def load_state() -> dict:
    if os.path.exists(STATE_PATH):
        try:
            with open(STATE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_state(state: dict) -> None:
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def ensure_state_defaults(state: dict) -> dict:
    state.setdefault("season_name", "Drag Race Season")
    state.setdefault("contestants", [])
    state.setdefault("episodes", {})
    state.setdefault("bonus_by_user", {})  # <-- NEW: username -> bonus points total
    return state


# -------------------------
# Auto-detect questions from a dataframe
# -------------------------
def detect_question_groups(df: pd.DataFrame, username_col: str) -> Dict[str, Tuple[str, List[str], int, bool, List[str]]]:
    """
    Returns dict: qid -> (label, columns, points_per_pick_guess, is_checkbox, option_universe)
    - label is the grouped header
    - columns is ordered by pick index
    - points_per_pick_guess is extracted from the first column that has points.
    """
    ignore_like = {"timestamp", "email address", "email", "e-mail", "name"}
    cols = list(df.columns)

    question_cols = []
    for c in cols:
        ck = norm_key(c)
        if c == username_col:
            continue
        if any(tok in ck for tok in ignore_like) and "points" not in ck:
            # still allow if it's a real question with points
            # but typical meta columns don't have points
            pass
        # We consider "question-ish" anything that isn't timestamp/email and isn't username
        if ck in ignore_like:
            continue
        if "timestamp" in ck and "points" not in ck:
            continue
        if "email address" in ck and "points" not in ck:
            continue
        question_cols.append(c)

    # group by stripped header
    groups: Dict[str, List[str]] = {}
    for c in question_cols:
        base = strip_pick_suffix(c)
        groups.setdefault(base, []).append(c)

    # order columns by pick index
    out: Dict[str, Tuple[str, List[str], int, bool, List[str]]] = {}
    for base, cols_in_group in groups.items():
        ordered = sorted(cols_in_group, key=extract_pick_index)

        p = None
        for col in ordered:
            p = extract_points(col)
            if p is not None:
                break
        points_guess = p if p is not None else 0

        qid = re.sub(r"[^a-z0-9]+", "_", norm_key(base)).strip("_")
        if not qid:
            qid = f"q_{abs(hash(base)) % 10**8}"

        checkbox_flag = is_checkbox_group(base, ordered)
        universe = derive_option_universe(base, ordered) if checkbox_flag else []

        out[qid] = (base, ordered, points_guess, checkbox_flag, universe)

    return out


# -------------------------
# Scoring
# -------------------------
def parse_text_answers(raw: str) -> List[str]:
    """
    Accept comma-separated answers OR one-per-line.
    """
    raw = norm_text(raw)
    if not raw:
        return []
    if "\n" in raw:
        parts = [p.strip() for p in raw.splitlines()]
    else:
        parts = [p.strip() for p in raw.split(",")]
    return [p for p in parts if p]

def get_row_picks(row: pd.Series, columns: List[str]) -> List[str]:
    picks = []
    for c in columns:
        v = norm_text(row.get(c, ""))
        if v:
            picks.append(v)
    return picks

def apply_implied_outcomes(ep: EpisodeSpec) -> None:
    """
    Mutates episode question specs so that:
    - WINNER correct answers are also treated as TOP correct answers
    - ELIMINATED correct answers are also treated as BOTTOM correct answers

    This is done by finding questions whose labels contain keywords.
    It is robust to different forms across episodes.
    """
    # Identify question IDs by label text (since you don't have stable keys yet)
    winner_qids = []
    top_qids = []
    elim_qids = []
    bottom_qids = []

    for qid, q in ep.questions.items():
        lk = norm_key(q.label)
        # winner
        if ("who will win" in lk) or ("winner" in lk and "season" not in lk and "superstar" not in lk):
            winner_qids.append(qid)
        # top group
        if ("top" in lk) and ("who else" in lk or "top 3" in lk or "top three" in lk or "top group" in lk):
            top_qids.append(qid)
        # eliminated
        if ("who will be eliminated" in lk) or ("eliminated" in lk):
            elim_qids.append(qid)
        # bottom group
        if ("bottom" in lk) and ("who else" in lk or "bottom 3" in lk or "bottom three" in lk or "bottom group" in lk):
            bottom_qids.append(qid)

    def merge_answers(src_qids: List[str], dst_qids: List[str]) -> None:
        # Union correct answers from all src into all dst
        src = set()
        for sid in src_qids:
            src.update(ep.questions[sid].correct_answers or [])
        if not src:
            return
        for did in dst_qids:
            dst = list(ep.questions[did].correct_answers or [])
            merged = list(dict.fromkeys(dst + list(src)))  # stable dedupe
            ep.questions[did].correct_answers = merged

    # winners count as top
    merge_answers(winner_qids, top_qids)
    # eliminated count as bottom
    merge_answers(elim_qids, bottom_qids)

def score_question_picks(
    picks: List[str],
    q: QuestionSpec,
    contestants: List[str],
    ep: Optional[EpisodeSpec] = None,  # optional so existing callers can pass it
) -> Tuple[float, Dict[str, object]]:
    """
    Scores a single question for one response row.
    Adds optional "bucket fallback" behavior:
      - If this is the WINNER question and the pick isn't a winner but *is in TOP correct answers*,
        award TOP points_per_pick instead (once).
      - If this is the ELIMINATED question and the pick isn't eliminated but *is in BOTTOM correct answers*,
        award BOTTOM points_per_pick instead (once).
    """
    detail = {"picks": picks, "correct": q.correct_answers, "status": "resolved"}

    if q.no_correct_answer:
        detail["status"] = "no_correct_answer"
        return 0, detail

    if not q.correct_answers:
        detail["status"] = "pending"
        return 0, detail
    
    # ✅ NEW: checkbox scoring = compare checked vs unchecked across full universe
    if q.qtype == "text" and getattr(q, "checkbox_scoring", False) and q.option_universe:
        # picks = checked options (because get_row_picks only collects non-empty columns)
        checked = {norm_key(p) for p in picks if norm_text(p)}
        correct_in = {norm_key(a) for a in q.correct_answers if norm_text(a)}
        universe = {norm_key(o) for o in q.option_universe if norm_text(o)}

        # Safety: only score items we know are in the universe
        checked = checked & universe
        correct_in = correct_in & universe

        # Correct “in” guesses (checked & should be in)
        tp = len(checked & correct_in)

        # Correct “not in” guesses (unchecked & should NOT be in)
        unchecked = universe - checked
        should_not_be_in = universe - correct_in
        tn = len(unchecked & should_not_be_in)

        num_correct = tp + tn
        pts = float(q.points_per_pick) * float(num_correct)

        detail.update({
            "status": "resolved_checkbox",
            "normalized_checked": sorted(list(checked)),
            "normalized_correct_in": sorted(list(correct_in)),
            "universe_size": len(universe),
            "tp": tp,
            "tn": tn,
            "num_correct": num_correct,
            "points": pts,
        })
        return pts, detail

    # Normalize picks / answers based on type
    if q.qtype == "contestant":
        choice_universe = contestants if contestants else q.correct_answers
        picks_norm = [fuzzy_match(p, choice_universe) for p in picks]
        correct_set = set(fuzzy_match(a, choice_universe) for a in q.correct_answers)
    else:
        picks_norm = [norm_key(p) for p in picks]
        correct_set = set(norm_key(a) for a in q.correct_answers)

    # Deduplicate picks unless allowed
    if not q.allow_duplicate_picks:
        seen = set()
        deduped = []
        for p in picks_norm:
            if p not in seen:
                deduped.append(p)
                seen.add(p)
        picks_norm = deduped

    # Base scoring
    num_correct = sum(1 for p in picks_norm if p in correct_set)
    pts = q.points_per_pick * num_correct

    # ---- Bucket fallback (optional) ----
    # This is what makes your "4 points" example possible.
    if ep and q.qtype == "contestant" and pts == 0 and picks_norm:
        lk = norm_key(q.label)

        def find_first_question_by_keywords(must_contain: List[str]) -> Optional[QuestionSpec]:
            for _qid, _q in ep.questions.items():
                k = norm_key(_q.label)
                if all(s in k for s in must_contain):
                    return _q
            return None

        # Winner -> Top fallback
        if "who will win" in lk or ("winner" in lk and "season" not in lk and "superstar" not in lk):
            top_q = find_first_question_by_keywords(["top"])
            if top_q and top_q.correct_answers:
                top_set = set(fuzzy_match(a, contestants) for a in top_q.correct_answers) if contestants else set(top_q.correct_answers)
                if picks_norm[0] in top_set:
                    pts = top_q.points_per_pick  # award top points once
                    detail["status"] = "fallback_top_from_winner"

        # Eliminated -> Bottom fallback
        if "who will be eliminated" in lk or "eliminated" in lk:
            bottom_q = find_first_question_by_keywords(["bottom"])
            if bottom_q and bottom_q.correct_answers:
                bottom_set = set(fuzzy_match(a, contestants) for a in bottom_q.correct_answers) if contestants else set(bottom_q.correct_answers)
                if picks_norm[0] in bottom_set:
                    pts = bottom_q.points_per_pick
                    detail["status"] = "fallback_bottom_from_elim"

    detail["normalized_picks"] = picks_norm
    detail["num_correct"] = num_correct
    detail["points"] = pts
    return pts, detail

def score_episode_df(df: pd.DataFrame, ep: EpisodeSpec, contestants: List[str]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    for _, r in df.iterrows():
        username = effective_username(r, ep.username_col)
        if not username:
            continue

        total = 0
        per_q = {}

        for qid, q in ep.questions.items():
            picks = get_row_picks(r, q.columns)
            pts, _detail = score_question_picks(picks, q, contestants, ep=ep)
            per_q[qid] = pts
            total += pts

        rows.append({"username": username, "total": total, **per_q})

    scored = pd.DataFrame(rows)

    leaderboard = (
        scored.groupby("username", as_index=False)["total"]
        .sum()
        .sort_values("total", ascending=False)
    )
    return scored, leaderboard

def season_leaderboard(state: dict) -> pd.DataFrame:
    """
    Aggregate all episodes from stored per-episode scored rows if present,
    otherwise return empty.
    """
    all_rows = []
    for ep_id, ep_data in state.get("episodes", {}).items():
        scored_rows = ep_data.get("last_scored_rows", [])
        all_rows.extend(scored_rows)

    if not all_rows:
        return pd.DataFrame(columns=["username", "total"])

    df = pd.DataFrame(all_rows)
    if "username" not in df.columns or "total" not in df.columns:
        return pd.DataFrame(columns=["username", "total"])
    return df.groupby("username", as_index=False)["total"].sum().sort_values("total", ascending=False)


# -------------------------
# UI
# -------------------------
state = ensure_state_defaults(load_state())

st.title("RuPaul’s Drag Race Bracket Scorer — Flexible (Local)")

with st.sidebar:
    st.header("Season Setup")
    state["season_name"] = st.text_input("Season name", value=state.get("season_name", "Drag Race Season"))

    st.caption("Contestant list improves name matching for contestant questions.")
    contestants_text = st.text_area(
        "Contestants (one per line)",
        value="\n".join(state.get("contestants", [])),
        height=180
    )
    state["contestants"] = [line.strip() for line in contestants_text.splitlines() if line.strip()]

    st.divider()
    st.subheader("Episodes")
    existing_eps = sorted(state.get("episodes", {}).keys())
    st.write("Saved episodes:", ", ".join(existing_eps) if existing_eps else "None yet")

    st.divider()
    if st.button("Save season state"):
        save_state(state)
        scores_df = write_scores_csv(state)  # <-- writes scores.csv
        st.success(f"Saved to {STATE_PATH} and wrote {SCORES_CSV_PATH}")

        csv_bytes = scores_df.to_csv(index=False).encode("utf-8")

    if st.button("Reset season state (danger)"):
        state = ensure_state_defaults({})
        save_state(state)
        st.warning("Season state reset.")



# -------------------------
# 1) Load Google Form responses from a PUBLIC Google Sheet (single tab)
# -------------------------
import io

UA = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0 Safari/537.36"
}

def sheet_id_from_url(url: str) -> str:
    """
    Extract the spreadsheet ID from a Google Sheets URL.
    Supports:
      - https://docs.google.com/spreadsheets/d/<ID>/edit...
      - URLs with extra path/query params
    """
    url = (url or "").strip()
    m = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", url)
    if not m:
        raise ValueError("Could not find spreadsheet ID in the URL.")
    return m.group(1)

def gid_from_url(url: str) -> Optional[str]:
    """
    Extract gid from query (?gid=123) or fragment (#gid=123) if present.
    """
    url = (url or "").strip()
    parsed = urlparse(url)

    # query param gid=...
    q = parse_qs(parsed.query or "")
    if "gid" in q and q["gid"]:
        return str(q["gid"][0])

    # fragment gid=...
    frag = parsed.fragment or ""
    m = re.search(r"(?:^|[&#])gid=(\d+)", frag)
    if m:
        return m.group(1)

    return None

@st.cache_data(show_spinner=False)
def first_gid_from_public_sheet(sheet_id: str) -> str:
    """
    Best-effort scrape to find a gid in the public HTML.
    Used only if gid=0 fails and the URL didn’t provide a gid.
    """
    view_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit?usp=sharing"
    r = requests.get(view_url, headers=UA, timeout=20)
    if r.status_code != 200:
        raise ValueError(f"Could not open sheet HTML to detect gid (HTTP {r.status_code}).")

    html = r.text

    # Common patterns in the HTML/JS payload
    # Try gid first
    m = re.search(r'["\']gid["\']\s*:\s*(\d+)', html)
    if m:
        return m.group(1)

    # Sometimes it appears as gridId
    m = re.search(r'["\']gridId["\']\s*:\s*(\d+)', html)
    if m:
        return m.group(1)

    # Last resort: any "gid=123" occurrence
    m = re.search(r"gid=(\d+)", html)
    if m:
        return m.group(1)

    # If we truly can’t find it, fall back to 0
    return "0"

@st.cache_data(show_spinner=False, ttl=30)
def load_public_sheet_csv(sheet_id: str, gid: str) -> tuple[pd.DataFrame, str]:
    export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

    r = requests.get(export_url, headers=UA, timeout=20)
    if r.status_code != 200:
        raise ValueError(
            f"CSV export failed: HTTP {r.status_code}\nURL: {export_url}\nBody: {r.text[:200]}"
        )

    # IMPORTANT: decode bytes as UTF-8 (handles curly quotes/em-dashes correctly)
    csv_text = r.content.decode("utf-8-sig", errors="replace")

    df = pd.read_csv(io.StringIO(csv_text))
    df.columns = [str(c) for c in df.columns]
    return df, export_url

def try_load(sheet_id: str) -> tuple[pd.DataFrame, str, str]:
    # 1) Try the default first-tab gid
    try:
        df, url = load_public_sheet_csv(sheet_id, "0")
        return df, url, "0"
    except Exception:
        pass

    # 2) Fallback: scrape a gid (more expensive / less reliable)
    gid = first_gid_from_public_sheet(sheet_id)
    df, url = load_public_sheet_csv(sheet_id, gid)
    return df, url, gid


st.subheader("1) Load this episode’s Google Form responses from Google Sheets")

sheet_url = st.text_input(
    "Paste Google Sheet link (must be 'Anyone with the link can view')",
    value="",
    key="sheet_url",
)

load_btn = st.button("Load sheet", type="primary", key="load_sheet_btn")

if not sheet_url:
    st.info("Paste the link above, then click **Load sheet**.")
    st.stop()

if sheet_url and load_btn:
    try:
        sheet_id = sheet_id_from_url(sheet_url)

        df, export_url, gid = try_load(sheet_id)

        st.session_state["loaded_export_url"] = export_url

        if df.empty:
            st.error("Loaded, but the sheet appears empty. Are you sure responses exist in this sheet?")
            st.stop()

        file_sig = (sheet_id, gid, df.shape, tuple(df.columns))
        if st.session_state.get("loaded_df_sig") != file_sig:
            st.session_state["loaded_df_sig"] = file_sig
            st.session_state.pop("working_episode", None)
            st.session_state.pop("working_episode_id", None)

        st.session_state["loaded_df"] = df
        st.session_state["loaded_episode_gid"] = gid
        st.session_state["loaded_sheet_id"] = sheet_id

        st.success(f"Loaded {len(df):,} rows (gid={gid}).")
        st.caption("CSV export URL used (open it in your browser if debugging):")
        st.code(export_url, language="text")
        st.write("Preview", df.head(30))

    except Exception as e:
        st.error(f"Could not load sheet. Error: {e}")
        st.stop()



st.divider()
st.subheader("2) Set up episode questions + enter results")

if "loaded_df" not in st.session_state:
    st.info("Load a sheet above first.")
    st.stop()

df = st.session_state["loaded_df"]

# Pick username column
cols = list(df.columns)
username_default = guess_username_column(cols)
username_col = st.selectbox(
    "Which column identifies the player (username)?",
    options=cols,
    index=cols.index(username_default) if username_default in cols else 0
)

# Episode ID
default_ep_id = f"ep_{st.session_state.get('loaded_episode_gid','0')}"
episode_id = st.text_input(
    "Episode ID (Number only, e.g. 2, 3, 4, 5, etc.)",
    value=st.session_state.get("working_episode_id", default_ep_id)
)

# Detect question groups for this sheet
detected = detect_question_groups(df, username_col=username_col)
if not detected:
    st.error("No question columns detected. Check the username column selection.")
    st.stop()

# Load existing episode config if present
existing_ep = state.get("episodes", {}).get(episode_id) if episode_id else None

# (Re)build working episode when episode_id changes OR not present yet
if (
    "working_episode" not in st.session_state
    or st.session_state.get("working_episode_id") != episode_id
):
    questions: Dict[str, QuestionSpec] = {}

    if existing_ep and existing_ep.get("questions"):
        # Load saved questions
        for qid, qd in existing_ep["questions"].items():
            questions[qid] = QuestionSpec(**qd)

        # Merge in newly detected questions not in saved config
        for qid, (label, qcols, pguess, is_cb, universe) in detected.items():
            if qid not in questions:
                if is_cb:
                    qtype_guess = "text"
                else:
                    qtype_guess = "contestant" if state.get("contestants") else "text"
                questions[qid] = QuestionSpec(
                    qid=qid,
                    label=label,
                    columns=qcols,
                    qtype=qtype_guess,
                    timing="episode",
                    points_per_pick=pguess or 0,
                    checkbox_scoring=is_cb,
                    option_universe=universe,
                )
            else:
                questions[qid].columns = qcols
                questions[qid].checkbox_scoring = bool(is_cb)
                questions[qid].option_universe = list(universe)
    else:
        # Fresh init from detection
        for qid, (label, qcols, pguess, is_cb, universe) in detected.items():
            # IMPORTANT: checkbox questions should default to text
            if is_cb:
                qtype_guess = "text"
            else:
                qtype_guess = "contestant" if state.get("contestants") else "text"

            questions[qid] = QuestionSpec(
                qid=qid,
                label=label,
                columns=qcols,
                qtype=qtype_guess,
                timing="episode",
                points_per_pick=float(pguess or 0.0),
                checkbox_scoring=bool(is_cb),
                option_universe=list(universe),
            )

    st.session_state["working_episode"] = EpisodeSpec(
        episode_id=episode_id or "UNNAMED",
        username_col=username_col,
        questions=questions,
    )
    st.session_state["working_episode_id"] = episode_id

ep: EpisodeSpec = st.session_state["working_episode"]
ep.username_col = username_col
ep.episode_id = episode_id or ep.episode_id

st.caption(f"Detected {len(detected)} question groups. Editing episode: **{ep.episode_id}**")

pending_qids, resolved_qids = [], []

# Full question editor UI
for qid, q in ep.questions.items():
    # Keep columns synced to detection if present
    if qid in detected:
        _, detected_cols, _, is_cb, universe = detected[qid]
        q.columns = detected_cols
        q.checkbox_scoring = bool(is_cb)
        q.option_universe = list(universe)

    with st.expander(q.label, expanded=False):
        st.caption("Columns captured: " + " | ".join(q.columns))

        c1, c2, c3, c4 = st.columns([1.2, 1.0, 1.0, 1.2])
        with c1:
            q.qtype = st.selectbox(
                "Type", ["contestant", "text"],
                index=0 if q.qtype == "contestant" else 1,
                key=f"type_{qid}"
            )
        with c2:
            q.timing = st.selectbox(
                "Timing", ["episode", "season"],
                index=0 if q.timing == "episode" else 1,
                key=f"timing_{qid}"
            )
        with c3:
            q.points_per_pick = st.number_input(
                "Points per pick",
                min_value=0.0,
                value=float(q.points_per_pick or 0.0),
                step=0.5,
                format="%.2f",
                key=f"pts_{qid}",
            )
        with c4:
            q.allow_duplicate_picks = st.checkbox(
                "Allow duplicate picks?",
                value=bool(q.allow_duplicate_picks),
                key=f"dup_{qid}"
            )

        q.no_correct_answer = st.checkbox(
            "No correct answer this time (everyone gets 0)?",
            value=bool(q.no_correct_answer),
            key=f"nocorrect_{qid}"
        )

        if q.no_correct_answer:
            q.correct_answers = []
            st.info("This question will award 0 points to everyone.")
        else:
            if q.qtype == "contestant":
                if not state.get("contestants"):
                    st.warning("Add contestants in the sidebar for best matching.")
                    free = st.text_input(
                        "Type correct answers (comma-separated)",
                        value=",".join(q.correct_answers),
                        key=f"ans_free_{qid}"
                    )
                    q.correct_answers = parse_text_answers(free)
                else:
                    q.correct_answers = st.multiselect(
                        "Correct answer(s)",
                        options=state["contestants"],
                        default=[a for a in q.correct_answers if a in state["contestants"]],
                        key=f"ans_{qid}"
                    )
            else:
                raw = st.text_area(
                    "Correct answer(s) (comma-separated or one per line). Leave blank if unknown yet.",
                    value="\n".join(q.correct_answers),
                    height=90,
                    key=f"ans_text_{qid}"
                )
                q.correct_answers = parse_text_answers(raw)

        # Status badge
        if q.no_correct_answer:
            resolved_qids.append(qid)
            st.success("Status: NO CORRECT ANSWER (scores 0).")
        elif q.correct_answers:
            resolved_qids.append(qid)
            st.success("Status: RESOLVED (will score).")
        else:
            pending_qids.append(qid)
            st.warning("Status: PENDING (scores 0 until you fill in correct answer).")

st.subheader("3) Calculate")
colA, colB, colC = st.columns([1, 1, 2])

with colA:
    run_score = st.button("Score this episode", type="primary")
with colB:
    save_ep = st.button("Save episode config to season_state.json")
with colC:
    st.caption(
        f"Resolved questions: {len(resolved_qids)} • Pending questions: {len(pending_qids)} • "
        "Pending questions count as 0 until resolved."
    )

if save_ep:
    if not ep.episode_id or ep.episode_id == "UNNAMED":
        st.error("Please enter an Episode ID/label before saving.")
    else:
        prev = state["episodes"].get(ep.episode_id, {})

        existing_rows = prev.get("last_scored_rows", [])

        state["episodes"][ep.episode_id] = {
            "episode_id": ep.episode_id,

            # Preserve previous values if the current ones are empty
            "sheet_url": sheet_url or prev.get("sheet_url", ""),
            "username_col": ep.username_col,

            "questions": {qid: asdict(q) for qid, q in ep.questions.items()},
            "last_scored_rows": existing_rows,

            "last_export_url": st.session_state.get("loaded_export_url", "") or prev.get("last_export_url", ""),
            "last_gid_used": st.session_state.get("loaded_episode_gid", "") or prev.get("last_gid_used", ""),
            
            "season_picks": prev.get("season_picks", {}),
        }

        save_state(state)
        st.success(f"Saved episode config for {ep.episode_id}")

if run_score:
    apply_implied_outcomes(ep)

    scored_df, leaderboard_df = score_episode_df(df, ep, state.get("contestants", []))
    store_season_picks(state, ep, df)

    # ✅ Add this here (display-only polish)
    scored_df["total"] = scored_df["total"].round(2)
    leaderboard_df["total"] = leaderboard_df["total"].round(2)

    st.subheader(f"Episode Leaderboard: {ep.episode_id}")
    st.dataframe(leaderboard_df, use_container_width=True)

    st.subheader("Per-response breakdown (this episode)")
    st.dataframe(scored_df.sort_values("total", ascending=False), use_container_width=True)

    # Persist results for season leaderboard
    if ep.episode_id and ep.episode_id != "UNNAMED":
        state["episodes"].setdefault(ep.episode_id, {})
        state["episodes"][ep.episode_id].update({
            "episode_id": ep.episode_id,
            "sheet_url": sheet_url,  # <-- add
            "username_col": ep.username_col,
            "questions": {qid: asdict(q) for qid, q in ep.questions.items()},
            "last_scored_rows": scored_df.to_dict(orient="records"),
            "last_export_url": st.session_state.get("loaded_export_url", ""),  # <-- add (see below)
            "last_gid_used": st.session_state.get("loaded_episode_gid", ""),   # <-- add
            "season_picks": state["episodes"][ep.episode_id].get("season_picks", {}),
        })
        new_bonus = award_new_bonuses(state, state.get("contestants", []))
        if new_bonus:
            st.success(f"Awarded new bonuses to {len(new_bonus)} player(s).")

        save_state(state)
        write_scores_csv(state)


    # After save_state(state) and write_scores_csv(state)
    owner = "nickazcarate"
    repo = "nickazcarate.github.io"
    branch = "main"  # or gh-pages, whatever Pages uses
    token = st.secrets["GITHUB_TOKEN"]

    # Push season_state.json
    with open(STATE_PATH, "rb") as f:
        github_upsert_file(owner, repo, branch, STATE_PATH, f.read(), token,
                           commit_message=f"Update state for {ep.episode_id}")

    # Push scores.csv
    with open(SCORES_CSV_PATH, "rb") as f:
        github_upsert_file(owner, repo, branch, SCORES_CSV_PATH, f.read(), token,
                           commit_message=f"Update scores for {ep.episode_id}")

    st.success("Pushed updates to GitHub ✅ (Pages will update after rebuild)")


    st.download_button(
        "Download this episode breakdown CSV",
        data=scored_df.to_csv(index=False).encode("utf-8"),
        file_name=f"{ep.episode_id}_breakdown.csv",
        mime="text/csv",
    )

    st.download_button(
        "Download this episode leaderboard CSV",
        data=leaderboard_df.to_csv(index=False).encode("utf-8"),
        file_name=f"{ep.episode_id}_leaderboard.csv",
        mime="text/csv",
    )

st.divider()
st.subheader("Season Leaderboard (across saved episodes)")
st.dataframe(season_leaderboard(state), use_container_width=True)