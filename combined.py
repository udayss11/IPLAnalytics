import random
import pandas as pd
import streamlit as st
from sklearn.ensemble import RandomForestClassifier

st.set_page_config(page_title="IPL Analytics App", layout="wide")

# ============================
# PREMIUM UI CSS
# ============================
st.markdown("""
<style>
:root {
    --bg: #f6f8fc;
    --card: rgba(255,255,255,0.82);
    --card-strong: rgba(255,255,255,0.95);
    --text: #172033;
    --muted: #5b6780;
    --line: rgba(15, 23, 42, 0.08);
    --shadow: 0 10px 35px rgba(15, 23, 42, 0.10);
    --shadow-soft: 0 6px 18px rgba(15, 23, 42, 0.08);
    --accent: #4f46e5;
    --accent-2: #0ea5e9;
    --success: #059669;
    --danger: #dc2626;
    --warning: #d97706;
}

html, body, [data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at top left, rgba(79,70,229,0.08), transparent 30%),
        radial-gradient(circle at top right, rgba(14,165,233,0.08), transparent 28%),
        linear-gradient(180deg, #f8fbff 0%, #f4f7fb 100%);
    color: var(--text);
}

section.main > div {
    max-width: 1280px;
    padding-top: 1.1rem;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
    border-right: 1px solid rgba(255,255,255,0.06);
}
[data-testid="stSidebar"] * {
    color: #e5eefc !important;
}
[data-testid="stSidebar"] .stRadio label {
    font-size: 15px;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.06);
    padding: 10px 12px;
    border-radius: 12px;
    margin-bottom: 8px;
}

.hero-card {
    position: relative;
    overflow: hidden;
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 45%, #1d4ed8 100%);
    padding: 28px 30px;
    border-radius: 24px;
    color: white;
    box-shadow: 0 18px 45px rgba(29, 78, 216, 0.18);
    margin-bottom: 20px;
}
.hero-card::after {
    content: "";
    position: absolute;
    inset: auto -40px -40px auto;
    width: 180px;
    height: 180px;
    border-radius: 999px;
    background: rgba(255,255,255,0.08);
}
.hero-title {
    font-size: 42px;
    font-weight: 800;
    line-height: 1.1;
    margin: 0 0 8px 0;
}
.hero-subtitle {
    font-size: 16px;
    color: rgba(255,255,255,0.86);
    margin: 0;
    max-width: 800px;
}

.section-chip {
    display: inline-block;
    padding: 8px 14px;
    border-radius: 999px;
    background: rgba(79,70,229,0.10);
    color: #4338ca;
    font-weight: 700;
    font-size: 12px;
    letter-spacing: 0.02em;
    margin-bottom: 12px;
}

.section-title {
    background: linear-gradient(135deg, rgba(255,255,255,0.92), rgba(255,255,255,0.76));
    backdrop-filter: blur(8px);
    border: 1px solid var(--line);
    box-shadow: var(--shadow-soft);
    padding: 14px 18px;
    border-radius: 18px;
    color: var(--text);
    margin: 18px 0 14px 0;
    font-weight: 800;
    font-size: 20px;
}

.premium-card {
    background: linear-gradient(180deg, var(--card-strong), var(--card));
    backdrop-filter: blur(10px);
    border: 1px solid var(--line);
    box-shadow: var(--shadow-soft);
    border-radius: 22px;
    padding: 18px 18px;
    margin-bottom: 16px;
}

.metric-row {
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 14px;
    margin: 12px 0 18px 0;
}
.metric-tile {
    background: linear-gradient(180deg, rgba(255,255,255,0.95), rgba(255,255,255,0.82));
    border: 1px solid var(--line);
    border-radius: 20px;
    box-shadow: var(--shadow-soft);
    padding: 18px 16px;
}
.metric-label {
    color: var(--muted);
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 8px;
}
.metric-value {
    color: var(--text);
    font-size: 28px;
    line-height: 1;
    font-weight: 800;
}
.metric-sub {
    color: var(--muted);
    margin-top: 8px;
    font-size: 12px;
}

.player-card {
    background: linear-gradient(135deg, #071124 0%, #020617 100%);
    padding: 14px 18px;
    border-radius: 18px;
    margin-bottom: 10px;
    color: white;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 15px;
    box-shadow: 0 10px 20px rgba(2,6,23,0.18);
    border: 1px solid rgba(255,255,255,0.06);
}
.player-meta {
    font-size: 13px;
    opacity: 0.88;
}
.badge {
    padding: 7px 13px;
    border-radius: 999px;
    font-weight: 800;
    font-size: 11px;
    color: white;
    letter-spacing: 0.02em;
}
.badge-bat { background: #2563eb; }
.badge-ar  { background: #059669; }
.badge-bowl{ background: #dc2626; }
.badge-wk  { background: #f59e0b; }

.insight-box {
    background: linear-gradient(180deg, rgba(239,246,255,0.95), rgba(239,246,255,0.82));
    border-left: 5px solid #2563eb;
    border-radius: 16px;
    padding: 14px 16px;
    margin: 10px 0;
    box-shadow: var(--shadow-soft);
}
.strength-box {
    background: linear-gradient(180deg, rgba(236,253,245,0.95), rgba(236,253,245,0.82));
    border-left: 5px solid #059669;
    border-radius: 16px;
    padding: 14px 16px;
    margin: 10px 0;
    box-shadow: var(--shadow-soft);
}
.weakness-box {
    background: linear-gradient(180deg, rgba(254,242,242,0.95), rgba(254,242,242,0.82));
    border-left: 5px solid #dc2626;
    border-radius: 16px;
    padding: 14px 16px;
    margin: 10px 0;
    box-shadow: var(--shadow-soft);
}
.tip-box {
    background: linear-gradient(180deg, rgba(255,251,235,0.96), rgba(255,251,235,0.82));
    border-left: 5px solid #d97706;
    border-radius: 16px;
    padding: 14px 16px;
    margin: 10px 0;
    box-shadow: var(--shadow-soft);
}

.compare-bar-wrap {
    margin: 10px 0 14px 0;
}
.compare-label {
    font-size: 13px;
    font-weight: 700;
    color: var(--muted);
    margin-bottom: 6px;
}
.compare-bar {
    width: 100%;
    height: 14px;
    background: #e8edf7;
    border-radius: 999px;
    overflow: hidden;
    border: 1px solid rgba(15,23,42,0.06);
}
.compare-fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #4f46e5, #0ea5e9);
}

.stButton > button {
    border-radius: 14px;
    border: 1px solid rgba(79,70,229,0.20);
    background: linear-gradient(180deg, #ffffff, #f8fbff);
    color: #1f2a44;
    font-weight: 700;
    padding: 0.55rem 1rem;
    box-shadow: var(--shadow-soft);
}
.stButton > button:hover {
    border-color: rgba(79,70,229,0.45);
    transform: translateY(-1px);
}

div[data-testid="stMetric"] {
    background: linear-gradient(180deg, rgba(255,255,255,0.95), rgba(255,255,255,0.82));
    border: 1px solid var(--line);
    border-radius: 20px;
    padding: 14px 14px;
    box-shadow: var(--shadow-soft);
}

div[data-testid="stDataFrame"] {
    background: white;
    border-radius: 18px;
    overflow: hidden;
    border: 1px solid var(--line);
    box-shadow: var(--shadow-soft);
}

div[role="tablist"] {
    gap: 8px;
}
button[data-baseweb="tab"] {
    border-radius: 12px !important;
    background: rgba(255,255,255,0.8) !important;
    border: 1px solid var(--line) !important;
    box-shadow: var(--shadow-soft);
    padding: 10px 16px !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(180deg, #eef2ff, #e0e7ff) !important;
    color: #312e81 !important;
    font-weight: 800 !important;
}

@media (max-width: 1100px) {
    .metric-row {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}
</style>
""", unsafe_allow_html=True)
st.markdown("""
<style>
.feature-grid {
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 14px;
    margin: 10px 0 22px 0;
}
.feature-card {
    background: linear-gradient(180deg, rgba(255,255,255,0.96), rgba(255,255,255,0.82));
    border: 1px solid rgba(15,23,42,0.08);
    border-radius: 22px;
    padding: 18px 16px;
    box-shadow: 0 10px 24px rgba(15,23,42,0.08);
    transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
    animation: fadeUp 0.5s ease both;
}
.feature-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 16px 34px rgba(15,23,42,0.12);
    border-color: rgba(79,70,229,0.18);
}
.feature-icon {
    width: 46px;
    height: 46px;
    border-radius: 14px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #eef2ff, #e0f2fe);
    font-size: 22px;
    margin-bottom: 12px;
}
.feature-title {
    font-size: 16px;
    font-weight: 800;
    color: #172033;
    margin-bottom: 8px;
}
.feature-text {
    font-size: 13px;
    color: #5b6780;
    line-height: 1.5;
}

.quick-stats {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 14px;
    margin: 4px 0 22px 0;
}
.quick-stat {
    background: linear-gradient(180deg, rgba(255,255,255,0.95), rgba(255,255,255,0.84));
    border: 1px solid rgba(15,23,42,0.08);
    border-radius: 20px;
    padding: 16px;
    box-shadow: 0 8px 20px rgba(15,23,42,0.07);
    animation: fadeUp 0.6s ease both;
}
.quick-stat-label {
    font-size: 12px;
    color: #5b6780;
    font-weight: 700;
    margin-bottom: 6px;
}
.quick-stat-value {
    font-size: 26px;
    font-weight: 800;
    color: #172033;
}

.welcome-banner {
    background: linear-gradient(135deg, rgba(79,70,229,0.10), rgba(14,165,233,0.10));
    border: 1px solid rgba(79,70,229,0.10);
    border-radius: 20px;
    padding: 16px 18px;
    margin: 6px 0 20px 0;
    box-shadow: 0 8px 18px rgba(15,23,42,0.06);
    animation: fadeUp 0.45s ease both;
}
.welcome-title {
    font-size: 18px;
    font-weight: 800;
    color: #172033;
    margin-bottom: 6px;
}
.welcome-text {
    font-size: 14px;
    color: #5b6780;
    line-height: 1.6;
}

@keyframes fadeUp {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0px);
    }
}

@media (max-width: 1200px) {
    .feature-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
    .quick-stats {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}
</style>
""", unsafe_allow_html=True)

