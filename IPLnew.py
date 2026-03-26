import random
import pandas as pd
import streamlit as st
from sklearn.ensemble import RandomForestClassifier

st.set_page_config(page_title="IPL Analytics App", layout="wide")

# ============================
# STYLES
# ============================
st.markdown("""
<style>
.player-card {
    background: linear-gradient(135deg, #0b1220, #020617);
    padding: 14px 18px;
    border-radius: 14px;
    margin-bottom: 10px;
    color: white;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 15px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.35);
}
.badge {
    padding: 6px 12px;
    border-radius: 999px;
    font-weight: 700;
    font-size: 12px;
    color: white;
}
.badge-bat { background: #2563eb; }
.badge-ar  { background: #059669; }
.badge-bowl{ background: #dc2626; }
.badge-wk  { background: #f59e0b; }
.section-title {
    padding: 10px 14px;
    border-radius: 12px;
    background: #0f172a;
    color: white;
    margin: 12px 0;
    font-weight: 700;
}
.small-note {
    color: #475569;
    font-size: 13px;
}
</style>
""", unsafe_allow_html=True)

st.title("🏏 IPL Analytics App")

# ============================
# LOAD DATA
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
    matches = pd.read_csv("IPL Matches 2008-2022.csv")
    matches.columns = [c.strip() for c in matches.columns]

    needed = ["team1", "team2", "city", "toss_winner", "toss_decision", "winner", "eliminator", "method"]
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
# NORMALIZATION + BASIC HELPERS
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
                <span style="font-size:13px; opacity:0.9;">
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
    row = venue_df_local[venue_df_local["venue"].str.lower() == str(venue).strip().lower()]
    if row.empty:
        return None
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
# ============================
# RATING SYSTEM
# ============================
def team_metrics(team, impact):
    metrics = {}
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


def match_strength(team, impact):
    overall, breakdown = stricter_professional_rating(team, impact, return_breakdown=True)
    bat = batting_rating(team, impact)
    bowl = bowling_rating(team, impact)
    bench = bench_strength(impact)
    balance = balance_score(team, impact)

    strength = overall * 0.40 + bat * 0.20 + bowl * 0.20 + bench * 0.10 + balance * 0.10
    return {
        "overall": overall,
        "batting": bat,
        "bowling": bowl,
        "bench": bench,
        "balance": balance,
        "strength": round(strength, 2),
        "breakdown": breakdown
    }

# ============================
# GROUND / PITCH FIT RATING
# ============================
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

# ============================
# CONTEXT MODEL
# ============================
@st.cache_resource
def train_context_model(matches):
    train_df = matches.copy()
    train_df["team1_c"] = train_df["team1"].apply(canonical_team_name)
    train_df["team2_c"] = train_df["team2"].apply(canonical_team_name)
    train_df["toss_winner_c"] = train_df["toss_winner"].apply(canonical_team_name)
    train_df["winner_c"] = train_df["winner"].apply(canonical_team_name)

    train_df["eliminator"] = train_df["eliminator"].replace({"Unknown": "N"}).fillna("N")
    train_df["method"] = train_df["method"].replace({"Unknown": "normal"}).fillna("normal")

    features = train_df[["team1_c", "team2_c", "city", "toss_winner_c", "toss_decision", "eliminator", "method"]].copy()
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


def build_context_features(team1, team2, venue, toss_winner, toss_decision="field", eliminator="N", method="normal"):
    row = pd.DataFrame([{
        "team1_c": canonical_team_name(team1),
        "team2_c": canonical_team_name(team2),
        "city": venue,
        "toss_winner_c": canonical_team_name(toss_winner),
        "toss_decision": toss_decision,
        "eliminator": eliminator,
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
    r1 = match_strength(xi1, impact1)
    r2 = match_strength(xi2, impact2)

    venue_row = get_venue_row(venue_df_local, venue)

    adj1, adj_break1 = venue_adjusted_team_rating(xi1, impact1, venue_row)
    adj2, adj_break2 = venue_adjusted_team_rating(xi2, impact2, venue_row)

    rating1 = (r1["strength"] * 0.7) + (adj1 * 0.3)
    rating2 = (r2["strength"] * 0.7) + (adj2 * 0.3)
    rating_total = rating1 + rating2

    rating_prob1 = rating1 / rating_total if rating_total > 0 else 0.5
    rating_prob2 = rating2 / rating_total if rating_total > 0 else 0.5

    h2h1, h2h2 = head_to_head_prob(hist_df, team1_name, team2_name)
    v1, v2 = venue_prob(hist_df, team1_name, team2_name, venue)
    t1, t2 = toss_prob(hist_df, team1_name, team2_name, toss_winner)
    ml1, ml2 = ml_context_prob(team1_name, team2_name, venue, toss_winner, toss_decision)

    venue_boost1 = venue_strategy_boost(xi1, impact1, venue_row, toss_winner, toss_decision, team1_name)
    venue_boost2 = venue_strategy_boost(xi2, impact2, venue_row, toss_winner, toss_decision, team2_name)

    context1 = h2h1 * 0.25 + v1 * 0.15 + t1 * 0.10 + ml1 * 0.30 + venue_boost1 * 0.20
    context2 = h2h2 * 0.25 + v2 * 0.15 + t2 * 0.10 + ml2 * 0.30 + venue_boost2 * 0.20

    final1 = rating_prob1 * 0.80 + context1 * 0.20
    final2 = rating_prob2 * 0.80 + context2 * 0.20

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
    }

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

    # ----------------------------
    # STRENGTHS
    # ----------------------------
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

    # ----------------------------
    # WEAKNESSES
    # ----------------------------
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

    # ----------------------------
    # VENUE FIT EXPLANATION
    # ----------------------------
    if venue_row is not None:
        if normalize_text(str(venue_row.get("pitch_type", ""))) == "spin":
            if metrics["spinners"] >= 2:
                venue_points.append(f"{venue_name} is a spin-friendly venue, and this squad has enough spin resources to exploit those conditions.")
            else:
                venue_points.append(f"{venue_name} generally rewards spin bowling, but this squad may be slightly underprepared in that department.")

        elif normalize_text(str(venue_row.get("pitch_type", ""))) == "pace":
            if metrics["pacers"] >= 3:
                venue_points.append(f"{venue_name} offers pace assistance, and this XI has enough seam resources to take advantage of it.")
            else:
                venue_points.append(f"{venue_name} can reward pacers, but this squad may need a stronger seam attack for ideal balance.")

        elif normalize_text(str(venue_row.get("pitch_type", ""))) == "batting":
            if metrics["batting_options"] >= 7:
                venue_points.append(f"{venue_name} is batting friendly, and this squad has the depth to post or chase large totals.")
            else:
                venue_points.append(f"{venue_name} tends to produce high-scoring games, so a little more batting depth would improve suitability.")

        elif normalize_text(str(venue_row.get("pitch_type", ""))) == "slow":
            if metrics["spinners"] >= 2 and metrics["all_rounders"] >= 1:
                venue_points.append(f"{venue_name} is on the slower side, and this squad is reasonably equipped with spin and control options.")
            else:
                venue_points.append(f"{venue_name} can be slow and tactical, but this XI may need more spin or control options.")

        elif normalize_text(str(venue_row.get("pitch_type", ""))) == "balanced":
            venue_points.append(f"{venue_name} is relatively balanced, so team structure and execution will matter more than one dominant skill type.")

        if better_to and better_to.lower() not in ["unknown", "nan", "none"]:
            venue_points.append(f"Historically, teams do better here when they {better_to.lower()}.")

    # ----------------------------
    # SUGGESTIONS
    # ----------------------------
    if metrics["spinners"] < 2 and normalize_text(str(venue_row.get("pitch_type", ""))) in ["spin", "slow"]:
        suggestions.append("Consider adding one more spinner or a spin-bowling all-rounder for these conditions.")
    if metrics["pacers"] < 3 and normalize_text(str(venue_row.get("pitch_type", ""))) == "pace":
        suggestions.append("Consider strengthening the pace attack to improve suitability for this venue.")
    if metrics["batting_options"] < 7 and normalize_text(str(venue_row.get("pitch_type", ""))) == "batting":
        suggestions.append("Adding one more batting option or finisher would improve performance on a batting-friendly pitch.")
    if metrics["finishers"] < 1:
        suggestions.append("A more reliable finisher in slots 6 to 8 would improve chase stability and death-over output.")
    if metrics["all_rounders"] < 1:
        suggestions.append("Adding an all-rounder would improve balance between batting depth and bowling coverage.")
    if metrics["bowling_options"] < 5:
        suggestions.append("The XI needs one more reliable bowling option to reduce pressure on the core attack.")
    if not suggestions:
        suggestions.append("This squad is already well balanced; only minor tactical changes would be needed depending on opposition.")

    # Keep output controlled
    strengths = strengths[:3] if strengths else ["The squad has a workable overall structure with a few useful positives."]
    weaknesses = weaknesses[:3] if weaknesses else ["There are no major structural weaknesses, although execution and matchups will still matter."]
    venue_points = venue_points[:2] if venue_points else [f"The venue profile for {venue_name} does not create any extreme bias for or against this XI."]
    suggestions = suggestions[:1]

    summary = (
        f"**Analyst Summary for {team_name}**\n\n"
        f"This squad has a **Professional Rating of {professional_rating}/10**, a **Batting Rating of {batting_rating_val}/10**, "
        f"a **Bowling Rating of {bowling_rating_val}/10**, a **Ground Fit Rating of {ground_fit}/10**, "
        f"and a **Venue Adjusted Rating of {venue_adjusted}/10**. "
        f"The selected venue is **{venue_name}**, which is categorized as a **{pitch_type}** surface.\n\n"
        f"**Top Strengths**\n"
        f"1. {strengths[0]}\n"
        f"2. {strengths[1] if len(strengths) > 1 else strengths[0]}\n"
        f"3. {strengths[2] if len(strengths) > 2 else strengths[-1]}\n\n"
        f"**Main Weaknesses**\n"
        f"1. {weaknesses[0]}\n"
        f"2. {weaknesses[1] if len(weaknesses) > 1 else weaknesses[0]}\n"
        f"3. {weaknesses[2] if len(weaknesses) > 2 else weaknesses[-1]}\n\n"
        f"**Venue Fit**\n"
        f"- {venue_points[0]}\n"
        f"- {venue_points[1] if len(venue_points) > 1 else venue_points[0]}\n\n"
        f"**Suggested Improvement**\n"
        f"- {suggestions[0]}"
    )

    return summary
# ============================
# UI SECTION HELPERS
# ============================
def manual_team_selection(team_name, full_df, key_prefix):
    squad_df = full_df[full_df["Team"] == team_name].copy().reset_index(drop=True)
    squad_df = prepare_team_df(squad_df)

    st.markdown(f"### {team_name} Squad Selection")
    selected_players = st.multiselect(
        f"Select exactly 12 players for {team_name}",
        squad_df["Name"].tolist(),
        key=f"{key_prefix}_multiselect",
    )

    xi = pd.DataFrame()
    impact = pd.DataFrame()

    if len(selected_players) == 12:
        selected_df = squad_df.set_index("Name").loc[selected_players].reset_index()
        xi = selected_df.iloc[:11].copy().reset_index(drop=True)
        impact = selected_df.iloc[11:].copy().reset_index(drop=True)
    elif len(selected_players) > 12:
        st.error(f"Select only 12 players for {team_name}")

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
    for i, row in xi.iterrows():
        show_player_card(f"{i+1}.", row)

    st.markdown("**Impact Players**")
    if not impact.empty:
        for _, row in impact.iterrows():
            show_player_card("•", row)
    else:
        st.info("No impact players available")

    st.markdown(f"**Ground Fit Rating:** {venue_adj_break['Ground Fit Rating']} / 10")
    st.markdown(f"**Venue Adjusted Rating:** {venue_adj_break['Venue Adjusted Rating']} / 10")
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

    with st.expander(f"🧠 Explain {team_name} squad"):
        st.markdown(explanation)
# ============================
# SIDEBAR MENU
# ============================
st.sidebar.title("🏏 IPL Analytics App")
app_mode = st.sidebar.radio(
    "Choose what you want to do",
    [
        "Single Team Analysis",
        "Teams' Past Head-to-Head Records",
        "Best Playing Squads According to Venue",
        "Match Winner Prediction",
        "Venue Information",
    ],
)

# ============================
# MODE 1
# ============================
if app_mode == "Single Team Analysis":
    st.header("Single Team Analysis")

    selected_team = st.selectbox("Select IPL Team", sorted(df["Team"].dropna().unique()), key="single_team")
    single_team_venue = st.selectbox(
        "Select Venue for Squad Fit Analysis",
        venue_df["venue"].dropna().astype(str).tolist(),
        key="single_team_venue_mode",
    )

    team_df = df[df["Team"] == selected_team].copy().reset_index(drop=True)
    team_df = prepare_team_df(team_df)

    if team_df.empty:
        st.error("No players found for selected team.")
    else:
        user_sel = st.multiselect(
            "Select exactly 12 players",
            team_df["Name"].tolist(),
            key="single_team_selector_mode",
        )

        if st.button("Analyze Team"):
            if len(user_sel) != 12:
                st.error("Please select exactly 12 players.")
            else:
                user_df = team_df.set_index("Name").loc[user_sel].reset_index()
                xi = user_df.iloc[:11].copy()
                impact = user_df.iloc[11:].copy()

                rating_user, breakdown = stricter_professional_rating(xi, impact, return_breakdown=True)
                venue_row = get_venue_row(venue_df, single_team_venue)
                adj_rating, adj_break = venue_adjusted_team_rating(xi, impact, venue_row)
                

                st.markdown("### Your Playing 12")
                for i, row in user_df.iterrows():
                    show_player_card(f"{i+1}.", row)

                st.markdown(f"**Professional Team Rating:** {rating_user} / 10")
                st.markdown(f"**Batting Rating:** {breakdown['Batting Rating']} / 10")
                st.markdown(f"**Bowling Rating:** {breakdown['Bowling Rating']} / 10")
                st.markdown(f"**Ground Fit Rating:** {adj_break['Ground Fit Rating']} / 10")
                st.markdown(f"**Venue Adjusted Rating:** {adj_break['Venue Adjusted Rating']} / 10")
if st.button("Explain This Squad", key="explain_single_team"):
    if len(user_sel) != 12:
        st.error("Please select exactly 12 players first.")
    else:
        user_df = team_df.set_index("Name").loc[user_sel].reset_index()
        xi = user_df.iloc[:11].copy()
        impact = user_df.iloc[11:].copy()

        rating_user, breakdown = stricter_professional_rating(xi, impact, return_breakdown=True)
        venue_row = get_venue_row(venue_df, single_team_venue)
        adj_rating, adj_break = venue_adjusted_team_rating(xi, impact, venue_row)

        explanation = llm_style_squad_explainer(
            team_name=selected_team,
            venue_name=single_team_venue,
            venue_row=venue_row,
            xi=xi,
            impact=impact,
            professional_rating=rating_user,
            breakdown=breakdown,
            venue_adjusted_break=adj_break
        )

        st.markdown("### 🧠 LLM-Style Squad Explanation")
        st.markdown(explanation)            

# ============================
# MODE 2
# ============================
elif app_mode == "Teams' Past Head-to-Head Records":
    st.header("Teams' Past Head-to-Head Records")

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
                st.subheader("Head-to-Head Summary")
                st.dataframe(summary, use_container_width=True)

                st.subheader("Match Details")
                st.dataframe(details, use_container_width=True)

# ============================
# MODE 3
# ============================
elif app_mode == "Best Playing Squads According to Venue":
    st.header("Best Playing Squads According to Venue")

    selected_venue = st.selectbox(
        "Select Venue",
        venue_df["venue"].dropna().astype(str).tolist(),
        key="venue_best_squad",
    )

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
    st.header("Match Winner Prediction")

    all_teams = sorted(df["Team"].dropna().unique())
    all_venues = venue_df["venue"].dropna().astype(str).str.strip().tolist()

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

        if squad_mode == "Auto Best XI":
            xi1, impact1 = auto_best_team_for_match(team1_name, df, venue_row=venue_row_match)
            xi2, impact2 = auto_best_team_for_match(team2_name, df, venue_row=venue_row_match)

            left, right = st.columns(2)
            with left:
                show_squad(f"{team1_name}", xi1, impact1)
            with right:
                show_squad(f"{team2_name}", xi2, impact2)
        else:
            left, right = st.columns(2)
            with left:
                xi1, impact1 = manual_team_selection(team1_name, df, "team1_manual_mode")
            with right:
                xi2, impact2 = manual_team_selection(team2_name, df, "team2_manual_mode")

            if not xi1.empty:
                with left:
                    show_squad(f"{team1_name} Selected Squad", xi1, impact1)
            if not xi2.empty:
                with right:
                    show_squad(f"{team2_name} Selected Squad", xi2, impact2)

        ready = (
            not xi1.empty and len(xi1) == 11 and
            not xi2.empty and len(xi2) == 11
        )

        if st.button("Predict Match Winner"):
            if not ready:
                st.error("Please make sure both teams have valid Playing XI selections.")
            else:
                result = hybrid_prediction(
                    matches_df, venue_df,
                    team1_name, xi1, impact1,
                    team2_name, xi2, impact2,
                    venue, toss_winner, toss_decision,
                )

                st.subheader("Prediction Result")
                a, b, c = st.columns(3)
                with a:
                    st.metric(f"{team1_name} Win %", f"{result['prob1']}%")
                with b:
                    st.metric("Predicted Winner", result["winner"])
                with c:
                    st.metric(f"{team2_name} Win %", f"{result['prob2']}%")

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
                        "Final Win %",
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
                        result["prob1"],
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
                        result["prob2"],
                    ],
                })

                st.subheader("Comparison")
                st.dataframe(compare_df, use_container_width=True)