# ============================
# PREMIUM UI HELPERS
# ============================
def render_hero():
    st.markdown("""
    <div class="hero-card">
        <div class="section-chip">PORTFOLIO PROJECT · IPL ANALYTICS</div>
        <div class="hero-title">🏏 IPL Analytics App</div>
        <p class="hero-subtitle">
            Premium cricket analytics dashboard for squad evaluation, venue-aware team building,
            head-to-head analysis, and multi-factor match winner prediction.
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_metric_tiles(items):
    cols = st.columns(len(items))
    for col, (label, value, sub) in zip(cols, items):
        value = str(value) if value is not None else "-"
        sub = str(sub) if sub is not None else ""

        with col:
            st.metric(label=label, value=value)
            if sub:
                st.caption(sub)


def render_section_header(title, emoji=""):
    label = f"{emoji} {title}".strip()
    st.markdown(f'<div class="section-title">{label}</div>', unsafe_allow_html=True)


def render_compare_bar(label, value, max_value=100):
    pct = 0 if max_value == 0 else max(0, min(100, (value / max_value) * 100))
    st.markdown(f"""
    <div class="compare-bar-wrap">
        <div class="compare-label">{label}: {value}</div>
        <div class="compare-bar">
            <div class="compare-fill" style="width:{pct}%"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_text_box(kind, title, content):
    class_map = {
        "insight": "insight-box",
        "strength": "strength-box",
        "weakness": "weakness-box",
        "tip": "tip-box"
    }
    cls = class_map.get(kind, "insight-box")
    st.markdown(
        f'<div class="{cls}"><b>{title}</b><br>{content}</div>',
        unsafe_allow_html=True
    )
def render_feature_cards():
    st.markdown("""
    <div class="feature-grid">
        <div class="feature-card">
            <div class="feature-icon">📋</div>
            <div class="feature-title">Single Team Analysis</div>
            <div class="feature-text">Evaluate a chosen 12-player squad using professional, batting, bowling, and venue-adjusted ratings.</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🤝</div>
            <div class="feature-title">Head-to-Head Records</div>
            <div class="feature-text">Compare two teams using historical wins, matchup percentages, and match-by-match records.</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🧭</div>
            <div class="feature-title">Venue-Based Best XI</div>
            <div class="feature-text">Generate venue-aware best playing squads based on spin, pace, batting depth, and balance.</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🎯</div>
            <div class="feature-title">Match Prediction</div>
            <div class="feature-text">Predict winners using squad ratings, venue fit, toss, head-to-head, and context model factors.</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🏟️</div>
            <div class="feature-title">Venue Insights</div>
            <div class="feature-text">Explore pitch type, toss impact, batting-first trends, bowling-first trends, and venue tendencies.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_welcome_banner():
    st.markdown("""
    <div class="welcome-banner">
        <div class="welcome-title">Welcome to the IPL Analytics Dashboard</div>
        <div class="welcome-text">
            Use the left sidebar to switch between analysis modes. This app combines squad-building logic,
            venue-aware selection, historical records, and a hybrid prediction model in one premium dashboard.
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_quick_stats():
    total_teams = int(df["Team"].nunique())
    total_players = int(df["Name"].nunique())
    total_matches = int(len(matches_df))
    total_venues = int(venue_df["venue"].nunique())

    st.markdown(f"""
    <div class="quick-stats">
        <div class="quick-stat">
            <div class="quick-stat-label">Teams Covered</div>
            <div class="quick-stat-value">{total_teams}</div>
        </div>
        <div class="quick-stat">
            <div class="quick-stat-label">Venues Tracked</div>
            <div class="quick-stat-value">{total_venues}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
# ============================
# DATA LOAD
# ============================
@st.cache_data
def load_squad_data():
    squad = pd.read_csv("IPL2025.csv")
    squad.columns = [c.strip() for c in squad.columns]

    text_cols = ["Team", "Name", "Role", "Bowling Type", "Batting Position", "Nationality", "Priority"]
    for col in text_cols:
        if col in squad.columns:
            squad[col] = squad[col].astype(str).str.strip()

    priority_map = {
        "low": 1,
        "mid": 2,
        "medium": 2,
        "high": 3,
        "top": 4
    }

    squad["Priority_Score"] = (
        squad["Priority"]
        .astype(str)
        .str.lower()
        .map(priority_map)
        .fillna(0)
        .astype(int)
    )

    squad["Rating"] = pd.to_numeric(squad.get("Rating", 0), errors="coerce").fillna(0)
    return squad


@st.cache_data
def load_match_context_data():
    matches = pd.read_csv("ipl2026.csv", low_memory=False)
    matches.columns = [c.strip() for c in matches.columns]

    needed = ["team1", "team2", "city", "toss_winner", "toss_decision", "winner", "Eliminator", "method"]
    matches = matches[needed].copy()

    for col in needed:
        matches[col] = matches[col].astype(str).str.strip()

    matches = matches.replace("nan", "Unknown").fillna("Unknown")
    return matches


@st.cache_data
def load_venue_data():
    venue = pd.read_excel("IPL_Venue_Details_With_Stats.xlsx")
    venue.columns = [c.strip() for c in venue.columns]
    venue["venue"] = venue["venue"].astype(str).str.strip()
    venue["pitch_type"] = venue["pitch_type"].astype(str).str.strip().str.lower()
    venue["better_to"] = venue["better_to"].astype(str).str.strip().str.lower()
    return venue


df = load_squad_data()
matches_df = load_match_context_data()
venue_df = load_venue_data()

# ============================
# BASIC HELPERS
# ============================
def normalize_text(x):
    return str(x).strip().lower()


TEAM_NAME_MAP = {
    "csk": "Chennai Super Kings",
    "chennai super kings": "Chennai Super Kings",
    "dc": "Delhi Capitals",
    "delhi capitals": "Delhi Capitals",
    "gt": "Gujarat Titans",
    "gujarat titans": "Gujarat Titans",
    "kkr": "Kolkata Knight Riders",
    "kolkata knight riders": "Kolkata Knight Riders",
    "lsg": "Lucknow Supergiants",
    "lucknow supergiants": "Lucknow Supergiants",
    "lucknow super giants": "Lucknow Supergiants",
    "mi": "Mumbai Indians",
    "mumbai indians": "Mumbai Indians",
    "pbks": "Punjab Kings",
    "punjab kings": "Punjab Kings",
    "rr": "Rajasthan Royals",
    "rajasthan royals": "Rajasthan Royals",
    "rcb": "Royal Challengers Bangalore",
    "royal challengers bangalore": "Royal Challengers Bangalore",
    "srh": "Sunrisers Hyderabad",
    "sunrisers hyderabad": "Sunrisers Hyderabad",
}

def canonical_team_name(name):
    return TEAM_NAME_MAP.get(normalize_text(name), str(name).strip())


def bp_rank(x):
    x = normalize_text(x)
    if "opener" in x:
        return 0
    if "top" in x:
        return 1
    if "middle" in x and "lower" not in x:
        return 2
    if "lower middle" in x:
        return 3
    if "lower" in x:
        return 4
    return 99


def role_rank(x):
    x = normalize_text(x)
    if "wk" in x or "wicket" in x:
        return 1
    if "bat" in x:
        return 1
    if "round" in x:
        return 2
    if "bowler" in x:
        return 3
    return 9


def is_wicketkeeper(role):
    role = normalize_text(role)
    return ("wk" in role) or ("wicket" in role)


def is_all_rounder(role):
    return "round" in normalize_text(role)


def is_bowler(role):
    return "bowler" in normalize_text(role)


def is_batter(role):
    return ("bat" in normalize_text(role)) or is_wicketkeeper(role)


def is_overseas(nationality):
    return normalize_text(nationality) != "india"


def is_opener(bp):
    return "opener" in normalize_text(bp)


def is_top_order(bp):
    bp = normalize_text(bp)
    return ("opener" in bp) or ("top" in bp)


def is_middle_order(bp):
    bp = normalize_text(bp)
    return ("middle" in bp) and ("lower" not in bp)


def is_lower_middle(bp):
    return "lower middle" in normalize_text(bp)


def is_lower_order(bp):
    return "lower" in normalize_text(bp)


def is_spinner(bt):
    bt = normalize_text(bt)
    return any(k in bt for k in ["spin", "legbreak", "offbreak", "orthodox", "chinaman"])


def is_pacer(bt):
    bt = normalize_text(bt)
    return any(k in bt for k in ["fast", "medium", "pace", "seam"])


def role_badge(role):
    role = normalize_text(role)
    if is_wicketkeeper(role):
        return "WK", "badge-wk"
    if is_all_rounder(role):
        return "AR", "badge-ar"
    if is_batter(role):
        return "BAT", "badge-bat"
    return "BOWL", "badge-bowl"


def show_player_card(index_text, row):
    txt, cls = role_badge(row["Role"])
    st.markdown(
        f"""
        <div class="player-card">
            <div>
                <b>{index_text} {row['Name']}</b><br>
                <span class="player-meta">
                    {row['Role']} | {row['Batting Position']} | {row['Bowling Type']} | {row['Nationality']} | Rating: {row['Rating']}
                </span>
            </div>
            <div class="badge {cls}">{txt}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ============================
# VENUE HELPERS
# ============================
def get_venue_row(venue_df_local, venue):
    row = venue_df_local[
        venue_df_local["venue"].astype(str).str.lower() == str(venue).strip().lower()
    ]

    if row.empty:
        return pd.Series({
            "venue": str(venue).strip(),
            "pitch_type": "balanced",
            "toss_win_match_pct": 50,
            "bat_first_win_pct": 50,
            "bowl_first_win_pct": 50,
            "better_to": "balanced"
        })

    return row.iloc[0] 


def player_venue_fit_score(player, venue_row):
    if venue_row is None:
        return 0.0

    pitch_type = str(venue_row.get("pitch_type", "")).strip().lower()
    role = str(player.get("Role", ""))
    bt = str(player.get("Bowling Type", ""))
    bp = str(player.get("Batting Position", ""))

    score = 0.0

    if pitch_type == "spin":
        if is_spinner(bt):
            score += 2.0
        if is_all_rounder(role) and is_spinner(bt):
            score += 1.0
        if is_middle_order(bp):
            score += 0.4

    elif pitch_type == "pace":
        if is_pacer(bt):
            score += 2.0
        if is_all_rounder(role) and is_pacer(bt):
            score += 0.8
        if is_opener(bp) or is_top_order(bp):
            score += 0.4

    elif pitch_type == "batting":
        if is_batter(role):
            score += 1.2
        if is_opener(bp):
            score += 0.8
        if is_top_order(bp):
            score += 0.5
        if is_lower_middle(bp) or is_lower_order(bp):
            score += 0.5

    elif pitch_type == "slow":
        if is_spinner(bt):
            score += 1.6
        if is_all_rounder(role):
            score += 0.8
        if is_middle_order(bp):
            score += 0.3
        if is_lower_middle(bp):
            score += 0.4

    elif pitch_type == "balanced":
        if is_batter(role):
            score += 0.5
        if is_bowler(role):
            score += 0.5
        if is_all_rounder(role):
            score += 0.6
        if is_spinner(bt) or is_pacer(bt):
            score += 0.3

    return round(score, 2)


def venue_team_targets(venue_row):
    if venue_row is None:
        return {"min_spinners": 1, "min_pacers": 2, "min_batting_options": 6, "min_all_rounders": 1}

    pitch_type = str(venue_row.get("pitch_type", "")).strip().lower()

    if pitch_type == "spin":
        return {"min_spinners": 2, "min_pacers": 2, "min_batting_options": 6, "min_all_rounders": 1}
    if pitch_type == "pace":
        return {"min_spinners": 1, "min_pacers": 3, "min_batting_options": 6, "min_all_rounders": 1}
    if pitch_type == "batting":
        return {"min_spinners": 1, "min_pacers": 2, "min_batting_options": 7, "min_all_rounders": 1}
    if pitch_type == "slow":
        return {"min_spinners": 2, "min_pacers": 2, "min_batting_options": 6, "min_all_rounders": 2}
    return {"min_spinners": 1, "min_pacers": 2, "min_batting_options": 6, "min_all_rounders": 1}

# ============================
# TEAM BUILDING
# ============================
def prepare_team_df(team_source_df):
    temp_df = team_source_df.copy().reset_index(drop=True)
    temp_df["BP_Rank"] = temp_df["Batting Position"].apply(bp_rank)
    temp_df["Role_Rank"] = temp_df["Role"].apply(role_rank)
    return temp_df


def valid_for_slot(player, slot):
    bp = player["BP_Rank"]
    rr = player["Role_Rank"]

    if slot in [1, 2]:
        return bp == 0
    if slot == 3:
        return bp in [0, 1]
    if slot == 4:
        return bp in [1, 2]
    if slot in [5, 6, 7]:
        return bp == 2
    if slot == 8:
        return bp in [3, 4]
    if slot == 9:
        return bp in [3, 4] and rr in [2, 3]
    if slot in [10, 11]:
        return rr == 3
    return False


def repair_team(team):
    team = team.reset_index(drop=True).copy()
    for slot in range(1, 12):
        i = slot - 1
        if i >= len(team):
            continue
        if not valid_for_slot(team.iloc[i], slot):
            for j in range(len(team)):
                if i == j:
                    continue
                if valid_for_slot(team.iloc[j], slot) and valid_for_slot(team.iloc[i], j + 1):
                    temp = team.iloc[i].copy()
                    team.iloc[i] = team.iloc[j]
                    team.iloc[j] = temp
                    break
    return team.reset_index(drop=True)


def candidates(slot, taken_names, team_source_df, venue_row=None):
    c = team_source_df[~team_source_df["Name"].isin(taken_names)].copy()
    if c.empty:
        return c

    c["Venue_Fit"] = c.apply(lambda row: player_venue_fit_score(row, venue_row), axis=1)

    if slot in [10, 11]:
        out = c[c["Role"].apply(is_bowler)].sort_values(["Venue_Fit", "Priority_Score", "Rating"], ascending=[False, False, False])
        if not out.empty:
            return out

    if slot == 9:
        out = c[
            (c["Role"].apply(is_all_rounder) | c["Role"].apply(is_bowler)) &
            (c["Batting Position"].apply(is_lower_middle) | c["Batting Position"].apply(is_lower_order))
        ].sort_values(["Venue_Fit", "Priority_Score", "Rating"], ascending=[False, False, False])
        if not out.empty:
            return out

    if slot in [1, 2]:
        out = c[c["Batting Position"].apply(is_opener)].sort_values(["Venue_Fit", "Priority_Score", "Rating"], ascending=[False, False, False])
        if not out.empty:
            return out

    if slot == 3:
        out = c[c["Batting Position"].apply(lambda x: is_opener(x) or is_top_order(x))].sort_values(
            ["Venue_Fit", "Priority_Score", "Rating"], ascending=[False, False, False]
        )
        if not out.empty:
            return out

    if slot == 4:
        out = c[c["Batting Position"].apply(lambda x: is_top_order(x) or is_middle_order(x))].sort_values(
            ["Venue_Fit", "Priority_Score", "Rating"], ascending=[False, False, False]
        )
        if not out.empty:
            return out

    if slot in [5, 6, 7]:
        out = c[c["Batting Position"].apply(is_middle_order)].sort_values(
            ["Venue_Fit", "Priority_Score", "Rating"], ascending=[False, False, False]
        )
        if not out.empty:
            return out

    if slot == 8:
        out = c[c["Batting Position"].apply(lambda x: is_lower_middle(x) or is_lower_order(x))].sort_values(
            ["Venue_Fit", "Priority_Score", "Rating"], ascending=[False, False, False]
        )
        if not out.empty:
            return out

    return c.sort_values(["Venue_Fit", "Priority_Score", "Rating"], ascending=[False, False, False])


def create_team(team_source_df, venue_row=None):
    team_source_df = prepare_team_df(team_source_df)
    team_source_df["Venue_Fit"] = team_source_df.apply(lambda row: player_venue_fit_score(row, venue_row), axis=1)

    taken = set()
    slots = {}
    targets = venue_team_targets(venue_row)

    top_players = team_source_df.sort_values(
        ["Priority_Score", "Venue_Fit", "Rating", "BP_Rank"],
        ascending=[False, False, False, True]
    )

    for _, player in top_players.iterrows():
        if player["Priority_Score"] < 4:
            continue
        for slot in range(1, 12):
            if slot not in slots and valid_for_slot(player, slot):
                slots[slot] = player
                taken.add(player["Name"])
                break

    wk_pool = team_source_df[
        (~team_source_df["Name"].isin(taken)) &
        (team_source_df["Role"].apply(is_wicketkeeper))
    ].sort_values(["Venue_Fit", "Priority_Score", "Rating"], ascending=[False, False, False])

    if not wk_pool.empty:
        for slot in [4, 5, 6]:
            if slot not in slots and valid_for_slot(wk_pool.iloc[0], slot):
                slots[slot] = wk_pool.iloc[0]
                taken.add(wk_pool.iloc[0]["Name"])
                break

    for slot in range(1, 12):
        if slot in slots:
            continue
        cands = candidates(slot, taken, team_source_df, venue_row)
        if cands.empty:
            continue
        top_n = min(4, len(cands))
        pick = cands.head(top_n).sample(1, random_state=random.randint(1, 999999)).iloc[0]
        slots[slot] = pick
        taken.add(pick["Name"])

    if len(slots) < 11:
        leftovers = team_source_df[~team_source_df["Name"].isin(taken)].sort_values(
            ["Venue_Fit", "Priority_Score", "Rating"], ascending=[False, False, False]
        )
        for _, player in leftovers.iterrows():
            next_slot = next((s for s in range(1, 12) if s not in slots), None)
            if next_slot is None:
                break
            slots[next_slot] = player
            taken.add(player["Name"])

    team = pd.DataFrame([slots[s] for s in sorted(slots.keys())]).drop_duplicates(subset=["Name"]).reset_index(drop=True)

    if len(team) > 11:
        team = team.head(11)

    overseas_count = int(team["Nationality"].apply(is_overseas).sum())
    if overseas_count > 4:
        extra = overseas_count - 4
        remove_pool = team[team["Nationality"].apply(is_overseas)].sort_values(
            ["Venue_Fit", "Priority_Score", "Rating"], ascending=[True, True, True]
        )
        add_pool = team_source_df[
            (~team_source_df["Name"].isin(team["Name"])) &
            (~team_source_df["Nationality"].apply(is_overseas))
        ].sort_values(["Venue_Fit", "Priority_Score", "Rating"], ascending=[False, False, False])

        rem_players = remove_pool.head(extra)
        add_players = add_pool.head(len(rem_players))
        if len(rem_players) > 0 and len(add_players) > 0:
            team = team[~team["Name"].isin(rem_players["Name"])]
            team = pd.concat([team, add_players], ignore_index=True)

    current_spinners = int(team["Bowling Type"].apply(is_spinner).sum())
    current_pacers = int(team["Bowling Type"].apply(is_pacer).sum())
    current_ar = int(team["Role"].apply(is_all_rounder).sum())
    current_bat_depth = int(team.apply(lambda row: is_batter(row["Role"]) or is_all_rounder(row["Role"]), axis=1).sum())

    if current_spinners < targets["min_spinners"]:
        needed = targets["min_spinners"] - current_spinners
        spin_pool = team_source_df[
            (~team_source_df["Name"].isin(team["Name"])) &
            (team_source_df["Bowling Type"].apply(is_spinner))
        ].sort_values(["Venue_Fit", "Priority_Score", "Rating"], ascending=[False, False, False])
        remove_pool = team[~team["Bowling Type"].apply(is_spinner)].sort_values(
            ["Venue_Fit", "Priority_Score", "Rating"], ascending=[True, True, True]
        )
        add_players = spin_pool.head(needed)
        rem_players = remove_pool.head(len(add_players))
        if len(add_players) > 0 and len(rem_players) > 0:
            team = team[~team["Name"].isin(rem_players["Name"])]
            team = pd.concat([team, add_players], ignore_index=True)

    current_pacers = int(team["Bowling Type"].apply(is_pacer).sum())
    if current_pacers < targets["min_pacers"]:
        needed = targets["min_pacers"] - current_pacers
        pace_pool = team_source_df[
            (~team_source_df["Name"].isin(team["Name"])) &
            (team_source_df["Bowling Type"].apply(is_pacer))
        ].sort_values(["Venue_Fit", "Priority_Score", "Rating"], ascending=[False, False, False])
        remove_pool = team[~team["Bowling Type"].apply(is_pacer)].sort_values(
            ["Venue_Fit", "Priority_Score", "Rating"], ascending=[True, True, True]
        )
        add_players = pace_pool.head(needed)
        rem_players = remove_pool.head(len(add_players))
        if len(add_players) > 0 and len(rem_players) > 0:
            team = team[~team["Name"].isin(rem_players["Name"])]
            team = pd.concat([team, add_players], ignore_index=True)

    current_ar = int(team["Role"].apply(is_all_rounder).sum())
    if current_ar < targets["min_all_rounders"]:
        needed = targets["min_all_rounders"] - current_ar
        ar_pool = team_source_df[
            (~team_source_df["Name"].isin(team["Name"])) &
            (team_source_df["Role"].apply(is_all_rounder))
        ].sort_values(["Venue_Fit", "Priority_Score", "Rating"], ascending=[False, False, False])
        remove_pool = team[~team["Role"].apply(is_all_rounder)].sort_values(
            ["Venue_Fit", "Priority_Score", "Rating"], ascending=[True, True, True]
        )
        add_players = ar_pool.head(needed)
        rem_players = remove_pool.head(len(add_players))
        if len(add_players) > 0 and len(rem_players) > 0:
            team = team[~team["Name"].isin(rem_players["Name"])]
            team = pd.concat([team, add_players], ignore_index=True)

    current_bat_depth = int(team.apply(lambda row: is_batter(row["Role"]) or is_all_rounder(row["Role"]), axis=1).sum())
    if current_bat_depth < targets["min_batting_options"]:
        needed = targets["min_batting_options"] - current_bat_depth
        bat_pool = team_source_df[
            (~team_source_df["Name"].isin(team["Name"])) &
            (team_source_df.apply(lambda row: is_batter(row["Role"]) or is_all_rounder(row["Role"]), axis=1))
        ].sort_values(["Venue_Fit", "Priority_Score", "Rating"], ascending=[False, False, False])
        remove_pool = team[~team.apply(lambda row: is_batter(row["Role"]) or is_all_rounder(row["Role"]), axis=1)].sort_values(
            ["Venue_Fit", "Priority_Score", "Rating"], ascending=[True, True, True]
        )
        add_players = bat_pool.head(needed)
        rem_players = remove_pool.head(len(add_players))
        if len(add_players) > 0 and len(rem_players) > 0:
            team = team[~team["Name"].isin(rem_players["Name"])]
            team = pd.concat([team, add_players], ignore_index=True)

    team = team.drop_duplicates(subset=["Name"]).head(11).reset_index(drop=True)
    team = prepare_team_df(team)
    team = repair_team(team)

    if len(team) < 11:
        fill_pool = team_source_df[~team_source_df["Name"].isin(team["Name"])].sort_values(
            ["Venue_Fit", "Priority_Score", "Rating"], ascending=[False, False, False]
        )
        needed = 11 - len(team)
        team = pd.concat([team, fill_pool.head(needed)], ignore_index=True).head(11)

    return team.reset_index(drop=True)


def impact_players(team, team_source_df):
    pool = team_source_df[~team_source_df["Name"].isin(team["Name"])].sort_values(["Priority_Score", "Rating"], ascending=[False, False])
    impact_list = []

    batter_cover = pool[pool["Role"].apply(is_batter)]
    if not batter_cover.empty:
        impact_list.append(batter_cover.iloc[0])

    bowling_cover = pool[pool["Role"].apply(lambda x: is_bowler(x) or is_all_rounder(x))]
    if not bowling_cover.empty and bowling_cover.iloc[0]["Name"] not in [p["Name"] for p in impact_list]:
        impact_list.append(bowling_cover.iloc[0])

    for _, p in pool.iterrows():
        if len(impact_list) >= 5:
            break
        if p["Name"] not in [x["Name"] for x in impact_list]:
            impact_list.append(p)

    impact_df = pd.DataFrame(impact_list[:5])
    if not impact_df.empty:
        impact_df = prepare_team_df(impact_df)
    return impact_df

#=============================
def choose_projected_impact_player(team, impact_df, innings_mode="bat_first"):
    """
    innings_mode:
        - 'bat_first'  -> team starts with stronger batting XI, impact should preferably strengthen bowling
        - 'bowl_first' -> team starts with stronger bowling XI, impact should preferably strengthen batting
    """
    if impact_df is None or impact_df.empty:
        return None

    impact_df = impact_df.copy().reset_index(drop=True)

    if innings_mode == "bat_first":
        # prefer bowlers / bowling all-rounders
        bowl_pool = impact_df[
            impact_df.apply(lambda row: is_bowler(row["Role"]) or is_all_rounder(row["Role"]), axis=1)
        ].copy()

        if not bowl_pool.empty:
            bowl_pool["Impact_Score"] = bowl_pool.apply(
                lambda row: row["Rating"] + (1.0 if is_bowler(row["Role"]) else 0.6) + (0.4 if is_pacer(row["Bowling Type"]) or is_spinner(row["Bowling Type"]) else 0),
                axis=1
            )
            return bowl_pool.sort_values("Impact_Score", ascending=False).iloc[0]

    elif innings_mode == "bowl_first":
        # prefer batters / wk / batting all-rounders / opener cover
        bat_pool = impact_df[
            impact_df.apply(lambda row: is_batter(row["Role"]) or is_all_rounder(row["Role"]), axis=1)
        ].copy()

        if not bat_pool.empty:
            bat_pool["Impact_Score"] = bat_pool.apply(
                lambda row: row["Rating"]
                + (1.0 if is_batter(row["Role"]) else 0.6)
                + (0.6 if is_opener(row["Batting Position"]) else 0.3 if is_top_order(row["Batting Position"]) else 0),
                axis=1
            )
            return bat_pool.sort_values("Impact_Score", ascending=False).iloc[0]

    # fallback: best rated player
    return impact_df.sort_values("Rating", ascending=False).iloc[0]
def suggest_best_impact_options(team, impact_df, innings_mode="bat_first", top_n=2):
    if impact_df is None or impact_df.empty:
        return pd.DataFrame()

    impact_df = impact_df.copy().reset_index(drop=True)

    if innings_mode == "bat_first":
        impact_df["Suggestion_Score"] = impact_df.apply(
            lambda row: row["Rating"]
            + (1.2 if is_bowler(row["Role"]) else 0.8 if is_all_rounder(row["Role"]) else 0)
            + (0.5 if is_spinner(row["Bowling Type"]) or is_pacer(row["Bowling Type"]) else 0),
            axis=1
        )
    else:
        impact_df["Suggestion_Score"] = impact_df.apply(
            lambda row: row["Rating"]
            + (1.2 if is_batter(row["Role"]) else 0.8 if is_all_rounder(row["Role"]) else 0)
            + (0.6 if is_opener(row["Batting Position"]) else 0.3 if is_top_order(row["Batting Position"]) else 0),
            axis=1
        )

    return impact_df.sort_values(["Suggestion_Score", "Rating"], ascending=[False, False]).head(top_n).reset_index(drop=True)
def build_effective_team_with_impact(team, impact_df, innings_mode="bat_first"):
    if team is None or team.empty:
        return pd.DataFrame(), None, None

    team = team.copy().reset_index(drop=True)

    projected_impact = choose_projected_impact_player(team, impact_df, innings_mode)
    if projected_impact is None:
        return team.copy(), None, None

    if innings_mode == "bat_first":
        removable = team[
            team.apply(lambda row: is_batter(row["Role"]) or is_wicketkeeper(row["Role"]) or is_all_rounder(row["Role"]), axis=1)
        ].copy()

        openers_count = int(team["Batting Position"].apply(is_opener).sum())
        if openers_count <= 2:
            removable = removable[~removable["Batting Position"].apply(is_opener)]

        if removable.empty:
            removable = team.copy()

    else:
        removable = team[
            team.apply(lambda row: is_bowler(row["Role"]) or is_all_rounder(row["Role"]), axis=1)
        ].copy()

        pacers_count = int(team["Bowling Type"].apply(is_pacer).sum())
        spinners_count = int(team["Bowling Type"].apply(is_spinner).sum())

        temp = removable.copy()
        if pacers_count <= 2:
            temp = temp[~temp["Bowling Type"].apply(is_pacer)]
        if spinners_count <= 1:
            temp = temp[~temp["Bowling Type"].apply(is_spinner)]

        if not temp.empty:
            removable = temp

        if removable.empty:
            removable = team.copy()

    removable = removable.sort_values(["Priority_Score", "Rating"], ascending=[True, True])
    replaced_player = removable.iloc[0].copy()

    effective_team = team[team["Name"] != replaced_player["Name"]].copy().reset_index(drop=True)

    projected_impact_df = pd.DataFrame([projected_impact]).copy()
    effective_team = pd.concat([effective_team, projected_impact_df], ignore_index=True)

    # keep only expected columns if present
    expected_cols = team.columns.tolist()
    effective_team = effective_team.reindex(columns=expected_cols)

    effective_team = effective_team.drop_duplicates(subset=["Name"]).reset_index(drop=True)

    # ensure required columns exist
    required_cols = ["Name", "Role", "Batting Position", "Bowling Type", "Nationality", "Rating", "Priority_Score"]
    for col in required_cols:
        if col not in effective_team.columns:
            effective_team[col] = "" if col in ["Name", "Role", "Batting Position", "Bowling Type", "Nationality"] else 0

    effective_team["Rating"] = pd.to_numeric(effective_team["Rating"], errors="coerce").fillna(0)
    effective_team["Priority_Score"] = pd.to_numeric(effective_team["Priority_Score"], errors="coerce").fillna(0)

    effective_team = prepare_team_df(effective_team)
    effective_team = repair_team(effective_team)

    if len(effective_team) > 11:
        effective_team = effective_team.head(11).reset_index(drop=True)

    return effective_team, projected_impact, replaced_player
# ============================
# RATING LOGIC
# ============================
def team_metrics(team, impact):
    metrics = {}

    if team is None or not isinstance(team, pd.DataFrame) or team.empty:
        raise ValueError("team_metrics received an empty or invalid team DataFrame")

    required_cols = ["Batting Position", "Role", "Bowling Type", "Nationality", "Rating", "Priority_Score", "Name"]
    missing_cols = [col for col in required_cols if col not in team.columns]
    if missing_cols:
        raise ValueError(f"team_metrics missing required columns: {missing_cols}")

    combined = pd.concat([team, impact], ignore_index=True) if impact is not None and not impact.empty else team.copy()
    combined = combined.drop_duplicates(subset=["Name"]).reset_index(drop=True)

    metrics["openers"] = int(team["Batting Position"].apply(is_opener).sum())
    metrics["top_order"] = int(team["Batting Position"].apply(is_top_order).sum())
    metrics["middle_order"] = int(team["Batting Position"].apply(is_middle_order).sum())
    metrics["lower_middle"] = int(team["Batting Position"].apply(is_lower_middle).sum())
    metrics["lower_order"] = int(team["Batting Position"].apply(is_lower_order).sum())

    metrics["wicketkeepers"] = int(team["Role"].apply(is_wicketkeeper).sum())
    metrics["batters"] = int(team["Role"].apply(is_batter).sum())
    metrics["all_rounders"] = int(team["Role"].apply(is_all_rounder).sum())
    metrics["bowlers"] = int(team["Role"].apply(is_bowler).sum())

    metrics["spinners"] = int(team["Bowling Type"].apply(is_spinner).sum())
    metrics["pacers"] = int(team["Bowling Type"].apply(is_pacer).sum())
    metrics["overseas"] = int(team["Nationality"].apply(is_overseas).sum())

    metrics["high_priority"] = int((team["Priority_Score"] >= 3).sum())
    metrics["top_priority"] = int((team["Priority_Score"] == 4).sum())
    metrics["low_priority"] = int((team["Priority_Score"] <= 1).sum())

    metrics["bowling_options"] = int(team.apply(lambda row: is_bowler(row["Role"]) or is_all_rounder(row["Role"]), axis=1).sum())
    metrics["batting_options"] = int(team.apply(lambda row: is_batter(row["Role"]) or is_all_rounder(row["Role"]), axis=1).sum())

    middle_finishers = team.iloc[5:8] if len(team) >= 8 else team
    metrics["finishers"] = int(
        middle_finishers.apply(
            lambda row: is_all_rounder(row["Role"]) or is_lower_middle(row["Batting Position"]) or is_lower_order(row["Batting Position"]),
            axis=1
        ).sum()
    )

    tail = team.iloc[7:11] if len(team) >= 11 else team.tail(4)
    metrics["tail_all_rounders"] = int(tail["Role"].apply(is_all_rounder).sum())
    metrics["tail_rating_avg"] = float(tail["Rating"].mean()) if not tail.empty else 0.0

    metrics["combined_rating_avg"] = float(combined["Rating"].mean()) if not combined.empty else 0.0
    metrics["combined_priority_avg"] = float(combined["Priority_Score"].mean()) if not combined.empty else 0.0

    metrics["team_rating_sum"] = float(team["Rating"].sum())
    metrics["team_rating_avg"] = float(team["Rating"].mean())

    top3_sum = float(team["Rating"].sort_values(ascending=False).head(3).sum())
    metrics["top3_share"] = top3_sum / metrics["team_rating_sum"] if metrics["team_rating_sum"] > 0 else 1.0

    bottom3_avg = float(team["Rating"].sort_values().head(3).mean())
    metrics["bottom3_avg"] = bottom3_avg if not pd.isna(bottom3_avg) else 0.0

    if impact is not None and not impact.empty:
        metrics["impact_high_priority"] = int((impact["Priority_Score"] >= 3).sum())
        metrics["impact_bat_cover"] = int(impact["Role"].apply(is_batter).sum())
        metrics["impact_bowl_cover"] = int(impact.apply(lambda row: is_bowler(row["Role"]) or is_all_rounder(row["Role"]), axis=1).sum())
    else:
        metrics["impact_high_priority"] = 0
        metrics["impact_bat_cover"] = 0
        metrics["impact_bowl_cover"] = 0

    return metrics


def batting_rating(team, impact=None):
    combined = pd.concat([team, impact], ignore_index=True) if impact is not None and not impact.empty else team.copy()
    combined = combined.drop_duplicates(subset=["Name"]).reset_index(drop=True)

    openers = int(team["Batting Position"].apply(is_opener).sum())
    top_order = int(team["Batting Position"].apply(is_top_order).sum())
    middle_order = int(team["Batting Position"].apply(is_middle_order).sum())
    finishers = int(
        team.iloc[5:8].apply(
            lambda row: is_all_rounder(row["Role"]) or is_lower_middle(row["Batting Position"]) or is_lower_order(row["Batting Position"]),
            axis=1
        ).sum()
    ) if len(team) >= 8 else 0

    wicketkeepers = int(team["Role"].apply(is_wicketkeeper).sum())
    batting_options = int(team.apply(lambda row: is_batter(row["Role"]) or is_all_rounder(row["Role"]), axis=1).sum())
    avg12 = float(combined["Rating"].mean()) if not combined.empty else 0.0

    base = avg12 * 0.55 + openers * 0.60 + top_order * 0.30 + middle_order * 0.35 + finishers * 0.45 + wicketkeepers * 0.25 + batting_options * 0.20

    penalty = 0.0
    if openers < 2:
        penalty += 1.5
    if top_order < 3:
        penalty += 1.0
    if middle_order < 3:
        penalty += 1.0
    if finishers < 1:
        penalty += 1.25
    if wicketkeepers < 1:
        penalty += 1.5
    if batting_options < 6:
        penalty += 1.25

    score = base - penalty
    return round(max(1.0, min(10.0, score / 1.5)), 2)


def bowling_rating(team, impact=None):
    combined = pd.concat([team, impact], ignore_index=True) if impact is not None and not impact.empty else team.copy()
    combined = combined.drop_duplicates(subset=["Name"]).reset_index(drop=True)

    bowlers = int(team["Role"].apply(is_bowler).sum())
    all_rounders = int(team["Role"].apply(is_all_rounder).sum())
    spinners = int(team["Bowling Type"].apply(is_spinner).sum())
    pacers = int(team["Bowling Type"].apply(is_pacer).sum())
    bowling_options = int(team.apply(lambda row: is_bowler(row["Role"]) or is_all_rounder(row["Role"]), axis=1).sum())

    tail = team.iloc[7:11] if len(team) >= 11 else team.tail(4)
    tail_support = int(tail["Role"].apply(lambda x: is_bowler(x) or is_all_rounder(x)).sum())
    avg12 = float(combined["Rating"].mean()) if not combined.empty else 0.0

    base = avg12 * 0.50 + bowlers * 0.55 + all_rounders * 0.30 + spinners * 0.45 + pacers * 0.45 + bowling_options * 0.30 + tail_support * 0.20

    penalty = 0.0
    if bowlers < 3:
        penalty += 1.5
    if spinners < 1:
        penalty += 1.25
    if pacers < 2:
        penalty += 1.25
    if bowling_options < 5:
        penalty += 1.75
    if tail_support < 3:
        penalty += 0.75

    score = base - penalty
    return round(max(1.0, min(10.0, score / 1.45)), 2)


def stricter_professional_rating(team, impact, return_breakdown=False):
    m = team_metrics(team, impact)

    base_score = round(m["combined_rating_avg"], 2)
    bat_score = batting_rating(team, impact)
    bowl_score = bowling_rating(team, impact)

    support_score = min(2.0, (
        m["all_rounders"] * 0.30 +
        m["high_priority"] * 0.18 +
        m["impact_high_priority"] * 0.12 +
        m["combined_priority_avg"] * 0.22
    ))

    balance_score_val = min(2.0, (
        m["batting_options"] * 0.12 +
        m["bowling_options"] * 0.14 +
        (1 if m["wicketkeepers"] >= 1 else 0) * 0.35 +
        (1 if m["overseas"] <= 4 else 0) * 0.25
    ))

    raw_score = (
        base_score * 0.40 +
        bat_score * 0.22 +
        bowl_score * 0.22 +
        support_score * 0.08 +
        balance_score_val * 0.08
    )

    penalty = 0.0
    reasons = []
    analysis_flags = []

    if m["openers"] < 2:
        penalty += 1.2
        reasons.append("Less than 2 openers")
    if m["wicketkeepers"] < 1:
        penalty += 1.8
        reasons.append("No wicketkeeper")
    if m["all_rounders"] < 1:
        penalty += 1.2
        reasons.append("No all-rounder")
    if m["bowlers"] < 3:
        penalty += 1.4
        reasons.append("Less than 3 specialist bowlers")
    if m["spinners"] < 1:
        penalty += 1.2
        reasons.append("No spinner")
    if m["pacers"] < 2:
        penalty += 1.2
        reasons.append("Less than 2 pacers")
    if m["overseas"] > 4:
        penalty += 3.0
        reasons.append("More than 4 overseas players")
    if m["bowling_options"] < 5:
        penalty += 1.8
        reasons.append("Less than 5 bowling options")
    if m["batting_options"] < 6:
        penalty += 1.2
        reasons.append("Less than 6 batting options")
    if m["high_priority"] < 3:
        penalty += 1.2
        reasons.append("Less than 3 high/top priority players")
    if m["low_priority"] > 2:
        penalty += (m["low_priority"] - 2) * 0.7
        reasons.append("Too many low priority players")
    if m["finishers"] < 1:
        penalty += 1.2
        reasons.append("No finisher presence in slots 6-8")
    if m["top3_share"] > 0.45:
        penalty += 0.6
        reasons.append("Too dependent on top 3 players")
    if m["bottom3_avg"] < 5.5:
        penalty += 0.8
        reasons.append("Bottom 3 too weak")

    if m["tail_all_rounders"] < 1:
        analysis_flags.append("Tail lacks all-rounder support")
    if m["tail_rating_avg"] < 6:
        analysis_flags.append("Weak tail average rating")
    if m["impact_high_priority"] < 2:
        analysis_flags.append("Weak impact bench quality")
    if m["impact_bat_cover"] < 1:
        analysis_flags.append("Impact bench lacks batting cover")
    if m["impact_bowl_cover"] < 1:
        analysis_flags.append("Impact bench lacks bowling cover")

    bonus = 0.0
    if m["openers"] >= 2 and m["wicketkeepers"] >= 1 and m["all_rounders"] >= 2:
        bonus += 0.4
    if m["spinners"] >= 1 and m["pacers"] >= 2 and m["bowling_options"] >= 5:
        bonus += 0.4
    if m["high_priority"] >= 4 and m["low_priority"] <= 1:
        bonus += 0.4
    if m["combined_rating_avg"] >= 7.5:
        bonus += 0.3
    if m["finishers"] >= 2:
        bonus += 0.2

    final_score = round(max(1.0, min(10.0, raw_score - penalty + bonus)), 2)

    if return_breakdown:
        return final_score, {
            "Base Score": round(base_score, 2),
            "Batting Rating": bat_score,
            "Bowling Rating": bowl_score,
            "Support Score": round(support_score, 2),
            "Balance Score": round(balance_score_val, 2),
            "Raw Score": round(raw_score, 2),
            "Penalty": round(penalty, 2),
            "Bonus": round(bonus, 2),
            "Final Score": final_score,
            "Reasons": reasons,
            "Analysis Flags": analysis_flags,
            "Metrics": m
        }

    return final_score


def bench_strength(impact):
    if impact is None or impact.empty:
        return 0.0
    bench_avg = float(impact["Rating"].mean()) if "Rating" in impact.columns else 0.0
    bench_priority = float(impact["Priority_Score"].mean()) if "Priority_Score" in impact.columns else 0.0
    score = (bench_avg * 0.7) + (bench_priority * 0.8)
    return round(min(10.0, score / 1.2), 2)


def balance_score(team, impact):
    m = team_metrics(team, impact)
    score = 0.0
    if m["openers"] >= 2:
        score += 1.5
    if m["wicketkeepers"] >= 1:
        score += 1.0
    if m["all_rounders"] >= 1:
        score += 1.2
    if m["bowlers"] >= 3:
        score += 1.2
    if m["spinners"] >= 1:
        score += 1.0
    if m["pacers"] >= 2:
        score += 1.0
    if m["bowling_options"] >= 5:
        score += 1.3
    if m["batting_options"] >= 6:
        score += 1.0
    if m["overseas"] <= 4:
        score += 0.8
    return round(min(10.0, score), 2)


def match_strength(team, impact, innings_mode="bat_first"):
    effective_team, projected_impact, replaced_player = build_effective_team_with_impact(team, impact, innings_mode)

    overall, breakdown = stricter_professional_rating(effective_team, impact, return_breakdown=True)
    bat = batting_rating(effective_team, impact)
    bowl = bowling_rating(effective_team, impact)
    bench = bench_strength(impact)
    balance = balance_score(effective_team, impact)

    strength = overall * 0.40 + bat * 0.20 + bowl * 0.20 + bench * 0.10 + balance * 0.10

    return {
        "overall": overall,
        "batting": bat,
        "bowling": bowl,
        "bench": bench,
        "balance": balance,
        "strength": round(strength, 2),
        "breakdown": breakdown,
        "effective_team": effective_team,
        "projected_impact": projected_impact,
        "replaced_player": replaced_player,
        "innings_mode": innings_mode
    }


def ground_fit_rating(team, impact, venue_row):
    if venue_row is None:
        return 5.0

    pitch_type = str(venue_row.get("pitch_type", "")).strip().lower()

    spin_count = int(team["Bowling Type"].apply(is_spinner).sum())
    pace_count = int(team["Bowling Type"].apply(is_pacer).sum())
    all_rounders = int(team["Role"].apply(is_all_rounder).sum())
    batting_depth = int(team.apply(lambda row: is_batter(row["Role"]) or is_all_rounder(row["Role"]), axis=1).sum())
    openers = int(team["Batting Position"].apply(is_opener).sum())
    finishers = int(
        team.iloc[5:8].apply(
            lambda row: is_all_rounder(row["Role"]) or is_lower_middle(row["Batting Position"]) or is_lower_order(row["Batting Position"]),
            axis=1
        ).sum()
    ) if len(team) >= 8 else 0

    score = 5.0

    if pitch_type == "spin":
        score += spin_count * 0.9
        score += all_rounders * 0.35
        if spin_count < 2:
            score -= 1.0

    elif pitch_type == "pace":
        score += pace_count * 0.9
        score += openers * 0.3
        if pace_count < 2:
            score -= 1.0

    elif pitch_type == "batting":
        score += batting_depth * 0.45
        score += openers * 0.5
        score += finishers * 0.4

    elif pitch_type == "slow":
        score += spin_count * 0.7
        score += all_rounders * 0.5
        score += finishers * 0.3
        if spin_count < 2:
            score -= 0.8

    elif pitch_type == "balanced":
        score += batting_depth * 0.25
        score += pace_count * 0.25
        score += spin_count * 0.25
        score += all_rounders * 0.2

    return round(max(1.0, min(10.0, score / 1.2)), 2)


def venue_adjusted_team_rating(team, impact, venue_row):
    overall, breakdown = stricter_professional_rating(team, impact, return_breakdown=True)
    bat = batting_rating(team, impact)
    bowl = bowling_rating(team, impact)
    fit = ground_fit_rating(team, impact, venue_row)

    final = (
        overall * 0.50 +
        bat * 0.15 +
        bowl * 0.15 +
        fit * 0.20
    )

    final = round(min(10.0, max(1.0, final)), 2)

    return final, {
        "Overall Rating": overall,
        "Batting Rating": bat,
        "Bowling Rating": bowl,
        "Ground Fit Rating": fit,
        "Venue Adjusted Rating": final,
        "Breakdown": breakdown
    }

# ============================
# LLM STYLE EXPLAINER
# ============================
def llm_style_squad_explainer(
    team_name,
    venue_name,
    venue_row,
    xi,
    impact,
    professional_rating,
    breakdown,
    venue_adjusted_break
):
    metrics = breakdown["Metrics"]

    pitch_type = str(venue_row.get("pitch_type", "unknown")).title() if venue_row is not None else "Unknown"
    better_to = str(venue_row.get("better_to", "unknown")).replace("_", " ").title() if venue_row is not None else "Unknown"

    batting_rating_val = breakdown["Batting Rating"]
    bowling_rating_val = breakdown["Bowling Rating"]
    ground_fit = venue_adjusted_break["Ground Fit Rating"]
    venue_adjusted = venue_adjusted_break["Venue Adjusted Rating"]

    strengths = []
    weaknesses = []
    suggestions = []
    venue_points = []

    if metrics["openers"] >= 2:
        strengths.append("The squad has a proper opening combination, which gives it a stable start at the top.")
    if metrics["batting_options"] >= 6:
        strengths.append("The batting depth is strong, with enough options to absorb collapses and finish innings well.")
    if metrics["finishers"] >= 1:
        strengths.append("There is at least one finisher in the middle-to-lower order, which improves end-over scoring potential.")
    if metrics["spinners"] >= 2:
        strengths.append("The side has a strong spin unit, which is especially valuable on slower surfaces.")
    if metrics["pacers"] >= 2:
        strengths.append("The pace attack has enough depth to cover powerplay and death overs effectively.")
    if metrics["all_rounders"] >= 2:
        strengths.append("Multiple all-rounders improve squad balance and provide tactical flexibility.")
    if metrics["wicketkeepers"] >= 1:
        strengths.append("The presence of a wicketkeeper-batter adds structural balance to the XI.")
    if professional_rating >= 8:
        strengths.append("Overall, this looks like a highly competitive XI with strong structural balance.")
    elif professional_rating >= 7:
        strengths.append("This is a well-built squad with a solid overall profile.")
    if ground_fit >= 8:
        strengths.append(f"This squad is exceptionally well suited to {venue_name} based on the pitch profile.")

    if metrics["openers"] < 2:
        weaknesses.append("The side lacks a clearly defined opening pair, which can create instability at the top.")
    if metrics["batting_options"] < 6:
        weaknesses.append("The batting depth is slightly thin, so early wickets could put the middle order under pressure.")
    if metrics["finishers"] < 1:
        weaknesses.append("The side does not have a strong finishing profile in the lower middle order.")
    if metrics["spinners"] < 1:
        weaknesses.append("The bowling attack lacks spin variety, which can be a problem on slower or turning tracks.")
    if metrics["pacers"] < 2:
        weaknesses.append("The pace resources are limited, which can hurt both new-ball and death-over control.")
    if metrics["all_rounders"] < 1:
        weaknesses.append("There is limited all-round support, which reduces tactical flexibility.")
    if metrics["wicketkeepers"] < 1:
        weaknesses.append("The XI structure is incomplete because there is no wicketkeeper presence.")
    if metrics["bowling_options"] < 5:
        weaknesses.append("The bowling depth is below ideal, increasing dependence on a small core of bowlers.")
    if metrics["top3_share"] > 0.45:
        weaknesses.append("The batting quality is too concentrated in the top three, so the team may be overdependent on a few players.")
    if metrics["bottom3_avg"] < 5.5:
        weaknesses.append("The lower end of the XI looks weak on rating average, which affects depth and recovery ability.")
    if professional_rating < 6.5:
        weaknesses.append("Overall squad quality is below ideal and the XI may struggle against stronger opposition.")
    if ground_fit < 6:
        weaknesses.append(f"This squad is not naturally suited to the conditions at {venue_name}.")

    if venue_row is not None:
        venue_pitch = normalize_text(str(venue_row.get("pitch_type", "")))
        if venue_pitch == "spin":
            if metrics["spinners"] >= 2:
                venue_points.append(f"{venue_name} is a spin-friendly venue, and this squad has enough spin resources to exploit those conditions.")
            else:
                venue_points.append(f"{venue_name} generally rewards spin bowling, but this squad may be slightly underprepared in that department.")
        elif venue_pitch == "pace":
            if metrics["pacers"] >= 3:
                venue_points.append(f"{venue_name} offers pace assistance, and this XI has enough seam resources to take advantage of it.")
            else:
                venue_points.append(f"{venue_name} can reward pacers, but this squad may need a stronger seam attack for ideal balance.")
        elif venue_pitch == "batting":
            if metrics["batting_options"] >= 7:
                venue_points.append(f"{venue_name} is batting friendly, and this squad has the depth to post or chase large totals.")
            else:
                venue_points.append(f"{venue_name} tends to produce high-scoring games, so a little more batting depth would improve suitability.")
        elif venue_pitch == "slow":
            if metrics["spinners"] >= 2 and metrics["all_rounders"] >= 1:
                venue_points.append(f"{venue_name} is on the slower side, and this squad is reasonably equipped with spin and control options.")
            else:
                venue_points.append(f"{venue_name} can be slow and tactical, but this XI may need more spin or control options.")
        elif venue_pitch == "balanced":
            venue_points.append(f"{venue_name} is relatively balanced, so team structure and execution will matter more than one dominant skill type.")

        if better_to and better_to.lower() not in ["unknown", "nan", "none"]:
            venue_points.append(f"Historically, teams do better here when they {better_to.lower()}.")

    if venue_row is not None and normalize_text(str(venue_row.get("pitch_type", ""))) in ["spin", "slow"] and metrics["spinners"] < 2:
        suggestions.append("Consider adding one more spinner or a spin-bowling all-rounder for these conditions.")
    if venue_row is not None and normalize_text(str(venue_row.get("pitch_type", ""))) == "pace" and metrics["pacers"] < 3:
        suggestions.append("Consider strengthening the pace attack to improve suitability for this venue.")
    if venue_row is not None and normalize_text(str(venue_row.get("pitch_type", ""))) == "batting" and metrics["batting_options"] < 7:
        suggestions.append("Adding one more batting option or finisher would improve performance on a batting-friendly pitch.")
    if metrics["finishers"] < 1:
        suggestions.append("A more reliable finisher in slots 6 to 8 would improve chase stability and death-over output.")
    if metrics["all_rounders"] < 1:
        suggestions.append("Adding an all-rounder would improve balance between batting depth and bowling coverage.")
    if metrics["bowling_options"] < 5:
        suggestions.append("The XI needs one more reliable bowling option to reduce pressure on the core attack.")
    if not suggestions:
        suggestions.append("This squad is already well balanced; only minor tactical changes would be needed depending on opposition.")

    strengths = strengths[:3] if strengths else ["The squad has a workable overall structure with a few useful positives."]
    weaknesses = weaknesses[:3] if weaknesses else ["There are no major structural weaknesses, although execution and matchups will still matter."]
    venue_points = venue_points[:2] if venue_points else [f"The venue profile for {venue_name} does not create any extreme bias for or against this XI."]
    suggestions = suggestions[:1]

    return {
        "summary": (
            f"This squad has a Professional Rating of {professional_rating}/10, a Batting Rating of {batting_rating_val}/10, "
            f"a Bowling Rating of {bowling_rating_val}/10, a Ground Fit Rating of {ground_fit}/10, "
            f"and a Venue Adjusted Rating of {venue_adjusted}/10. "
            f"The selected venue is {venue_name}, which is categorized as a {pitch_type} surface."
        ),
        "strengths": strengths,
        "weaknesses": weaknesses,
        "venue_points": venue_points,
        "suggestion": suggestions[0],
    }

# ============================
# CONTEXT / PREDICTION
# ============================
@st.cache_resource
def train_context_model(matches):
    train_df = matches.copy()
    train_df["team1_c"] = train_df["team1"].apply(canonical_team_name)
    train_df["team2_c"] = train_df["team2"].apply(canonical_team_name)
    train_df["toss_winner_c"] = train_df["toss_winner"].apply(canonical_team_name)
    train_df["winner_c"] = train_df["winner"].apply(canonical_team_name)

    train_df["Eliminator"] = train_df["Eliminator"].replace({"Unknown": "N"}).fillna("N")
    train_df["method"] = train_df["method"].replace({"Unknown": "normal"}).fillna("normal")

    features = train_df[["team1_c", "team2_c", "city", "toss_winner_c", "toss_decision", "Eliminator", "method"]].copy()
    X = pd.get_dummies(features, drop_first=False)
    y = train_df["winner_c"].copy()

    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=10,
        min_samples_split=4,
        min_samples_leaf=2,
        random_state=42,
    )
    model.fit(X, y)
    return model, X.columns.tolist()


context_model, context_feature_columns = train_context_model(matches_df)


def build_context_features(team1, team2, venue, toss_winner, toss_decision="field", Eliminator="N", method="normal"):
    row = pd.DataFrame([{
        "team1_c": canonical_team_name(team1),
        "team2_c": canonical_team_name(team2),
        "city": venue,
        "toss_winner_c": canonical_team_name(toss_winner),
        "toss_decision": toss_decision,
        "eliminator": Eliminator,
        "method": method
    }])

    row_enc = pd.get_dummies(row, drop_first=False)
    row_enc = row_enc.reindex(columns=context_feature_columns, fill_value=0)
    return row_enc


def head_to_head_prob(hist_df, team1, team2):
    t1 = canonical_team_name(team1)
    t2 = canonical_team_name(team2)
    matches = hist_df[
        ((hist_df["team1"].apply(canonical_team_name) == t1) & (hist_df["team2"].apply(canonical_team_name) == t2)) |
        ((hist_df["team1"].apply(canonical_team_name) == t2) & (hist_df["team2"].apply(canonical_team_name) == t1))
    ]
    if len(matches) == 0:
        return 0.5, 0.5
    t1_wins = sum(matches["winner"].apply(canonical_team_name) == t1)
    t2_wins = sum(matches["winner"].apply(canonical_team_name) == t2)
    total = t1_wins + t2_wins
    if total == 0:
        return 0.5, 0.5
    return t1_wins / total, t2_wins / total


def venue_prob(hist_df, team1, team2, venue):
    venue_matches = hist_df[hist_df["city"] == venue]
    if len(venue_matches) == 0:
        return 0.5, 0.5

    t1 = canonical_team_name(team1)
    t2 = canonical_team_name(team2)
    t1_wins = sum(venue_matches["winner"].apply(canonical_team_name) == t1)
    t2_wins = sum(venue_matches["winner"].apply(canonical_team_name) == t2)
    total = t1_wins + t2_wins
    if total == 0:
        return 0.5, 0.5
    return t1_wins / total, t2_wins / total


def toss_prob(hist_df, team1, team2, toss_winner):
    t1 = canonical_team_name(team1)
    t2 = canonical_team_name(team2)
    tw = canonical_team_name(toss_winner)

    matches = hist_df[
        ((hist_df["team1"].apply(canonical_team_name) == t1) & (hist_df["team2"].apply(canonical_team_name) == t2)) |
        ((hist_df["team1"].apply(canonical_team_name) == t2) & (hist_df["team2"].apply(canonical_team_name) == t1))
    ]
    if len(matches) == 0:
        return 0.5, 0.5

    toss_win_matches = matches[matches["toss_winner"].apply(canonical_team_name) == tw]
    if len(toss_win_matches) == 0:
        return 0.5, 0.5

    t1_wins = sum(toss_win_matches["winner"].apply(canonical_team_name) == t1)
    t2_wins = sum(toss_win_matches["winner"].apply(canonical_team_name) == t2)
    total = t1_wins + t2_wins
    if total == 0:
        return 0.5, 0.5
    return t1_wins / total, t2_wins / total


def ml_context_prob(team1, team2, venue, toss_winner, toss_decision):
    row = build_context_features(team1, team2, venue, toss_winner, toss_decision)
    proba = context_model.predict_proba(row)[0]
    classes = context_model.classes_

    t1 = canonical_team_name(team1)
    t2 = canonical_team_name(team2)

    p1 = 0.0
    p2 = 0.0
    for cls, p in zip(classes, proba):
        if cls == t1:
            p1 = float(p)
        elif cls == t2:
            p2 = float(p)

    total = p1 + p2
    if total <= 0:
        return 0.5, 0.5

    return p1 / total, p2 / total


def venue_strategy_boost(team, impact, venue_row, toss_winner, toss_decision, selected_team_name):
    if venue_row is None:
        return 0.0

    boost = 0.0
    pitch_type = str(venue_row.get("pitch_type", "")).lower()
    better_to = str(venue_row.get("better_to", "")).lower()
    toss_win_match_pct = venue_row.get("toss_win_match_pct", 50)

    spin_count = int(team["Bowling Type"].apply(is_spinner).sum())
    pace_count = int(team["Bowling Type"].apply(is_pacer).sum())
    batting_depth = int(team.apply(lambda row: is_batter(row["Role"]) or is_all_rounder(row["Role"]), axis=1).sum())

    if pitch_type == "spin":
        boost += min(0.6, spin_count * 0.15)
    elif pitch_type == "pace":
        boost += min(0.6, pace_count * 0.15)
    elif pitch_type == "batting":
        boost += min(0.6, batting_depth * 0.08)
    elif pitch_type == "slow":
        boost += min(0.5, spin_count * 0.12 + int(team["Role"].apply(is_all_rounder).sum()) * 0.08)
    elif pitch_type == "balanced":
        boost += 0.2

    if normalize_text(toss_winner) == normalize_text(selected_team_name):
        if better_to == "bat first" and normalize_text(toss_decision) == "bat":
            boost += 0.35
        elif better_to == "bowl first" and normalize_text(toss_decision) == "field":
            boost += 0.35

        if pd.notna(toss_win_match_pct):
            boost += min(0.35, (float(toss_win_match_pct) - 50) / 100)

    return round(boost, 3)


def hybrid_prediction(hist_df, venue_df_local, team1_name, xi1, impact1, team2_name, xi2, impact2, venue, toss_winner, toss_decision):
    # infer batting first / bowling first
    if canonical_team_name(toss_winner) == canonical_team_name(team1_name):
        if str(toss_decision).strip().lower() == "bat":
            team1_mode = "bat_first"
            team2_mode = "bowl_first"
        else:
            team1_mode = "bowl_first"
            team2_mode = "bat_first"
    else:
        if str(toss_decision).strip().lower() == "bat":
            team1_mode = "bowl_first"
            team2_mode = "bat_first"
        else:
            team1_mode = "bat_first"
            team2_mode = "bowl_first"

    r1 = match_strength(xi1, impact1, innings_mode=team1_mode)
    r2 = match_strength(xi2, impact2, innings_mode=team2_mode)

    venue_row = get_venue_row(venue_df_local, venue)

    adj1, adj_break1 = venue_adjusted_team_rating(r1["effective_team"], impact1, venue_row)
    adj2, adj_break2 = venue_adjusted_team_rating(r2["effective_team"], impact2, venue_row)

    rating1 = (r1["strength"] * 0.7) + (adj1 * 0.3)
    rating2 = (r2["strength"] * 0.7) + (adj2 * 0.3)
    rating_total = rating1 + rating2

    rating_prob1 = rating1 / rating_total if rating_total > 0 else 0.5
    rating_prob2 = rating2 / rating_total if rating_total > 0 else 0.5

    h2h1, h2h2 = head_to_head_prob(hist_df, team1_name, team2_name)
    v1, v2 = venue_prob(hist_df, team1_name, team2_name, venue)
    t1, t2 = toss_prob(hist_df, team1_name, team2_name, toss_winner)
    ml1, ml2 = ml_context_prob(team1_name, team2_name, venue, toss_winner, toss_decision)

    venue_boost1 = venue_strategy_boost(r1["effective_team"], impact1, venue_row, toss_winner, toss_decision, team1_name)
    venue_boost2 = venue_strategy_boost(r2["effective_team"], impact2, venue_row, toss_winner, toss_decision, team2_name)

    context1 = h2h1 * 0.25 + v1 * 0.15 + t1 * 0.10 + ml1 * 0.30 + venue_boost1 * 0.20
    context2 = h2h2 * 0.25 + v2 * 0.15 + t2 * 0.10 + ml2 * 0.30 + venue_boost2 * 0.20

    final1 = rating_prob1 * 0.60 + context1 * 0.40
    final2 = rating_prob2 * 0.60 + context2 * 0.40

    total = final1 + final2
    prob1 = round((final1 / total) * 100, 2) if total > 0 else 50.0
    prob2 = round((final2 / total) * 100, 2) if total > 0 else 50.0

    if prob1 > prob2:
        winner = team1_name
    elif prob2 > prob1:
        winner = team2_name
    else:
        winner = "Too close to call"

    return {
        "winner": winner,
        "team1": r1,
        "team2": r2,
        "prob1": prob1,
        "prob2": prob2,
        "rating_prob1": round(rating_prob1 * 100, 2),
        "rating_prob2": round(rating_prob2 * 100, 2),
        "context_prob1": round(context1 * 100, 2),
        "context_prob2": round(context2 * 100, 2),
        "h2h1": round(h2h1 * 100, 2),
        "h2h2": round(h2h2 * 100, 2),
        "venue1": round(v1 * 100, 2),
        "venue2": round(v2 * 100, 2),
        "toss1": round(t1 * 100, 2),
        "toss2": round(t2 * 100, 2),
        "ml1": round(ml1 * 100, 2),
        "ml2": round(ml2 * 100, 2),
        "venue_boost1": round(venue_boost1 * 100, 2),
        "venue_boost2": round(venue_boost2 * 100, 2),
        "ground_fit1": adj_break1["Ground Fit Rating"],
        "ground_fit2": adj_break2["Ground Fit Rating"],
        "venue_adjusted1": adj1,
        "venue_adjusted2": adj2,
        "team1_mode": team1_mode,
        "team2_mode": team2_mode
    }
# ============================
# SECTION HELPERS
# ============================
def manual_team_selection(team_name, full_df, key_prefix):
    squad_df = full_df[full_df["Team"] == team_name].copy().reset_index(drop=True)
    squad_df = prepare_team_df(squad_df)

    st.markdown(f"### {team_name} Squad Selection")

    starting_players = st.multiselect(
        f"Select exactly 11 starting players for {team_name}",
        squad_df["Name"].tolist(),
        key=f"{key_prefix}_starting_players",
    )

    remaining_pool = squad_df[~squad_df["Name"].isin(starting_players)]["Name"].tolist()

    impact_players_selected = st.multiselect(
        f"Select exactly 5 impact players for {team_name}",
        remaining_pool,
        key=f"{key_prefix}_impact_players",
    )

    xi = pd.DataFrame()
    impact = pd.DataFrame()

    if len(starting_players) == 11:
        xi = squad_df.set_index("Name").loc[starting_players].reset_index()
        xi = prepare_team_df(xi)
    elif len(starting_players) > 11:
        st.error(f"Select only 11 starting players for {team_name}")

    if len(impact_players_selected) == 5:
        impact = squad_df.set_index("Name").loc[impact_players_selected].reset_index()
        impact = prepare_team_df(impact)
    elif len(impact_players_selected) > 5:
        st.error(f"Select only 5 impact players for {team_name}")

    return xi, impact


def auto_best_team_for_match(team_name, full_df, venue_row=None):
    temp_df = full_df[full_df["Team"] == team_name].copy().reset_index(drop=True)
    temp_df = prepare_team_df(temp_df)
    if temp_df.empty:
        return pd.DataFrame(), pd.DataFrame()
    xi = create_team(temp_df, venue_row=venue_row)
    impact = impact_players(xi, temp_df)
    return xi, impact


def show_squad(title, xi, impact):
    st.markdown(f"### {title}")
    if xi.empty:
        st.warning("No XI available")
        return

    st.markdown("**Playing XI**")
    for i, row in xi.iterrows():
        show_player_card(f"{i+1}.", row)

    st.markdown("**Impact / Bench**")
    if impact is not None and not impact.empty:
        for _, row in impact.iterrows():
            show_player_card("•", row)
    else:
        st.info("No impact players available")
def show_impact_suggestions(team_name, xi, impact, innings_mode):
    suggested = suggest_best_impact_options(xi, impact, innings_mode=innings_mode, top_n=2)

    if suggested is None or suggested.empty:
        return

    mode_label = "batting first" if innings_mode == "bat_first" else "bowling first"
    st.markdown(f"### 💡 {team_name} - Ideal Impact Options ({mode_label})")

    for i, row in suggested.iterrows():
        show_player_card(f"{i+1}.", row)

def get_head_to_head_table(hist_df, team1, team2):
    t1 = canonical_team_name(team1)
    t2 = canonical_team_name(team2)

    matches = hist_df[
        ((hist_df["team1"].apply(canonical_team_name) == t1) & (hist_df["team2"].apply(canonical_team_name) == t2)) |
        ((hist_df["team1"].apply(canonical_team_name) == t2) & (hist_df["team2"].apply(canonical_team_name) == t1))
    ].copy()

    if matches.empty:
        return None

    matches["winner_c"] = matches["winner"].apply(canonical_team_name)
    t1_wins = int((matches["winner_c"] == t1).sum())
    t2_wins = int((matches["winner_c"] == t2).sum())
    total = len(matches)

    summary = pd.DataFrame({
        "Team": [team1, team2],
        "Wins": [t1_wins, t2_wins],
        "Win %": [
            round((t1_wins / total) * 100, 2) if total > 0 else 0,
            round((t2_wins / total) * 100, 2) if total > 0 else 0,
        ],
    })

    details = matches[["team1", "team2", "city", "toss_winner", "toss_decision", "winner"]].reset_index(drop=True)
    return summary, details


def show_best_squad_for_venue(team_name, full_df, venue_row):
    squad_df = full_df[full_df["Team"] == team_name].copy().reset_index(drop=True)
    squad_df = prepare_team_df(squad_df)

    if squad_df.empty:
        st.warning(f"No squad found for {team_name}")
        return

    xi = create_team(squad_df, venue_row=venue_row)
    impact = impact_players(xi, squad_df)
    venue_adj, venue_adj_break = venue_adjusted_team_rating(xi, impact, venue_row)

    st.markdown(f"### {team_name}")
    render_metric_tiles([
        ("Professional", f"{venue_adj_break['Overall Rating']}/10", "Base team quality"),
        ("Batting", f"{venue_adj_break['Batting Rating']}/10", "Batting profile"),
        ("Bowling", f"{venue_adj_break['Bowling Rating']}/10", "Bowling profile"),
        ("Ground Fit", f"{venue_adj_break['Ground Fit Rating']}/10", "Venue suitability"),
        ("Venue Adjusted", f"{venue_adj_break['Venue Adjusted Rating']}/10", "Final venue score"),
    ])

    for i, row in xi.iterrows():
        show_player_card(f"{i+1}.", row)

    st.markdown("**Impact Players**")
    if not impact.empty:
        for _, row in impact.iterrows():
            show_player_card("•", row)
    else:
        st.info("No impact players available")

    explanation = llm_style_squad_explainer(
        team_name=team_name,
        venue_name=str(venue_row.get("venue", "Unknown")) if venue_row is not None else "Unknown",
        venue_row=venue_row,
        xi=xi,
        impact=impact,
        professional_rating=venue_adj_break["Overall Rating"],
        breakdown=venue_adj_break["Breakdown"],
        venue_adjusted_break=venue_adj_break
    )

    with st.expander(f"🧠 Premium analyst view: {team_name}"):
        render_text_box("insight", "Analyst Summary", explanation["summary"])
        for s in explanation["strengths"]:
            render_text_box("strength", "Strength", s)
        for w in explanation["weaknesses"]:
            render_text_box("weakness", "Weakness", w)
        for v in explanation["venue_points"]:
            render_text_box("insight", "Venue Fit", v)
        render_text_box("tip", "Suggested Improvement", explanation["suggestion"])

def get_team_match_stats(matches_df, selected_team, venue_filter=None, opponent_filter=None, innings_filter="All"):
    df_stats = matches_df.copy()

    # standardize team names
    df_stats["team1_c"] = df_stats["team1"].apply(canonical_team_name)
    df_stats["team2_c"] = df_stats["team2"].apply(canonical_team_name)
    df_stats["winner_c"] = df_stats["winner"].apply(canonical_team_name)
    df_stats["toss_winner_c"] = df_stats["toss_winner"].apply(canonical_team_name)

    selected_team_c = canonical_team_name(selected_team)

    # keep only matches involving selected team
    df_stats = df_stats[
        (df_stats["team1_c"] == selected_team_c) |
        (df_stats["team2_c"] == selected_team_c)
    ].copy()

    if df_stats.empty:
        return None, None, None

    # identify opponent
    df_stats["opponent"] = df_stats.apply(
        lambda row: row["team2_c"] if row["team1_c"] == selected_team_c else row["team1_c"],
        axis=1
    )

    # venue filter
    if venue_filter and venue_filter != "All":
        df_stats = df_stats[df_stats["city"].astype(str).str.strip() == venue_filter].copy()

    # opponent filter
    if opponent_filter and opponent_filter != "All":
        opp_c = canonical_team_name(opponent_filter)
        df_stats = df_stats[df_stats["opponent"] == opp_c].copy()

    if df_stats.empty:
        return None, None, None

    # figure out whether selected team batted first or bowled first
    # In IPL data, team1 is generally batting first unless toss/decision changes logic in reality,
    # but for a practical dashboard, we use toss_decision + toss_winner to infer first innings.
    def team_batting_first(row):
        toss_winner = row["toss_winner_c"]
        toss_decision = str(row["toss_decision"]).strip().lower()
        team1 = row["team1_c"]
        team2 = row["team2_c"]

        if toss_winner == team1:
            if toss_decision == "bat":
                batting_first = team1
            else:
                batting_first = team2
        elif toss_winner == team2:
            if toss_decision == "bat":
                batting_first = team2
            else:
                batting_first = team1
        else:
            batting_first = team1

        return batting_first == selected_team_c

    df_stats["batting_first"] = df_stats.apply(team_batting_first, axis=1)
    df_stats["bowling_first"] = ~df_stats["batting_first"]

    # innings filter
    if innings_filter == "Batting First":
        df_stats = df_stats[df_stats["batting_first"]].copy()
    elif innings_filter == "Bowling First":
        df_stats = df_stats[df_stats["bowling_first"]].copy()

    if df_stats.empty:
        return None, None, None

    # win/loss columns
    df_stats["won"] = df_stats["winner_c"] == selected_team_c
    df_stats["lost"] = (~df_stats["won"]) & (df_stats["winner_c"].isin([selected_team_c]) == False)

    # base summary
    matches_played = len(df_stats)
    wins = int(df_stats["won"].sum())
    losses = matches_played - wins
    win_pct = round((wins / matches_played) * 100, 2) if matches_played > 0 else 0

    toss_wins = int((df_stats["toss_winner_c"] == selected_team_c).sum())
    toss_win_pct = round((toss_wins / matches_played) * 100, 2) if matches_played > 0 else 0

    batting_first_matches = int(df_stats["batting_first"].sum())
    bowling_first_matches = int(df_stats["bowling_first"].sum())

    wins_batting_first = int(df_stats[df_stats["batting_first"]]["won"].sum())
    wins_bowling_first = int(df_stats[df_stats["bowling_first"]]["won"].sum())

    bat_first_win_pct = round((wins_batting_first / batting_first_matches) * 100, 2) if batting_first_matches > 0 else 0
    bowl_first_win_pct = round((wins_bowling_first / bowling_first_matches) * 100, 2) if bowling_first_matches > 0 else 0

    summary = {
        "Matches Played": matches_played,
        "Wins": wins,
        "Losses": losses,
        "Win %": win_pct,
        "Toss Wins": toss_wins,
        "Toss Win %": toss_win_pct,
        "Batting First Matches": batting_first_matches,
        "Bowling First Matches": bowling_first_matches,
        "Wins Batting First": wins_batting_first,
        "Wins Bowling First": wins_bowling_first,
        "Bat First Win %": bat_first_win_pct,
        "Bowl First Win %": bowl_first_win_pct,
    }

    # opponent-wise table
    opp_table = (
        df_stats.groupby("opponent")
        .agg(
            Matches=("opponent", "count"),
            Wins=("won", "sum")
        )
        .reset_index()
    )
    opp_table["Losses"] = opp_table["Matches"] - opp_table["Wins"]
    opp_table["Win %"] = ((opp_table["Wins"] / opp_table["Matches"]) * 100).round(2)
    opp_table = opp_table.sort_values(["Win %", "Wins"], ascending=[False, False]).reset_index(drop=True)

    # venue-wise table
    venue_table = (
        df_stats.groupby("city")
        .agg(
            Matches=("city", "count"),
            Wins=("won", "sum")
        )
        .reset_index()
    )
    venue_table["Losses"] = venue_table["Matches"] - venue_table["Wins"]
    venue_table["Win %"] = ((venue_table["Wins"] / venue_table["Matches"]) * 100).round(2)
    venue_table = venue_table.sort_values(["Win %", "Wins"], ascending=[False, False]).reset_index(drop=True)

    return summary, opp_table, venue_table
# ============================
# APP HEADER + SIDEBAR
# ============================
render_hero()
render_welcome_banner()
render_quick_stats()
render_feature_cards()

st.sidebar.markdown("## 🏏 IPL Analytics")
st.sidebar.caption("Premium portfolio dashboard")
st.sidebar.markdown("### Navigate")

app_mode = st.sidebar.radio(
    "Choose what you want to do",
    [
        "Single Team Analysis",
        "Teams' Past Head-to-Head Records",
        "Best Playing Squads According to Venue",
        "Match Winner Prediction",
        "Venue Information",
        "Team Stats Explorer",
    ],
)

# ============================
# MODE 1
# ============================
if app_mode == "Single Team Analysis":
    render_section_header("Single Team Analysis", "📋")
    st.caption("Evaluate a selected squad with venue-aware ratings, innings-mode logic, and analyst-style explanation.")

    selected_team = st.selectbox(
        "Select IPL Team",
        sorted(df["Team"].dropna().unique()),
        key="single_team_select"
    )

    single_team_venue_options = sorted(
        venue_df["venue"].dropna().astype(str).str.strip().unique().tolist()
    )
    single_team_venue_options.append("Others")

    single_team_venue = st.selectbox(
        "Select Venue for Squad Fit Analysis",
        single_team_venue_options,
        key="single_team_venue_mode",
    )

    if single_team_venue == "Others":
        single_team_venue = st.text_input("Enter Custom Venue", key="single_team_custom_venue")

    single_team_mode = st.radio(
        "Squad Situation",
        ["Batting First", "Bowling First"],
        horizontal=True,
        key="single_team_innings_mode"
    )

    innings_mode = "bat_first" if single_team_mode == "Batting First" else "bowl_first"

    team_df = df[df["Team"] == selected_team].copy().reset_index(drop=True)
    team_df = prepare_team_df(team_df)

    if team_df.empty:
        st.error("No players found for selected team.")
    else:
        starting_players = st.multiselect(
            "Select exactly 11 starting players",
            team_df["Name"].tolist(),
            key="single_team_starting_xi"
        )
        remaining_pool = team_df[~team_df["Name"].isin(starting_players)]["Name"].tolist()

        impact_players_selected = st.multiselect(
            "Select exactly 5 impact players",
            remaining_pool,
            key="single_team_impact_5"
        )

        if st.button("Analyze Team"):
            if len(starting_players) != 11:
                st.error("Please select exactly 11 starting players.")
            elif len(impact_players_selected) != 5:
                st.error("Please select exactly 5 impact players.")
            else:
                xi = team_df.set_index("Name").loc[starting_players].reset_index()
                xi = prepare_team_df(xi)

                impact = team_df.set_index("Name").loc[impact_players_selected].reset_index()
                impact = prepare_team_df(impact)

                effective_team, projected_impact, replaced_player = build_effective_team_with_impact(
                    xi, impact, innings_mode
                )
                if effective_team is None or effective_team.empty:
                    st.error("Could not build an effective team from the selected XI and impact players.")
                else:
                    rating_user, breakdown = stricter_professional_rating(effective_team, impact, return_breakdown=True)
                    venue_row = get_venue_row(venue_df, single_team_venue)
                    _, adj_break = venue_adjusted_team_rating(effective_team, impact, venue_row)

                    render_metric_tiles([
                        ("Professional", f"{rating_user}/10", "Overall squad quality"),
                        ("Batting", f"{breakdown['Batting Rating']}/10", "Batting structure"),
                        ("Bowling", f"{breakdown['Bowling Rating']}/10", "Bowling resources"),
                        ("Ground Fit", f"{adj_break['Ground Fit Rating']}/10", "Venue suitability"),
                        ("Venue Adjusted", f"{adj_break['Venue Adjusted Rating']}/10", "Final venue-aware score"),
                     ])

                    render_section_header("Starting XI", "🧾")
                    for i, row in xi.iterrows():
                        show_player_card(f"{i+1}.", row)

                    render_section_header("Impact Options", "🎯")
                    for i, row in impact.iterrows():
                        show_player_card(f"{i+1}.", row)

                    suggested = suggest_best_impact_options(xi, impact, innings_mode=innings_mode, top_n=2)
                    if not suggested.empty:
                        render_section_header(f"Ideal Impact Options ({single_team_mode.lower()})", "💡")
                        for i, row in suggested.iterrows():
                            show_player_card(f"{i+1}.", row)

                    if projected_impact is not None:
                        render_text_box(
                            "insight",
                            "Projected Impact Used in Rating",
                            f"{projected_impact['Name']} was considered as the projected impact player for {single_team_mode.lower()}."
                        )

                    if replaced_player is not None:
                        render_text_box(
                            "insight",
                            "Effective XI Swap",
                            f"{projected_impact['Name']} was projected to replace {replaced_player['Name']} for rating and balance calculation."
                        )

                    render_section_header("Effective XI Used for Rating", "⚙️")
                    for i, row in effective_team.iterrows():
                        show_player_card(f"{i+1}.", row)

                    if breakdown.get("Reasons"):
                        render_section_header("Rating Deductions", "⚠️")
                        for reason in breakdown["Reasons"]:
                            render_text_box("weakness", "Weakness", reason)

                    if breakdown.get("Analysis Flags"):
                        render_section_header("Squad Observations", "🔎")
                        for flag in breakdown["Analysis Flags"]:
                            render_text_box("insight", "Observation", flag)

        if st.button("Explain This Squad", key="explain_single_team"):
            if len(starting_players) != 11:
               st.error("Please select exactly 11 starting players first.")
            elif len(impact_players_selected) != 5:
                st.error("Please select exactly 5 impact players first.")
            else:
                xi = team_df.set_index("Name").loc[starting_players].reset_index()
                xi = prepare_team_df(xi)

                impact = team_df.set_index("Name").loc[impact_players_selected].reset_index()
                impact = prepare_team_df(impact)

                effective_team, projected_impact, replaced_player = build_effective_team_with_impact(
                    xi, impact, innings_mode
                ) 
                if effective_team is None or effective_team.empty:
                    st.error("Could not build an effective team from the selected XI and impact players.")
                else:       
                    rating_user, breakdown = stricter_professional_rating(effective_team, impact, return_breakdown=True)
                    venue_row = get_venue_row(venue_df, single_team_venue)
                    _, adj_break = venue_adjusted_team_rating(effective_team, impact, venue_row)

                    explanation = llm_style_squad_explainer(
                        team_name=selected_team,
                        venue_name=single_team_venue,
                        venue_row=venue_row,
                        xi=effective_team,
                        impact=impact,
                        professional_rating=rating_user,
                        breakdown=breakdown,
                        venue_adjusted_break=adj_break
                    )   

                    render_section_header("LLM-Style Squad Explanation", "🧠")
                    render_text_box("insight", "Analyst Summary", explanation["summary"])

                    for s in explanation["strengths"]:
                        render_text_box("strength", "Strength", s)

                    for w in explanation["weaknesses"]:
                        render_text_box("weakness", "Weakness", w)

                    for v in explanation["venue_points"]:
                        render_text_box("insight", "Venue Fit", v)

                    render_text_box("tip", "Suggested Improvement", explanation["suggestion"])

                    if projected_impact is not None:
                        render_text_box(
                            "insight",
                            "Projected Impact Context",
                            f"{projected_impact['Name']} was treated as the likely impact player for {single_team_mode.lower()} while generating this analysis."
                        )

# ============================
# MODE 2
# ============================
elif app_mode == "Teams' Past Head-to-Head Records":
    render_section_header("Teams' Past Head-to-Head Records", "🤝")
    st.caption("Compare two teams using historical wins, percentages, and match-by-match records.")

    col1, col2 = st.columns(2)
    with col1:
        team1 = st.selectbox("Select Team 1", sorted(df["Team"].dropna().unique()), key="h2h_team1")
    with col2:
        team2 = st.selectbox("Select Team 2", sorted(df["Team"].dropna().unique()), index=1, key="h2h_team2")

    if team1 == team2:
        st.warning("Please select two different teams.")
    else:
        if st.button("Show Head-to-Head"):
            result = get_head_to_head_table(matches_df, team1, team2)
            if result is None:
                st.info("No historical matches found between these teams.")
            else:
                summary, details = result
                render_metric_tiles([
                    (team1, f"{summary.iloc[0]['Wins']}", "Head-to-head wins"),
                    (team2, f"{summary.iloc[1]['Wins']}", "Head-to-head wins"),
                    ("Total Matches", f"{int(summary['Wins'].sum())}", "Recorded meetings"),
                    (f"{team1} Win %", f"{summary.iloc[0]['Win %']}%", "Historical share"),
                    (f"{team2} Win %", f"{summary.iloc[1]['Win %']}%", "Historical share"),
                ])

                render_section_header("Head-to-Head Summary", "📊")
                st.dataframe(summary, use_container_width=True)

                render_section_header("Match Details", "📋")
                st.dataframe(details, use_container_width=True)

# ============================
# MODE 3
# ============================
elif app_mode == "Best Playing Squads According to Venue":
    render_section_header("Best Playing Squads According to Venue", "🧭")
    st.caption("Generate venue-aware best XIs based on pitch type, balance, and squad suitability.")

    best_squad_venue_options = sorted(venue_df["venue"].dropna().astype(str).str.strip().unique().tolist())
    best_squad_venue_options.append("Others")

    selected_venue = st.selectbox(
    "Select Venue",
    best_squad_venue_options,
    key="venue_best_squad",
        )
    if selected_venue == "Others":
        selected_venue = st.text_input("Enter Custom Venue", key="best_squad_custom_venue")

    venue_row = get_venue_row(venue_df, selected_venue)

    selected_teams = st.multiselect(
        "Select team(s) to generate venue-wise best squad",
        sorted(df["Team"].dropna().unique()),
        default=sorted(df["Team"].dropna().unique())[:2],
        key="venue_team_select",
    )

    if st.button("Generate Best Venue Squads"):
        if not selected_teams:
            st.warning("Please select at least one team.")
        else:
            for team_name in selected_teams:
                show_best_squad_for_venue(team_name, df, venue_row)
                st.markdown("---")

# ============================
# MODE 4
# ============================
elif app_mode == "Match Winner Prediction":
    render_section_header("Match Winner Prediction", "🎯")
    st.caption("Prediction combines squad strength, venue fit, toss, head-to-head, and ML context.")

    all_teams = sorted(df["Team"].dropna().unique())
    all_venues = venue_df["venue"].dropna().astype(str).str.strip().unique().tolist()
    all_venues.append("Others")
    col1, col2 = st.columns(2)
    with col1:
        team1_name = st.selectbox("Select Team 1", all_teams, key="match_team1_mode")
    with col2:
        team2_name = st.selectbox("Select Team 2", all_teams, index=1, key="match_team2_mode")

    if team1_name == team2_name:
        st.warning("Please select two different teams.")
    else:
        col3, col4, col5 = st.columns(3)
        with col3:
            venue = st.selectbox("Select Venue", all_venues, key="match_venue_mode")
            if venue == "Others":
                venue = st.text_input("Enter Custom Venue", key="match_custom_venue")
        with col4:
            toss_winner = st.selectbox("Toss Winner", [team1_name, team2_name], key="match_toss_winner_mode")
        with col5:
            toss_decision = st.selectbox("Toss Decision", ["field", "bat"], key="match_toss_decision_mode")

        venue_row_match = get_venue_row(venue_df, venue)

        squad_mode = st.radio(
            "Choose Squad Mode",
            ["Auto Best XI", "Manual Squad Selection"],
            horizontal=True,
            key="match_mode_type",
        )

        xi1, impact1 = pd.DataFrame(), pd.DataFrame()
        xi2, impact2 = pd.DataFrame(), pd.DataFrame()
        # infer innings modes for both teams
        if canonical_team_name(toss_winner) == canonical_team_name(team1_name):
            if str(toss_decision).strip().lower() == "bat":
                team1_mode = "bat_first"
                team2_mode = "bowl_first"
            else:
                team1_mode = "bowl_first"
                team2_mode = "bat_first"
        else:
            if str(toss_decision).strip().lower() == "bat":
                team1_mode = "bowl_first"
                team2_mode = "bat_first"
            else:
                team1_mode = "bat_first"
                team2_mode = "bowl_first"

        if squad_mode == "Auto Best XI":
            xi1, impact1 = auto_best_team_for_match(team1_name, df, venue_row=venue_row_match)
            xi2, impact2 = auto_best_team_for_match(team2_name, df, venue_row=venue_row_match)

            left, right = st.columns(2)
            with left:
                show_squad(f"{team1_name}", xi1, impact1)
                if not impact1.empty:
                    show_impact_suggestions(team1_name, xi1, impact1, team1_mode)
            with right:
                show_squad(f"{team2_name}", xi2, impact2)
                if not impact2.empty:
                    show_impact_suggestions(team2_name, xi2, impact2, team2_mode)
        else:
            left, right = st.columns(2)
            with left:
                xi1, impact1 = manual_team_selection(team1_name, df, "team1_manual_mode")
            with right:
                xi2, impact2 = manual_team_selection(team2_name, df, "team2_manual_mode")

            if not xi1.empty:
                with left:
                    show_squad(f"{team1_name} Selected Squad", xi1, impact1)
                    if not impact1.empty and len(impact1)>=2:
                        show_impact_suggestions(team1_name, xi1, impact1, team1_mode)
            if not xi2.empty:
                with right:
                    show_squad(f"{team2_name} Selected Squad", xi2, impact2)
                    if not impact2.empty and len(impact2)>=2:
                        show_impact_suggestions(team2_name, xi2, impact2, team2_mode)

        ready = (
            not xi1.empty and len(xi1) == 11 and
            not xi2.empty and len(xi2) == 11 and
            not impact1.empty and len(impact1) == 5 and
            not impact2.empty and len(impact2) == 5
        )

        if st.button("Predict Match Winner"):
            if not ready:
                st.error("Please make sure both teams have valid Playing XI and 5 impact player selections.")
            else:
                st.session_state["match_result"] = hybrid_prediction(
                    matches_df, venue_df,
                    team1_name, xi1, impact1,
                    team2_name, xi2, impact2,
                    venue, toss_winner, toss_decision,
                    )
                st.session_state["match_inputs"] = {
                    "team1_name": team1_name,
                    "team2_name": team2_name,
                    "xi1": xi1.copy(),
                    "impact1": impact1.copy(),
                    "xi2": xi2.copy(),
                    "impact2": impact2.copy(),
                    "venue": venue,
                    "toss_winner": toss_winner,
                    "toss_decision": toss_decision,
                    "venue_row_match": venue_row_match,
                    }
                if "match_result" in st.session_state and "match_inputs" in st.session_state:
                    result = st.session_state["match_result"]
                    saved_inputs = st.session_state["match_inputs"]

                    team1_name = saved_inputs["team1_name"]
                    team2_name = saved_inputs["team2_name"]
                    xi1 = saved_inputs["xi1"]
                    impact1 = saved_inputs["impact1"]
                    xi2 = saved_inputs["xi2"]
                    impact2 = saved_inputs["impact2"]
                    venue = saved_inputs["venue"]
                    toss_winner = saved_inputs["toss_winner"]
                    toss_decision = saved_inputs["toss_decision"]
                    venue_row_match = saved_inputs["venue_row_match"]

                render_metric_tiles([
                    (team1_name, f"{result['prob1']}%", "Predicted win probability"),
                    ("Winner", result["winner"], "Hybrid model output"),
                    (team2_name, f"{result['prob2']}%", "Predicted win probability"),
                    ("Venue Fit Edge", f"{result['ground_fit1']} vs {result['ground_fit2']}", "Ground fit comparison"),
                    ("Rating Edge", f"{result['team1']['overall']} vs {result['team2']['overall']}", "Overall squad rating"),
                ])

                tab1, tab2, tab3, tab4 = st.tabs(["📊 Ratings", "📈 Win Comparison", "🧠 Insights", "📋 Data Table"])

                with tab1:
                    c1, c2 = st.columns(2)
                    with c1:
                        render_section_header(team1_name, "🟦")
                        render_compare_bar("Overall Rating", result["team1"]["overall"], 10)
                        render_compare_bar("Batting Rating", result["team1"]["batting"], 10)
                        render_compare_bar("Bowling Rating", result["team1"]["bowling"], 10)
                        render_compare_bar("Ground Fit", result["ground_fit1"], 10)
                        render_compare_bar("Venue Adjusted", result["venue_adjusted1"], 10)

                    with c2:
                        render_section_header(team2_name, "🟥")
                        render_compare_bar("Overall Rating", result["team2"]["overall"], 10)
                        render_compare_bar("Batting Rating", result["team2"]["batting"], 10)
                        render_compare_bar("Bowling Rating", result["team2"]["bowling"], 10)
                        render_compare_bar("Ground Fit", result["ground_fit2"], 10)
                        render_compare_bar("Venue Adjusted", result["venue_adjusted2"], 10)

                with tab2:
                    c1, c2 = st.columns(2)
                    with c1:
                        render_compare_bar(f"{team1_name} Final Win %", result["prob1"], 100)
                        render_compare_bar("Rating Model %", result["rating_prob1"], 100)
                        render_compare_bar("Context Model %", result["context_prob1"], 100)
                        render_compare_bar("Head-to-Head %", result["h2h1"], 100)
                        render_compare_bar("Venue %", result["venue1"], 100)

                    with c2:
                        render_compare_bar(f"{team2_name} Final Win %", result["prob2"], 100)
                        render_compare_bar("Rating Model %", result["rating_prob2"], 100)
                        render_compare_bar("Context Model %", result["context_prob2"], 100)
                        render_compare_bar("Head-to-Head %", result["h2h2"], 100)
                        render_compare_bar("Venue %", result["venue2"], 100)

                with tab3:
                    reasons = []

                    if result["ground_fit1"] > result["ground_fit2"] and result["winner"] == team1_name:
                        reasons.append(f"{team1_name} is better suited to the pitch conditions.")
                    if result["ground_fit2"] > result["ground_fit1"] and result["winner"] == team2_name:
                        reasons.append(f"{team2_name} is better suited to the pitch conditions.")
                    if result["team1"]["overall"] > result["team2"]["overall"] and result["winner"] == team1_name:
                        reasons.append(f"{team1_name} has the stronger overall squad rating.")
                    if result["team2"]["overall"] > result["team1"]["overall"] and result["winner"] == team2_name:
                        reasons.append(f"{team2_name} has the stronger overall squad rating.")
                    if result["team1"]["bowling"] > result["team2"]["bowling"] and result["winner"] == team1_name:
                        reasons.append(f"{team1_name} has the stronger bowling attack.")
                    if result["team2"]["bowling"] > result["team1"]["bowling"] and result["winner"] == team2_name:
                        reasons.append(f"{team2_name} has the stronger bowling attack.")
                    if result["team1"]["batting"] > result["team2"]["batting"] and result["winner"] == team1_name:
                        reasons.append(f"{team1_name} has the stronger batting unit.")
                    if result["team2"]["batting"] > result["team1"]["batting"] and result["winner"] == team2_name:
                        reasons.append(f"{team2_name} has the stronger batting unit.")

                    render_text_box(
                        "strength",
                        "Prediction Summary",
                        f"<b>{result['winner']}</b> is the current favorite based on the hybrid model."
                    )

                    if reasons:
                        for r in reasons[:4]:
                            render_text_box("insight", "Key Factor", r)

                    if result["team1"].get("projected_impact") is not None:
                        render_text_box(
                            "insight",
                            f"{team1_name} Projected Impact Used in Rating",
                            f"{result['team1']['projected_impact']['Name']} was considered as the projected impact player for {result['team1_mode'].replace('_', ' ')}."
                        )

                    if result["team2"].get("projected_impact") is not None:
                        render_text_box(
                            "insight",
                            f"{team2_name} Projected Impact Used in Rating",
                            f"{result['team2']['projected_impact']['Name']} was considered as the projected impact player for {result['team2_mode'].replace('_', ' ')}."
                        )

                    if st.button("Explain Both Squads", key="explain_match_squads"):
                        st.session_state["show_both_squad_explanations"] = True

                    if st.session_state.get("show_both_squad_explanations", False):
                        team1_overall, team1_breakdown = stricter_professional_rating(xi1, impact1, return_breakdown=True)
                        _, team1_adj_break = venue_adjusted_team_rating(xi1, impact1, venue_row_match)

                        team2_overall, team2_breakdown = stricter_professional_rating(xi2, impact2, return_breakdown=True)
                        _, team2_adj_break = venue_adjusted_team_rating(xi2, impact2, venue_row_match)

                        exp1 = llm_style_squad_explainer(
                            team_name=team1_name,
                            venue_name=venue,
                            venue_row=venue_row_match,
                            xi=xi1,
                            impact=impact1,
                            professional_rating=team1_overall,
                            breakdown=team1_breakdown,
                            venue_adjusted_break=team1_adj_break
                        )

                        exp2 = llm_style_squad_explainer(
                            team_name=team2_name,
                            venue_name=venue,
                            venue_row=venue_row_match,
                            xi=xi2,
                            impact=impact2,
                            professional_rating=team2_overall,
                            breakdown=team2_breakdown,
                            venue_adjusted_break=team2_adj_break
                        )

                        c1, c2 = st.columns(2)

                        with c1:
                            render_section_header(f"{team1_name} Explanation", "🧠")
                            render_text_box("insight", "Analyst Summary", exp1["summary"])
                            for s in exp1["strengths"]:
                                render_text_box("strength", "Strength", s)
                            for w in exp1["weaknesses"]:
                                render_text_box("weakness", "Weakness", w)
                            for v in exp1["venue_points"]:
                                render_text_box("insight", "Venue Fit", v)
                            render_text_box("tip", "Suggested Improvement", exp1["suggestion"])

                        with c2:
                            render_section_header(f"{team2_name} Explanation", "🧠")
                            render_text_box("insight", "Analyst Summary", exp2["summary"])
                            for s in exp2["strengths"]:
                                render_text_box("strength", "Strength", s)
                            for w in exp2["weaknesses"]:
                                render_text_box("weakness", "Weakness", w)
                            for v in exp2["venue_points"]:
                                render_text_box("insight", "Venue Fit", v)
                            render_text_box("tip", "Suggested Improvement", exp2["suggestion"])      
                with tab4:
                    compare_df = pd.DataFrame({
                        "Metric": [
                            "Overall Rating",
                            "Batting Rating",
                            "Bowling Rating",
                            "Ground Fit Rating",
                            "Venue Adjusted Rating",
                            "Bench Strength",
                            "Balance Score",
                            "Rating Model %",
                            "Context Model %",
                            "Head-to-Head %",
                            "Venue %",
                            "Toss %",
                            "ML Context %",
                            "Venue Sheet Boost %",
                            "Final Win %"
                        ],
                        team1_name: [
                            result["team1"]["overall"],
                            result["team1"]["batting"],
                            result["team1"]["bowling"],
                            result["ground_fit1"],
                            result["venue_adjusted1"],
                            result["team1"]["bench"],
                            result["team1"]["balance"],
                            result["rating_prob1"],
                            result["context_prob1"],
                            result["h2h1"],
                            result["venue1"],
                            result["toss1"],
                            result["ml1"],
                            result["venue_boost1"],
                            result["prob1"]
                        ],
                        team2_name: [
                            result["team2"]["overall"],
                            result["team2"]["batting"],
                            result["team2"]["bowling"],
                            result["ground_fit2"],
                            result["venue_adjusted2"],
                            result["team2"]["bench"],
                            result["team2"]["balance"],
                            result["rating_prob2"],
                            result["context_prob2"],
                            result["h2h2"],
                            result["venue2"],
                            result["toss2"],
                            result["ml2"],
                            result["venue_boost2"],
                            result["prob2"]
                        ]
                    })
                    st.dataframe(compare_df, use_container_width=True)

# ============================
# MODE 5
# ============================
elif app_mode == "Venue Information":
    render_section_header("Venue Information", "🏟️")
    st.caption("Explore pitch type, toss impact, and venue-specific match tendencies.")

    selected_venue = st.selectbox(
        "Select Venue",
        venue_df["venue"].dropna().astype(str).tolist(),
        key="venue_info_mode",
    )

    row = get_venue_row(venue_df, selected_venue)

    if row is not None:
        render_metric_tiles([
            ("Pitch Type", str(row.get("pitch_type", "")).title(), "Surface nature"),
            ("Toss Win Match %", f"{row.get('toss_win_match_pct', 0):.2f}%" if pd.notna(row.get("toss_win_match_pct", None)) else "N/A", "Toss impact"),
            ("Bat First Win %", f"{row.get('bat_first_win_pct', 0):.2f}%" if pd.notna(row.get("bat_first_win_pct", None)) else "N/A", "Bat-first trend"),
            ("Bowl First Win %", f"{row.get('bowl_first_win_pct', 0):.2f}%" if pd.notna(row.get("bowl_first_win_pct", None)) else "N/A", "Chasing trend"),
            ("Better To", str(row.get("better_to", "")).title(), "Venue tendency"),
        ])

        render_section_header("Full Venue Row", "📋")
        st.dataframe(pd.DataFrame([row]), use_container_width=True)
        
elif app_mode == "Team Stats Explorer":
    render_section_header("Team Stats Explorer", "📊")
    st.caption("Explore a team's overall, venue-wise, opponent-wise, and innings-based record with filters.")

    all_teams = sorted(df["Team"].dropna().unique())
    all_venues = sorted(venue_df["venue"].dropna().astype(str).unique().tolist())
    all_venues.append("Others")
    all_opponents = ["All"] + all_teams

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        selected_team = st.selectbox("Select Team", all_teams, key="stats_team")

    with col2:
        selected_venue = st.selectbox("Select Venue", all_venues, key="stats_venue")
        if selected_venue == "Others":
            selected_venue = st.text_input("Enter venue")
    with col3:
        selected_opponent = st.selectbox("Select Opponent", all_opponents, key="stats_opponent")

    with col4:
        innings_filter = st.selectbox(
            "Match Situation",
            ["All", "Batting First", "Bowling First"],
            key="stats_innings_filter"
        )

    summary, opp_table, venue_table = get_team_match_stats(
        matches_df,
        selected_team=selected_team,
        venue_filter=selected_venue,
        opponent_filter=selected_opponent,
        innings_filter=innings_filter
    )

    if summary is None:
        st.warning("No records found for the selected filters.")
    else:
        render_metric_tiles([
            ("Matches", summary["Matches Played"], "Total filtered matches"),
            ("Wins", summary["Wins"], "Matches won"),
            ("Losses", summary["Losses"], "Matches lost"),
            ("Win %", f"{summary['Win %']}%", "Success rate"),
            ("Toss Wins", summary["Toss Wins"], "Tosses won"),
        ])

        render_metric_tiles([
            ("Toss Win %", f"{summary['Toss Win %']}%", "Toss success rate"),
            ("Bat First", summary["Batting First Matches"], "Matches batting first"),
            ("Bowl First", summary["Bowling First Matches"], "Matches bowling first"),
            ("Bat First Win %", f"{summary['Bat First Win %']}%", "When batting first"),
            ("Bowl First Win %", f"{summary['Bowl First Win %']}%", "When bowling first"),
        ])

        tab1, tab2, tab3 = st.tabs(["📌 Summary", "🤝 Opponent-wise", "🏟️ Venue-wise"])

        with tab1:
            render_text_box(
                "insight",
                "Filter Summary",
                f"Showing records for <b>{selected_team}</b> | Venue: <b>{selected_venue}</b> | "
                f"Opponent: <b>{selected_opponent}</b> | Situation: <b>{innings_filter}</b>"
            )

            render_compare_bar("Win %", summary["Win %"], 100)
            render_compare_bar("Toss Win %", summary["Toss Win %"], 100)
            render_compare_bar("Bat First Win %", summary["Bat First Win %"], 100)
            render_compare_bar("Bowl First Win %", summary["Bowl First Win %"], 100)

        with tab2:
            render_section_header("Opponent-wise Record", "🤝")
            st.dataframe(opp_table, use_container_width=True)

        with tab3:
            render_section_header("Venue-wise Record", "🏟️")
            st.dataframe(venue_table, use_container_width=True)