if st.button("Explain Both Squads", key="explain_match_squads"):
    venue_row = get_venue_row(venue_df, venue)

    team1_overall, team1_breakdown = stricter_professional_rating(xi1, impact1, return_breakdown=True)
    team1_adj, team1_adj_break = venue_adjusted_team_rating(xi1, impact1, venue_row)

    team2_overall, team2_breakdown = stricter_professional_rating(xi2, impact2, return_breakdown=True)
    team2_adj, team2_adj_break = venue_adjusted_team_rating(xi2, impact2, venue_row)

    exp1 = llm_style_squad_explainer(
        team_name=team1_name,
        venue_name=venue,
        venue_row=venue_row,
        xi=xi1,
        impact=impact1,
        professional_rating=team1_overall,
        breakdown=team1_breakdown,
        venue_adjusted_break=team1_adj_break
    )

    exp2 = llm_style_squad_explainer(
        team_name=team2_name,
        venue_name=venue,
        venue_row=venue_row,
        xi=xi2,
        impact=impact2,
        professional_rating=team2_overall,
        breakdown=team2_breakdown,
        venue_adjusted_break=team2_adj_break
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"### 🧠 {team1_name} Explanation")
        st.markdown(exp1)
    with col2:
        st.markdown(f"### 🧠 {team2_name} Explanation")
        st.markdown(exp2)
# ============================
# MODE 5
# ============================
elif app_mode == "Venue Information":
    st.header("Venue Information")

    selected_venue = st.selectbox(
        "Select Venue",
        venue_df["venue"].dropna().astype(str).tolist(),
        key="venue_info_mode",
    )

    row = get_venue_row(venue_df, selected_venue)

    if row is not None:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Pitch Type", str(row.get("pitch_type", "")).title())
        with c2:
            toss_val = row.get("toss_win_match_pct", None)
            st.metric("Toss Win Match %", f"{toss_val:.2f}%" if pd.notna(toss_val) else "N/A")
        with c3:
            bat_val = row.get("bat_first_win_pct", None)
            st.metric("Bat First Win %", f"{bat_val:.2f}%" if pd.notna(bat_val) else "N/A")
        with c4:
            bowl_val = row.get("bowl_first_win_pct", None)
            st.metric("Bowl First Win %", f"{bowl_val:.2f}%" if pd.notna(bowl_val) else "N/A")

        st.markdown("### Full Venue Row")
        st.dataframe(pd.DataFrame([row]), use_container_width=True)
        
