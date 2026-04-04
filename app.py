import streamlit as st
import json
import os
import pandas as pd
from pathlib import Path
from itertools import combinations
import base64
from PIL import Image
import io
from datetime import datetime
try:
    from supabase import create_client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

# ── Config ───────────────────────────────────────────────────────────────────
st.set_page_config(page_title="5A Premier League 2026", page_icon="🏏", layout="wide", initial_sidebar_state="collapsed")

PHOTOS_DIR = Path(__file__).parent / "photos"
STATE_FILE  = Path(__file__).parent / "match_state.json"
OVERS = 4
MAX_WICKETS = 8

# ── Supabase Storage ─────────────────────────────────────────────────────────
def get_supabase():
    try:
        url  = st.secrets["SUPABASE_URL"]
        key  = st.secrets["SUPABASE_KEY"]
        if SUPABASE_AVAILABLE and url and key:
            return create_client(url, key)
    except: pass
    return None

def cloud_load():
    """Load state from Supabase. Returns None if unavailable."""
    sb = get_supabase()
    if not sb: return None
    try:
        res = sb.table("app_state").select("value").eq("key", "match_state").execute()
        if res.data:
            return json.loads(res.data[0]["value"])
    except: pass
    return None

def cloud_save(s):
    """Save state to Supabase. Falls back silently."""
    sb = get_supabase()
    if not sb: return
    try:
        payload = json.dumps(s)
        sb.table("app_state").upsert({"key": "match_state", "value": payload}).execute()
    except: pass

def cloud_clear():
    """Clear state from Supabase."""
    sb = get_supabase()
    if not sb: return
    try:
        sb.table("app_state").delete().eq("key", "match_state").execute()
    except: pass

# ── Team Data ─────────────────────────────────────────────────────────────────
TEAMS = {
    "5A Strikers":      {"color":"#c9a84c","logo":"logo_Strikers.jpg",      "players":["Prathamesh Jadhav","Vaibhav Mohite","Anish Sawant","Sumit Kamble","Subodh Padelkar","Nitin Kamble","Tanmay Jadhav","Sarvesh Sawant"]},
    "5A Knight Riders": {"color":"#e65100","logo":"logo_Knight_Riders.jpg", "players":["Vaibhav Kamble","Siddhesh Jadhav","Harshwardhan Bagade","Siddhesh Vadepalli","Yogesh Tambe","Aakash Kamble","Rajendra Dhotre","Sandesh Padelkar"]},
    "5A Blasters":      {"color":"#b71c1c","logo":"logo_Blasters.jpg",      "players":["Mayur Jadav","Akshay Kamble","Umesh Waydande","Ojas Jadav","Prashant Pawar","Prashant Jadhav","Sahil Jadhav","Abhishek Mohite"]},
    "5A Warriors":      {"color":"#f9a825","logo":"logo_Warriors.jpg",      "players":["Mandar Jadhav","Suyash Dhotre","Aakash Kamble (Matkar)","Prasad Kadam","Rahul Shinde","Amol Kamble","Sujal Kamble","Kaustubh Sawant"]},
    "5A Challengers":   {"color":"#e65100","logo":"logo_Challengers.jpg",   "players":["Makrand Jadhav","Sushant Gamare","Shailesh Gopireddy","Sahil Kamble","Mandar Waydande","Shashank Kamble","Nayan Kamble","Vibhas Kamble"]},
}
team_names = list(TEAMS.keys())

# ── Schedule ──────────────────────────────────────────────────────────────────
def build_schedule():
    # Fixed schedule as per tournament organiser
    s = [
        {"match_no":1, "team1":"5A Strikers",      "team2":"5A Knight Riders", "stage":"League", "day":"4-Apr-2026","result":None,"winner":None},
        {"match_no":2, "team1":"5A Challengers",   "team2":"5A Warriors",       "stage":"League", "day":"4-Apr-2026","result":None,"winner":None},
        {"match_no":3, "team1":"5A Blasters",      "team2":"5A Strikers",       "stage":"League", "day":"4-Apr-2026","result":None,"winner":None},
        {"match_no":4, "team1":"5A Knight Riders", "team2":"5A Challengers",    "stage":"League", "day":"4-Apr-2026","result":None,"winner":None},
        {"match_no":5, "team1":"5A Warriors",      "team2":"5A Blasters",       "stage":"League", "day":"4-Apr-2026","result":None,"winner":None},
        {"match_no":6, "team1":"5A Strikers",      "team2":"5A Challengers",    "stage":"League", "day":"4-Apr-2026","result":None,"winner":None},
        {"match_no":7, "team1":"5A Knight Riders", "team2":"5A Warriors",       "stage":"League", "day":"4-Apr-2026","result":None,"winner":None},
        {"match_no":8, "team1":"5A Blasters",      "team2":"5A Challengers",    "stage":"League", "day":"5-Apr-2026","result":None,"winner":None},
        {"match_no":9, "team1":"5A Strikers",      "team2":"5A Warriors",       "stage":"League", "day":"5-Apr-2026","result":None,"winner":None},
        {"match_no":10,"team1":"5A Knight Riders", "team2":"5A Blasters",       "stage":"League", "day":"5-Apr-2026","result":None,"winner":None},
        {"match_no":11,"team1":"TBD",              "team2":"TBD",               "stage":"Qualifier","day":"5-Apr-2026","result":None,"winner":None},
        {"match_no":12,"team1":"TBD",              "team2":"TBD",               "stage":"FINAL",    "day":"5-Apr-2026","result":None,"winner":None},
    ]
    return s

# ── Photo helpers ─────────────────────────────────────────────────────────────
def pkey(name):
    return name.replace(" ","_").replace("(","").replace(")","").replace(".","").strip("_")

@st.cache_data
def get_b64(filename):
    # Try relative to app file first
    p = PHOTOS_DIR / filename
    if p.exists():
        with open(p,"rb") as f: return base64.b64encode(f.read()).decode()
    # Try absolute fallback paths for cloud
    for base in [Path("."), Path(__file__).parent, Path("/app/5apl")]:
        p2 = base / "photos" / filename
        if p2.exists():
            with open(p2,"rb") as f: return base64.b64encode(f.read()).decode()
    return None

def photo_img(name, size=115, border="#f9a825"):
    b = get_b64(f"{pkey(name)}.jpg")
    if b:
        return (f'<img src="data:image/jpeg;base64,{b}" style="border-radius:50%;width:{size}px;'
                f'height:{size}px;object-fit:cover;border:3px solid {border};display:block;margin:auto;">')
    ini = "".join([x[0] for x in name.split()[:2]])
    return (f'<div style="width:{size}px;height:{size}px;border-radius:50%;background:#2a2a3e;'
            f'display:flex;align-items:center;justify-content:center;font-size:{size//3}px;'
            f'font-weight:700;color:{border};border:3px solid {border};margin:auto;">{ini}</div>')

def logo_img(team, size=75):
    b = get_b64(TEAMS[team]["logo"])
    tc = TEAMS[team]["color"]
    if b:
        return (f'<img src="data:image/jpeg;base64,{b}" style="width:{size}px;height:{size}px;'
                f'object-fit:contain;border-radius:12px;'
                f'filter:drop-shadow(0 0 10px {tc}99);display:block;">')
    return f'<div style="width:{size}px;height:{size}px;background:#333;border-radius:12px;"></div>'

# ── State ─────────────────────────────────────────────────────────────────────
def blank_inn():
    return {"batting_team":"","bowling_team":"","score":0,"wickets":0,"balls":0,
            "batsmen":{"striker":{"name":"","runs":0,"balls":0,"fours":0,"sixes":0},
                       "non_striker":{"name":"","runs":0,"balls":0,"fours":0,"sixes":0}},
            "bowler":{"name":"","balls":0,"runs":0,"wickets":0},
            "fall_of_wickets":[],"ball_log":[],"bowling_card":{},"batting_card":{},
            "completed":False,"target":None}

def blank_state():
    return {"mode":"home","match_no":None,"innings":1,
            "inn1":blank_inn(),"inn2":blank_inn(),
            "toss_winner":"","schedule":build_schedule(),
            "points_table":{t:{"P":0,"W":0,"L":0,"T":0,"Pts":0,"RS":0,"RO":0.0,"RC":0,"RCO":0.0,"NRR":0.0} for t in team_names},
            "match_results":[]}

def migrate(s):
    if len(s.get("schedule",[])) not in [12]: s["schedule"] = build_schedule()
    if "match_results" not in s: s["match_results"]=[]
    for t in team_names:
        if t in s.get("points_table",{}):
            for key, default in [("T",0),("RS",0),("RO",0.0),("RC",0),("RCO",0.0),("NRR",0.0)]:
                if key not in s["points_table"][t]: s["points_table"][t][key]=default
    return s

def load_state():
    # Try Supabase cloud first
    s = cloud_load()
    if s: return migrate(s)
    # Fall back to local JSON
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE) as f: s=json.load(f)
            return migrate(s)
        except: pass
    return blank_state()

def save_state(s):
    cloud_save(s)  # Save to Supabase
    try:
        with open(STATE_FILE,"w") as f: json.dump(s,f,indent=2)  # Also local backup
    except: pass

def get_gs():
    if "gs" not in st.session_state: st.session_state.gs=load_state()
    return st.session_state.gs

def push():
    save_state(st.session_state.gs)

# ── Cricket Logic ─────────────────────────────────────────────────────────────
def ostr(balls): return f"{balls//6}.{balls%6}"
def crr(runs,balls): return round((runs/balls)*6,2) if balls>0 else 0.0
def rrr(target,runs,bl): return round(((target-runs)/bl)*6,2) if bl>0 and target>runs else 0.0
def is_over(inn): return inn["balls"]>=OVERS*6 or inn["wickets"]>=MAX_WICKETS
def chase_won(inn): return inn["target"] is not None and inn["score"]>=inn["target"]

def sync_card(inn):
    for pos in ["striker","non_striker"]:
        n=inn["batsmen"][pos]["name"]
        if n and n in inn["batting_card"]:
            inn["batting_card"][n].update({k:inn["batsmen"][pos][k] for k in ["runs","balls","fours","sixes"]})

def record_ball(inn, runs, extra=None, wicket=False):
    # extra: None | "wide" | "noball" | "bye" | "legbye"
    legal = extra not in ("wide","noball")
    bye_type = extra in ("bye","legbye")

    # Snapshot striker BEFORE any changes (for undo)
    striker_before = dict(inn["batsmen"]["striker"])

    inn["score"] += runs
    if extra in ("wide","noball"): inn["score"] += 1  # penalty run

    # Bowler charged: all runs except byes/legbyes (those are wicketkeeper/fielder fault)
    if not bye_type:
        inn["bowler"]["runs"] += runs + (1 if extra in ("wide","noball") else 0)

    if legal:
        inn["balls"] += 1
        inn["bowler"]["balls"] += 1
        if not wicket: inn["batsmen"]["striker"]["balls"] += 1

    if wicket and extra != "wide":
        inn["wickets"] += 1
        inn["bowler"]["wickets"] += 1
        inn["fall_of_wickets"].append({"wicket":inn["wickets"],"score":inn["score"],"overs":ostr(inn["balls"]),"batsman":inn["batsmen"]["striker"]["name"]})
        n = inn["batsmen"]["striker"]["name"]
        if n in inn["batting_card"]:
            inn["batting_card"][n]["out"] = True
        inn["batsmen"]["striker"] = {"name":"","runs":0,"balls":0,"fours":0,"sixes":0}
    elif not bye_type:
        # Normal runs go to batsman
        if extra not in ("wide",) and runs > 0:
            inn["batsmen"]["striker"]["runs"] += runs
            if runs == 4: inn["batsmen"]["striker"]["fours"] += 1

    # Rotate strike on odd runs (legal balls)
    if legal and not wicket and runs % 2 == 1:
        inn["batsmen"]["striker"],inn["batsmen"]["non_striker"] = inn["batsmen"]["non_striker"],inn["batsmen"]["striker"]

    # End of over
    if legal and inn["balls"] % 6 == 0 and inn["balls"] > 0:
        bn = inn["bowler"]["name"]
        if bn:
            if bn not in inn["bowling_card"]: inn["bowling_card"][bn]={"overs":0,"balls":0,"runs":0,"wickets":0}
            inn["bowling_card"][bn]["runs"] += inn["bowler"]["runs"]
            inn["bowling_card"][bn]["wickets"] += inn["bowler"]["wickets"]
            inn["bowling_card"][bn]["overs"] += 1
        inn["batsmen"]["striker"],inn["batsmen"]["non_striker"] = inn["batsmen"]["non_striker"],inn["batsmen"]["striker"]
        inn["bowler"] = {"name":"","balls":0,"runs":0,"wickets":0}

    inn["ball_log"].append({
        "runs": runs, "extra": extra, "wicket": wicket,
        "striker_snapshot": dict(striker_before) if wicket else None,
        "dismissal": inn["batting_card"].get(striker_before.get("name",""), {}).get("dismissal","") if wicket else None
    })
    sync_card(inn)

def undo_ball(inn):
    if not inn["ball_log"]: return False
    b = inn["ball_log"].pop()
    legal = b["extra"] not in ("wide","noball")

    # Reverse score
    inn["score"] -= b["runs"]
    if b["extra"] in ("wide","noball"): inn["score"] -= 1

    if legal:
        inn["balls"] = max(0, inn["balls"] - 1)

    if b["wicket"] and b["extra"] != "wide":
        # Reverse wicket counter
        inn["wickets"] = max(0, inn["wickets"] - 1)
        if inn["fall_of_wickets"]: inn["fall_of_wickets"].pop()

        # Restore original dismissed batsman as striker
        snap = b.get("striker_snapshot")
        if snap and snap.get("name"):
            dismissed_name = snap["name"]
            # Remove new batsman from batting card if they haven't faced a ball
            current_striker = inn["batsmen"]["striker"]["name"]
            if current_striker and current_striker != dismissed_name:
                # Only remove new batsman if they haven't scored/faced anything
                nb_data = inn["batting_card"].get(current_striker, {})
                if nb_data.get("balls", 0) == 0 and nb_data.get("runs", 0) == 0:
                    inn["batting_card"].pop(current_striker, None)
            # Restore dismissed batsman
            inn["batsmen"]["striker"] = snap
            # Restore their batting card entry as not out
            if dismissed_name in inn["batting_card"]:
                inn["batting_card"][dismissed_name]["out"] = False
                inn["batting_card"][dismissed_name]["dismissal"] = ""
        # Restore bowler wicket count
        if inn["bowler"]["name"]:
            inn["bowler"]["wickets"] = max(0, inn["bowler"]["wickets"] - 1)
    else:
        # Normal ball undo — reverse batsman stats
        if b["extra"] not in ("wide",):
            inn["batsmen"]["striker"]["balls"] = max(0, inn["batsmen"]["striker"]["balls"] - 1)
        if b["extra"] not in ("wide",) and not b["wicket"]:
            inn["batsmen"]["striker"]["runs"] = max(0, inn["batsmen"]["striker"]["runs"] - b["runs"])
            if b["runs"] == 4:
                inn["batsmen"]["striker"]["fours"] = max(0, inn["batsmen"]["striker"]["fours"] - 1)

    # Always reverse bowler stats for legal balls
    if legal:
        inn["bowler"]["balls"] = max(0, inn["bowler"]["balls"] - 1)
        if not b["wicket"]:
            bye_type = b["extra"] in ("bye","legbye")
            if not bye_type:
                inn["bowler"]["runs"] = max(0, inn["bowler"]["runs"] - b["runs"])
        if b["extra"] in ("wide","noball"):
            inn["bowler"]["runs"] = max(0, inn["bowler"]["runs"] - b["runs"] - 1)

    sync_card(inn)
    return True


# ── Awards & Stats Helpers ────────────────────────────────────────────────────
def impact_score(runs, balls, fours, sixes, wickets):
    """Impact score for MOM/MOT calculation"""
    bat = runs + (fours * 2) + (sixes * 4)
    sr_bonus = round((runs / balls) * 10, 1) if balls > 0 else 0
    bowl = wickets * 20
    return round(bat + sr_bonus + bowl, 1)

def get_player_match_stats(state, match_no):
    """Return dict of player -> {runs, balls, fours, sixes, wickets, impact} for a match"""
    i1 = state.get("_saved_inn1_" + str(match_no)) or {}
    i2 = state.get("_saved_inn2_" + str(match_no)) or {}
    stats = {}
    for inn_data in [i1, i2]:
        for p, d in inn_data.get("batting_card", {}).items():
            if p not in stats: stats[p] = {"team": inn_data.get("batting_team",""), "runs":0,"balls":0,"fours":0,"sixes":0,"wickets":0}
            stats[p]["runs"]  += d.get("runs", 0)
            stats[p]["balls"] += d.get("balls", 0)
            stats[p]["fours"] += d.get("fours", 0)
            stats[p]["sixes"] += d.get("sixes", 0)
        for p, d in inn_data.get("bowling_card", {}).items():
            if p not in stats: stats[p] = {"team": inn_data.get("bowling_team",""), "runs":0,"balls":0,"fours":0,"sixes":0,"wickets":0}
            stats[p]["wickets"] += d.get("wickets", 0)
    for p in stats:
        d = stats[p]
        stats[p]["impact"] = impact_score(d["runs"], d["balls"], d["fours"], d["sixes"], d["wickets"])
    return stats

def get_awards(state):
    """Compute MOM per match, top scorer, top wicket taker, MOT"""
    mom_list = []
    agg_bat = {}   # player -> total runs
    agg_bowl = {}  # player -> total wickets
    agg_impact = {}  # player -> total impact

    seen_matches = set()
    for mr in state.get("match_results", []):
        mn = mr.get("Match No","")
        if mn in seen_matches: continue  # Skip duplicate match entries
        seen_matches.add(mn)
        stage = mr.get("Stage","League")
        pstats = get_player_match_stats(state, mn)
        if not pstats: continue
        # MOM = highest impact
        mom_player = max(pstats, key=lambda p: pstats[p]["impact"])
        d = pstats[mom_player]
        mom_list.append({
            "Match No": mn, "Stage": stage,
            "Teams": f"{mr.get('Team 1','')} vs {mr.get('Team 2','')}",
            "Man of the Match": mom_player, "Team": d["team"],
            "Runs": d["runs"], "Balls": d["balls"],
            "4s": d["fours"], "6s": d["sixes"], "Wickets": d["wickets"],
            "Impact Score": d["impact"],
            "How Calculated": f"Runs({d['runs']}) + 4s×2({d['fours']*2}) + 6s×4({d['sixes']*4}) + SR bonus + Wkts×20({d['wickets']*20}) = {d['impact']}"
        })
        # Accumulate for tournament awards
        for p, d in pstats.items():
            agg_bat[p]    = agg_bat.get(p, {"team":d["team"],"runs":0})
            agg_bat[p]["runs"] += d["runs"]
            agg_bat[p]["team"] = d["team"]
            agg_bowl[p]   = agg_bowl.get(p, {"team":d["team"],"wickets":0})
            agg_bowl[p]["wickets"] += d["wickets"]
            agg_bowl[p]["team"] = d["team"]
            agg_impact[p] = agg_impact.get(p, {"team":d["team"],"impact":0.0})
            agg_impact[p]["impact"] += d["impact"]
            agg_impact[p]["team"] = d["team"]

    top_scorer = max(agg_bat.items(), key=lambda x: x[1]["runs"]) if agg_bat else None
    top_wicket = max(agg_bowl.items(), key=lambda x: x[1]["wickets"]) if agg_bowl else None
    mot        = max(agg_impact.items(), key=lambda x: x[1]["impact"]) if agg_impact else None

    return mom_list, top_scorer, top_wicket, mot, agg_bat, agg_bowl, agg_impact

# ── Excel Export ──────────────────────────────────────────────────────────────
def export_excel(state):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:

        # Sheet 1: Points Table
        pt = state["points_table"]
        pt_rows = sorted(pt.items(), key=lambda x: (-x[1]["Pts"], -x[1].get("NRR",0), -x[1]["W"]))
        pd.DataFrame([{"Rank": i+1, "Team": t, "P": d["P"], "W": d["W"], "L": d["L"], "T": d["T"], "Pts": d["Pts"], "NRR": round(d.get("NRR",0.0),3)}
                      for i, (t, d) in enumerate(pt_rows)]).to_excel(w, sheet_name="Points Table", index=False)

        # Sheet 2: Match Summary
        if state.get("match_results"):
            pd.DataFrame(state["match_results"]).to_excel(w, sheet_name="Match Summary", index=False)

        # Sheet 3: Schedule
        pd.DataFrame([{"Match": m["match_no"], "Stage": m.get("stage", "League"),
                        "Team 1": m["team1"], "Team 2": m["team2"],
                        "Result": m["result"] or "Pending", "Winner": m.get("winner") or "-"}
                      for m in state["schedule"]]).to_excel(w, sheet_name="Schedule", index=False)

        # Sheets 4 & 5: Batting & Bowling Scorecards per match
        bat_rows = []
        bowl_rows = []
        bat_agg = {}
        bowl_agg = {}

        for mr in state.get("match_results", []):
            mn = mr.get("Match No", "")
            stage = mr.get("Stage", "League")
            inn1_key = "_saved_inn1_" + str(mn)
            inn2_key = "_saved_inn2_" + str(mn)
            i1 = state.get(inn1_key) or {}
            i2 = state.get(inn2_key) or {}

            for inn_label, inn_data in [("Inn 1", i1), ("Inn 2", i2)]:
                if not inn_data: continue
                # Batting card
                for pname, pd_data in inn_data.get("batting_card", {}).items():
                    balls = pd_data.get("balls", 0)
                    runs = pd_data.get("runs", 0)
                    sr = round((runs / balls) * 100, 1) if balls > 0 else 0
                    row = {"Match No": mn, "Stage": stage, "Innings": inn_label,
                           "Team": inn_data.get("batting_team", ""), "Batsman": pname,
                           "Runs": runs, "Balls": balls, "4s": pd_data.get("fours", 0),
                           "6s": pd_data.get("sixes", 0), "Strike Rate": sr,
                           "Status": "Out" if pd_data.get("out") else "Not Out"}
                    bat_rows.append(row)
                    # Aggregate
                    if pname not in bat_agg:
                        bat_agg[pname] = {"Team": inn_data.get("batting_team",""), "Inn": 0, "Runs": 0, "Balls": 0, "4s": 0, "6s": 0, "Outs": 0, "HS": 0}
                    bat_agg[pname]["Inn"] += 1
                    bat_agg[pname]["Runs"] += runs
                    bat_agg[pname]["Balls"] += balls
                    bat_agg[pname]["4s"] += pd_data.get("fours", 0)
                    bat_agg[pname]["6s"] += pd_data.get("sixes", 0)
                    if pd_data.get("out"): bat_agg[pname]["Outs"] += 1
                    bat_agg[pname]["HS"] = max(bat_agg[pname]["HS"], runs)

                # Bowling card
                for pname, bd in inn_data.get("bowling_card", {}).items():
                    overs = bd.get("overs", 0)
                    runs_b = bd.get("runs", 0)
                    wkts = bd.get("wickets", 0)
                    balls_b = overs * 6
                    econ = round((runs_b / balls_b) * 6, 2) if balls_b > 0 else 0
                    row = {"Match No": mn, "Stage": stage, "Innings": inn_label,
                           "Team": inn_data.get("bowling_team", ""), "Bowler": pname,
                           "Overs": overs, "Runs": runs_b, "Wickets": wkts, "Economy": econ}
                    bowl_rows.append(row)
                    if pname not in bowl_agg:
                        bowl_agg[pname] = {"Team": inn_data.get("bowling_team",""), "Overs": 0, "Runs": 0, "Wickets": 0}
                    bowl_agg[pname]["Overs"] += overs
                    bowl_agg[pname]["Runs"] += runs_b
                    bowl_agg[pname]["Wickets"] += wkts

        if bat_rows:
            pd.DataFrame(bat_rows).to_excel(w, sheet_name="Batting Scorecards", index=False)
        if bowl_rows:
            pd.DataFrame(bowl_rows).to_excel(w, sheet_name="Bowling Scorecards", index=False)

        # Sheet 6 & 7: Tournament Aggregates
        if bat_agg:
            bat_final = []
            for p, d in sorted(bat_agg.items(), key=lambda x: -x[1]["Runs"]):
                avg = round(d["Runs"] / d["Outs"], 2) if d["Outs"] > 0 else d["Runs"]
                sr = round((d["Runs"] / d["Balls"]) * 100, 1) if d["Balls"] > 0 else 0
                bat_final.append({"Player": p, "Team": d["Team"], "Inn": d["Inn"],
                                   "Runs": d["Runs"], "Balls": d["Balls"], "HS": d["HS"],
                                   "Avg": avg, "SR": sr, "4s": d["4s"], "6s": d["6s"]})
            pd.DataFrame(bat_final).to_excel(w, sheet_name="Batting Aggregates", index=False)

        if bowl_agg:
            bowl_final = []
            for p, d in sorted(bowl_agg.items(), key=lambda x: -x[1]["Wickets"]):
                balls_b = d["Overs"] * 6
                econ = round((d["Runs"] / balls_b) * 6, 2) if balls_b > 0 else 0
                bowl_final.append({"Player": p, "Team": d["Team"], "Overs": d["Overs"],
                                    "Runs": d["Runs"], "Wickets": d["Wickets"], "Economy": econ})
            pd.DataFrame(bowl_final).to_excel(w, sheet_name="Bowling Aggregates", index=False)

        # Sheet: Man of the Match (per match)
        mom_list, top_scorer, top_wicket, mot, agg_bat_aw, agg_bowl_aw, agg_impact_aw = get_awards(state)
        if mom_list:
            pd.DataFrame(mom_list).to_excel(w, sheet_name="Man of the Match", index=False)

        # Sheet: Tournament Awards (top scorer, top wicket, MOT)
        award_rows = []
        if top_scorer:
            award_rows.append({"Award":"🏆 Most Runs","Player":top_scorer[0],"Team":top_scorer[1]["team"],"Value":top_scorer[1]["runs"],"Unit":"Runs"})
        if top_wicket:
            award_rows.append({"Award":"🎳 Most Wickets","Player":top_wicket[0],"Team":top_wicket[1]["team"],"Value":top_wicket[1]["wickets"],"Unit":"Wickets"})
        if mot:
            award_rows.append({"Award":"⭐ Man of the Tournament","Player":mot[0],"Team":mot[1]["team"],"Value":mot[1]["impact"],"Unit":"Impact Score"})
        if award_rows:
            pd.DataFrame(award_rows).to_excel(w, sheet_name="Tournament Awards", index=False)

        # Sheet: Match-wise Scorecards (one match per section, sorted by match)
        mw_rows = []
        for mr in state.get("match_results", []):
            mn = mr.get("Match No","")
            i1d = state.get("_saved_inn1_"+str(mn)) or {}
            i2d = state.get("_saved_inn2_"+str(mn)) or {}
            for inn_label, inn_data in [("Inn 1", i1d), ("Inn 2", i2d)]:
                if not inn_data: continue
                for pname, pd_data in inn_data.get("batting_card", {}).items():
                    mw_rows.append({
                        "Match No": mn, "Stage": mr.get("Stage","League"),
                        "Match": f"{mr.get('Team 1','')} vs {mr.get('Team 2','')}",
                        "Innings": inn_label, "Type": "Batting",
                        "Team": inn_data.get("batting_team",""), "Player": pname,
                        "Runs": pd_data.get("runs",0), "Balls": pd_data.get("balls",0),
                        "4s": pd_data.get("fours",0), "6s": pd_data.get("sixes",0),
                        "SR": round((pd_data["runs"]/pd_data["balls"])*100,1) if pd_data.get("balls",0)>0 else 0,
                        "Status": "Out" if pd_data.get("out") else "Not Out",
                        "Overs":"","Wickets":"","Economy":""
                    })
                for pname, bd in inn_data.get("bowling_card", {}).items():
                    balls_b = bd.get("overs",0)*6
                    mw_rows.append({
                        "Match No": mn, "Stage": mr.get("Stage","League"),
                        "Match": f"{mr.get('Team 1','')} vs {mr.get('Team 2','')}",
                        "Innings": inn_label, "Type": "Bowling",
                        "Team": inn_data.get("bowling_team",""), "Player": pname,
                        "Runs": bd.get("runs",0), "Balls":"",
                        "4s":"","6s":"",
                        "SR":"","Status":"",
                        "Overs": bd.get("overs",0),
                        "Wickets": bd.get("wickets",0),
                        "Economy": round((bd["runs"]/balls_b)*6,2) if balls_b>0 else 0
                    })
        if mw_rows:
            pd.DataFrame(mw_rows).to_excel(w, sheet_name="Match-wise Scorecards", index=False)

    buf.seek(0)
    return buf

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Rajdhani:wght@500;700&display=swap');
html,body,[data-testid="stAppViewContainer"]{background:#0a0a0f !important;color:#f0f0f0;}
[data-testid="stSidebar"]{display:none;}
.hdr{background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);border:2px solid #f9a825;border-radius:16px;
  padding:20px 30px;text-align:center;margin-bottom:20px;box-shadow:0 0 40px rgba(249,168,37,.3);}
.hdr h1{font-family:'Bebas Neue',sans-serif;font-size:3rem;color:#f9a825;margin:0;letter-spacing:4px;
  text-shadow:0 0 20px rgba(249,168,37,.5);}
.hdr p{color:#aaa;margin:4px 0 0;font-family:'Rajdhani',sans-serif;font-size:1.1rem;letter-spacing:2px;}
.pc{background:linear-gradient(135deg,#1a1a2e,#0d1b2a);border:1px solid #2a2a4a;border-radius:14px;padding:18px 12px;text-align:center;}
.pc .pn{font-family:'Rajdhani',sans-serif;font-weight:700;font-size:1.05rem;color:#f9a825;margin-top:10px;}
.pc .ps{font-family:'Rajdhani',sans-serif;font-size:1.4rem;color:#fff;margin:2px 0;}
.pc .pb{font-size:.78rem;color:#888;letter-spacing:1px;}
.bs{background:#f9a825;color:#000;font-size:.65rem;font-weight:700;padding:2px 8px;border-radius:4px;letter-spacing:1px;display:inline-block;margin-bottom:6px;}
.bns{background:#555;color:#fff;font-size:.65rem;font-weight:700;padding:2px 8px;border-radius:4px;letter-spacing:1px;display:inline-block;margin-bottom:6px;}
.bb{background:#e53935;color:#fff;font-size:.65rem;font-weight:700;padding:2px 8px;border-radius:4px;letter-spacing:1px;display:inline-block;margin-bottom:6px;}
.sb{background:#0d1b2a;border:1px solid #f9a82588;border-radius:12px;padding:14px 10px;text-align:center;height:100%;}
.sv{font-family:'Bebas Neue',sans-serif;font-size:2.2rem;color:#f9a825;}
.sl{font-size:.7rem;color:#888;letter-spacing:1px;margin-top:2px;}
.tb{background:linear-gradient(135deg,#b71c1c,#7f0000);border:2px solid #ff5252;border-radius:12px;padding:14px 10px;text-align:center;height:100%;}
.tv{font-family:'Bebas Neue',sans-serif;font-size:2.2rem;color:#fff;}
.ball{display:inline-block;min-width:34px;height:34px;border-radius:17px;text-align:center;line-height:34px;font-weight:700;font-size:.7rem;margin:2px;padding:0 6px;}
.b0{background:#222;color:#aaa;} .b1{background:#1b5e20;color:#fff;} .b2{background:#2e7d32;color:#fff;}
.b3{background:#388e3c;color:#fff;} .b4{background:#1565c0;color:#fff;} .b6{background:#7b1fa2;color:#fff;}
.bW{background:#c62828;color:#fff;} .bWd{background:#e65100;color:#fff;} .bNb{background:#f57f17;color:#000;}
.wbanner{background:linear-gradient(135deg,#1a237e,#283593);border:3px solid #f9a825;border-radius:20px;padding:32px;text-align:center;margin:16px 0;}
div[data-testid="column"]{padding:4px !important;}


</style>""", unsafe_allow_html=True)



# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: HOME
# ═══════════════════════════════════════════════════════════════════════════════
def page_home():
    s=get_gs()
    st.markdown('<div class="hdr"><h1>🏏 5A PREMIER LEAGUE 2026</h1><p>BOX CRICKET CHAMPIONSHIP · TANMAY CHASHAK</p></div>',unsafe_allow_html=True)
    c1,c2,c3=st.columns([2,1,1])
    with c1:
        if st.button("🏏  START / RESUME MATCH",use_container_width=True,type="primary"):
            s["mode"]="setup" if s["match_no"] is None else "live"; push(); st.rerun()
    with c2:
        if st.button("📊 TOURNAMENT TABLE",use_container_width=True):
            s["mode"]="tournament"; push(); st.rerun()
    with c3:
        buf=export_excel(s)
        st.download_button("📥 EXPORT EXCEL",buf,"5APL_2026.xlsx","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",use_container_width=True)

    st.markdown("<br>",unsafe_allow_html=True)
    cols=st.columns(5)
    for i,(tname,td) in enumerate(TEAMS.items()):
        with cols[i]:
            b=get_b64(td["logo"])
            if b:
                st.markdown(f'<div style="text-align:center"><img src="data:image/jpeg;base64,{b}" style="width:180px;height:180px;object-fit:contain;border-radius:16px;border:3px solid {td["color"]};filter:drop-shadow(0 0 12px {td["color"]}66);"></div>',unsafe_allow_html=True)
            st.markdown(f'<div style="font-family:Bebas Neue,sans-serif;font-size:.95rem;color:{td["color"]};text-align:center;margin:8px 0 14px;letter-spacing:2px;">{tname}</div>',unsafe_allow_html=True)
            for j in range(0,8,2):
                pc=st.columns(2)
                for k in range(2):
                    if j+k<8:
                        p=td["players"][j+k]
                        with pc[k]:
                            bp=get_b64(f"{pkey(p)}.jpg")
                            img_html=(f'<img src="data:image/jpeg;base64,{bp}" style="border-radius:50%;width:54px;height:54px;object-fit:cover;border:2px solid {td["color"]};display:block;margin:auto;">'
                                      if bp else
                                      f'<div style="width:54px;height:54px;border-radius:50%;background:#2a2a3e;display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:700;color:{td["color"]};border:2px solid {td["color"]};margin:auto;">{"".join([x[0] for x in p.split()[:2]])}</div>')
                            nm=p.split(); fn=nm[0]; ln=" ".join(nm[1:])
                            st.markdown(f'<div style="text-align:center;padding:6px 2px;">{img_html}<div style="font-family:Rajdhani,sans-serif;font-size:.72rem;color:#ddd;margin-top:5px;line-height:1.2;">{fn}<br>{ln}</div></div>',unsafe_allow_html=True)

    st.markdown("<br>",unsafe_allow_html=True)
    if st.button("🔄 RESET ALL DATA",use_container_width=True):
        st.session_state.gs=blank_state()
        cloud_clear()
        if STATE_FILE.exists(): STATE_FILE.unlink()
        st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: SETUP
# ═══════════════════════════════════════════════════════════════════════════════
def page_setup():
    s=get_gs()
    st.markdown('<div class="hdr"><h1>⚙️ MATCH SETUP</h1></div>',unsafe_allow_html=True)
    unplayed=[m for m in s["schedule"] if m["result"] is None]
    if not unplayed:
        st.success("All matches completed! 🏆")
        if st.button("🏠 Home"): s["mode"]="home"; push(); st.rerun()
        return
    labels=[f"Match {m['match_no']} [{m.get('stage','League')}]: {m['team1']} vs {m['team2']}" for m in unplayed]
    idx=st.selectbox("Choose match",range(len(labels)),format_func=lambda i:labels[i])
    chosen=unplayed[idx]
    t1,t2=chosen["team1"],chosen["team2"]
    if t1=="TBD" or t2=="TBD":
        st.info(f"**{chosen['stage']}** — select qualified teams")
        t1=st.selectbox("Team 1",team_names,key="ko1")
        t2=st.selectbox("Team 2",[t for t in team_names if t!=t1],key="ko2")
        chosen["team1"]=t1; chosen["team2"]=t2
    st.markdown(f"### {t1} 🆚 {t2}")
    col1,col2=st.columns(2)
    with col1: tw=st.selectbox("Toss Winner",[t1,t2])
    with col2: tc=st.selectbox("Elected to",["Bat","Bowl"])
    bat1=tw if tc=="Bat" else (t2 if tw==t1 else t1)
    bow1=t2 if bat1==t1 else t1
    st.info(f"**{bat1}** bats first · **{bow1}** bowls first")
    p1=st.selectbox("Striker",TEAMS[bat1]["players"],key="s1")
    p2=st.selectbox("Non-Striker",[p for p in TEAMS[bat1]["players"] if p!=p1],key="s2")
    b1=st.selectbox("Opening Bowler",TEAMS[bow1]["players"],key="b1")
    col1,col2=st.columns(2)
    with col1:
        if st.button("🏏 START MATCH",type="primary",use_container_width=True):
            s["match_no"]=chosen["match_no"]; s["innings"]=1
            inn=s["inn1"]
            inn["batting_team"]=bat1; inn["bowling_team"]=bow1
            inn["batsmen"]["striker"]["name"]=p1; inn["batsmen"]["non_striker"]["name"]=p2
            inn["bowler"]["name"]=b1
            inn["batting_card"][p1]={"name":p1,"runs":0,"balls":0,"fours":0,"sixes":0,"out":False}
            inn["batting_card"][p2]={"name":p2,"runs":0,"balls":0,"fours":0,"sixes":0,"out":False}
            s["mode"]="live"; push(); st.rerun()
    with col2:
        if st.button("🏠 Home",use_container_width=True): s["mode"]="home"; push(); st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: LIVE
# ═══════════════════════════════════════════════════════════════════════════════
def page_live():
    s=get_gs()
    ik="inn1" if s["innings"]==1 else "inn2"
    inn=s[ik]
    bt=inn["batting_team"]; bwt=inn["bowling_team"]
    tc=TEAMS[bt]["color"]

    # Chase win check
    if s["innings"]==2 and chase_won(inn):
        inn["completed"]=True
        page_result(s); return

    # Score header
    st.markdown(
        f'<div style="background:linear-gradient(135deg,#1a1a2e,#16213e);border:2px solid {tc};border-radius:16px;padding:16px 24px;margin-bottom:12px;">'
        f'<table style="width:100%;border-collapse:collapse;"><tr>'
        f'<td style="width:110px;vertical-align:middle;padding:8px;">{logo_img(bt,100)}</td>'
        f'<td style="text-align:center;vertical-align:middle;">'
        f'<div style="font-family:Bebas Neue,sans-serif;font-size:1.1rem;color:#aaa;letter-spacing:3px;">INNINGS {s["innings"]} · MATCH {s["match_no"]} · {OVERS} OVERS</div>'
        f'<div style="font-family:Bebas Neue,sans-serif;font-size:2.4rem;color:{tc};letter-spacing:2px;">{bt}</div>'
        f'<div style="font-family:Bebas Neue,sans-serif;font-size:5.5rem;color:#fff;line-height:1;text-shadow:0 0 30px {tc}88;">{inn["score"]}/{inn["wickets"]}</div>'
        f'<div style="font-family:Rajdhani,sans-serif;font-size:1.1rem;color:#aaa;letter-spacing:2px;">{ostr(inn["balls"])} Overs</div>'
        f'</td><td style="width:110px;vertical-align:middle;text-align:right;padding:8px;">{logo_img(bwt,100)}</td>'
        f'</tr></table></div>', unsafe_allow_html=True)

    # Stats row — all 4 boxes same height
    if s["innings"]==2 and inn.get("target"):
        tgt=inn["target"]; needed=max(0,tgt-inn["score"]); bl=max(0,OVERS*6-inn["balls"])
        c1,c2,c3,c4=st.columns(4)
        with c1: st.markdown(f'<div class="tb"><div style="font-size:.7rem;color:#ffcdd2;letter-spacing:2px;">TARGET</div><div class="tv">{tgt}</div></div>',unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="sb"><div class="sl">NEED</div><div class="sv">{needed}</div><div class="sl">{bl} BALLS LEFT</div></div>',unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="sb"><div class="sl">CRR</div><div class="sv">{crr(inn["score"],inn["balls"])}</div></div>',unsafe_allow_html=True)
        with c4: st.markdown(f'<div class="sb"><div class="sl">RRR</div><div class="sv" style="color:#ff5252">{rrr(tgt,inn["score"],bl)}</div></div>',unsafe_allow_html=True)
    else:
        bl=OVERS*6-inn["balls"]; proj=round(crr(inn["score"],inn["balls"])*OVERS,1) if inn["balls"]>0 else 0
        c1,c2,c3=st.columns(3)
        with c1: st.markdown(f'<div class="sb"><div class="sl">RUN RATE</div><div class="sv">{crr(inn["score"],inn["balls"])}</div></div>',unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="sb"><div class="sl">BALLS LEFT</div><div class="sv">{bl}</div></div>',unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="sb"><div class="sl">PROJECTED</div><div class="sv">{proj}</div></div>',unsafe_allow_html=True)

    st.markdown("<br>",unsafe_allow_html=True)

    # Player cards
    striker=inn["batsmen"]["striker"]; nstr=inn["batsmen"]["non_striker"]; bwlr=inn["bowler"]
    c1,c2,c3=st.columns(3)
    with c1:
        sr=round((striker["runs"]/striker["balls"])*100,1) if striker["balls"]>0 else 0
        st.markdown(f'<div class="pc"><div class="bs">🏏 ON STRIKE</div>{photo_img(striker["name"],120,tc)}<div class="pn">{striker["name"]}</div><div class="ps">{striker["runs"]} <span style="font-size:1rem;color:#aaa">({striker["balls"]}b)</span></div><div class="pb">4s:{striker["fours"]} · SR:{sr}</div></div>',unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="pc"><div class="bns">NON-STRIKER</div>{photo_img(nstr["name"],120,"#888")}<div class="pn">{nstr["name"]}</div><div class="ps">{nstr["runs"]} <span style="font-size:1rem;color:#aaa">({nstr["balls"]}b)</span></div><div class="pb">4s:{nstr["fours"]}</div></div>',unsafe_allow_html=True)
    with c3:
        ec=round((bwlr["runs"]/bwlr["balls"])*6,2) if bwlr["balls"]>0 else 0
        st.markdown(f'<div class="pc"><div class="bb">🎳 BOWLING</div>{photo_img(bwlr["name"],120,"#e53935")}<div class="pn">{bwlr["name"]}</div><div class="ps">{bwlr["wickets"]}/{bwlr["runs"]} <span style="font-size:1rem;color:#aaa">({ostr(bwlr["balls"])})</span></div><div class="pb">Economy:{ec}</div></div>',unsafe_allow_html=True)

    # Ball log chips
    if inn["ball_log"]:
        chips=""
        for b in inn["ball_log"][-36:]:
            if b["wicket"]: cls,lbl="bW","W"
            elif b["extra"]=="wide":
                cls="bWd"
                lbl=f"Wd+{b['runs']}" if b['runs']>0 else "Wd"
            elif b["extra"]=="noball":
                cls="bNb"
                lbl=f"NB+{b['runs']}" if b['runs']>0 else "NB"
            elif b["extra"]=="bye":
                cls="b1"; lbl=f"By{b['runs']}"
            elif b["extra"]=="legbye":
                cls="b1"; lbl=f"LB{b['runs']}"
            else:
                r=b["runs"]; cls=f"b{r}" if r in [0,1,2,3,4] else "b1"; lbl=str(r)
            chips+=f'<span class="ball {cls}">{lbl}</span>'
        st.markdown(f'<div style="text-align:center;padding:8px 0;">{chips}</div>',unsafe_allow_html=True)

    st.divider()

    # Innings over?
    if is_over(inn): page_end_innings(s,ik); return

    # Need new batsman?
    if striker["name"]=="":
        st.warning("🚨 Wicket! Select new batsman.")
        # Players already used = in batting_card AND (have faced balls OR are confirmed openers OR are out)
        # This prevents edge case where a player appears in card but never actually batted
        used = set()
        for pname, pdata in inn["batting_card"].items():
            # Count as used if: they faced at least 1 ball, OR they got out, OR they are the non-striker
            if (pdata.get("balls", 0) > 0 or 
                pdata.get("out", False) or 
                pname == inn["batsmen"]["non_striker"]["name"]):
                used.add(pname)
        # Always exclude current non-striker from new batsman selection
        used.add(inn["batsmen"]["non_striker"]["name"])
        avail = [p for p in TEAMS[bt]["players"] if p not in used]
        if not avail:
            st.error("All out! No more batsmen available.")
            page_end_innings(s,ik)
            return
        nb=st.selectbox("New Batsman",avail)
        if st.button("✅ Confirm",type="primary"):
            inn["batsmen"]["striker"]={"name":nb,"runs":0,"balls":0,"fours":0,"sixes":0}
            inn["batting_card"][nb]={"name":nb,"runs":0,"balls":0,"fours":0,"sixes":0,"out":False}
            push(); st.rerun()
        return

    # Need new bowler?
    if bwlr["name"]=="":
        st.warning("🎳 Select bowler for this over.")
        nb=st.selectbox("New Bowler",TEAMS[bwt]["players"])
        if st.button("✅ Confirm",type="primary"):
            inn["bowler"]={"name":nb,"balls":0,"runs":0,"wickets":0}
            if nb not in inn["bowling_card"]: inn["bowling_card"][nb]={"overs":0,"balls":0,"runs":0,"wickets":0}
            push(); st.rerun()
        return

    # Scorer Panel
    st.subheader("⌨️ Scorer Panel")
    # Run buttons (no 6 — Box Cricket)
    rcols = st.columns(6)
    for col,lbl,val in zip(rcols,["0","1","2","3","4 ✦","W 🎯"],[0,1,2,3,4,"W"]):
        with col:
            if st.button(lbl,use_container_width=True,key=f"r{val}"):
                if val=="W":
                    st.session_state["pending_wicket"] = True
                    st.session_state["striker_runs_before_out"] = inn["batsmen"]["striker"]["runs"]
                else:
                    if val==4:
                        record_ball(inn,4)
                    else:
                        record_ball(inn,val)
                push(); st.rerun()

    # Wicket type selection
    if st.session_state.get("pending_wicket"):
        st.markdown("#### 🎯 How did the batsman get out?")
        bowler_name = inn["bowler"]["name"]
        batting_team = inn["batting_team"]
        bowling_team = inn["bowling_team"]
        wc1,wc2,wc3,wc4 = st.columns(4)
        dismissal = None
        with wc1:
            if st.button("🏏 Bowled",use_container_width=True,key="wb"):
                dismissal = f"b {bowler_name}"
        with wc2:
            fielder = st.selectbox("Caught by",TEAMS[bowling_team]["players"],key="catch_by")
            if st.button("🤲 Caught",use_container_width=True,key="wc"):
                dismissal = f"c {fielder} b {bowler_name}"
        with wc3:
            ro_fielder = st.selectbox("Run Out by",TEAMS[bowling_team]["players"],key="ro_by")
            if st.button("🏃 Run Out",use_container_width=True,key="wro"):
                dismissal = f"run out ({ro_fielder})"
        with wc4:
            if st.button("🧱 Wall Out",use_container_width=True,key="wwall"):
                dismissal = "hit wall (out)"
        if dismissal:
            striker_runs = st.session_state.get("striker_runs_before_out", 0)
            # Store dismissal in batting card before recording
            sname = inn["batsmen"]["striker"]["name"]
            if sname in inn["batting_card"]:
                inn["batting_card"][sname]["dismissal"] = dismissal
            record_ball(inn, 0, wicket=True)
            st.session_state.pop("pending_wicket", None)
            st.session_state.pop("striker_runs_before_out", None)
            push(); st.rerun()
        if st.button("❌ Cancel Wicket",key="wcancel"):
            st.session_state.pop("pending_wicket", None)
            push(); st.rerun()
        st.stop()

    st.markdown("**Extras:**")
    # Wide: penalty(1) + runs between wickets. Wide+1 = just penalty (0 extra runs run).
    # Wide+2 = 1 run between wickets + 1 penalty = 2 total. etc.
    ec1 = st.columns(4)
    with ec1[0]:
        if st.button("Wide (1)",use_container_width=True,key="eW1",help="Wide ball only — 1 run penalty"):
            record_ball(inn,0,extra="wide"); push(); st.rerun()
    with ec1[1]:
        if st.button("Wide+run (2)",use_container_width=True,key="eW2",help="Wide + 1 run between wickets = 2 total"):
            record_ball(inn,1,extra="wide"); push(); st.rerun()
    with ec1[2]:
        if st.button("Wide+2runs (3)",use_container_width=True,key="eW3",help="Wide + 2 runs = 3 total"):
            record_ball(inn,2,extra="wide"); push(); st.rerun()
    with ec1[3]:
        if st.button("Wide+3runs (4)",use_container_width=True,key="eW4",help="Wide + 3 runs = 4 total"):
            record_ball(inn,3,extra="wide"); push(); st.rerun()

    ec2 = st.columns(5)
    with ec2[0]:
        if st.button("No Ball (1)",use_container_width=True,key="eNB1",help="No ball only — 1 run penalty"):
            record_ball(inn,0,extra="noball"); push(); st.rerun()
    with ec2[1]:
        if st.button("NB+run (2)",use_container_width=True,key="eNB2",help="No ball + 1 run = 2 total"):
            record_ball(inn,1,extra="noball"); push(); st.rerun()
    with ec2[2]:
        if st.button("NB+2runs (3)",use_container_width=True,key="eNB3",help="No ball + 2 runs = 3 total"):
            record_ball(inn,2,extra="noball"); push(); st.rerun()
    with ec2[3]:
        if st.button("NB+3runs (4)",use_container_width=True,key="eNB4",help="No ball + 3 runs = 4 total"):
            record_ball(inn,3,extra="noball"); push(); st.rerun()
    with ec2[4]:
        if st.button("NB+4runs (5)",use_container_width=True,key="eNB5",help="No ball + 4 runs = 5 total"):
            record_ball(inn,4,extra="noball"); push(); st.rerun()

    ec3 = st.columns(4)
    with ec3[0]:
        if st.button("Bye 1",use_container_width=True,key="eBye1",help="Bye — 1 run, not off bat"):
            record_ball(inn,1,extra="bye"); push(); st.rerun()
    with ec3[1]:
        if st.button("Bye 2",use_container_width=True,key="eBye2"):
            record_ball(inn,2,extra="bye"); push(); st.rerun()
    with ec3[2]:
        if st.button("Leg Bye 1",use_container_width=True,key="eLB1",help="Leg bye — 1 run off body"):
            record_ball(inn,1,extra="legbye"); push(); st.rerun()
    with ec3[3]:
        if st.button("Leg Bye 2",use_container_width=True,key="eLB2"):
            record_ball(inn,2,extra="legbye"); push(); st.rerun()

    if st.button("↩️ UNDO LAST BALL",use_container_width=True):
        if undo_ball(inn): st.toast("✅ Undone!")
        else: st.warning("Nothing to undo.")
        push(); st.rerun()

    with st.expander("🔄 Swap Strike / Change Bowler"):
        if st.button("Swap Striker ↔ Non-Striker"):
            inn["batsmen"]["striker"],inn["batsmen"]["non_striker"]=inn["batsmen"]["non_striker"],inn["batsmen"]["striker"]
            push(); st.rerun()
        nb=st.selectbox("Change Bowler",TEAMS[bwt]["players"],key="cbwl")
        if st.button("Set Bowler"):
            bn=inn["bowler"]["name"]
            if bn:
                if bn not in inn["bowling_card"]: inn["bowling_card"][bn]={"overs":0,"balls":0,"runs":0,"wickets":0}
                inn["bowling_card"][bn]["runs"]+=inn["bowler"]["runs"]
                inn["bowling_card"][bn]["wickets"]+=inn["bowler"]["wickets"]
            inn["bowler"]={"name":nb,"balls":0,"runs":0,"wickets":0}
            if nb not in inn["bowling_card"]: inn["bowling_card"][nb]={"overs":0,"balls":0,"runs":0,"wickets":0}
            push(); st.rerun()

    with st.expander("📋 Live Scorecard"):
        render_card(inn,bt,bwt)

    if st.button("🏠 Home",use_container_width=True):
        s["mode"]="home"; push(); st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# END INNINGS
# ═══════════════════════════════════════════════════════════════════════════════
def page_end_innings(s,ik):
    inn=s[ik]; bt=inn["batting_team"]; bwt=inn["bowling_team"]
    # Save current bowler's partial over to bowling_card before ending
    # Only save if bowler has bowled balls in this current (unsaved) spell
    cb = inn["bowler"]
    if cb.get("name") and cb["balls"] > 0:
        bn = cb["name"]
        if bn not in inn["bowling_card"]:
            inn["bowling_card"][bn] = {"overs":0,"balls":0,"runs":0,"wickets":0}
        # Only add what's in the CURRENT live spell — don't double count
        inn["bowling_card"][bn]["runs"]    += cb["runs"]
        inn["bowling_card"][bn]["wickets"] += cb["wickets"]
        inn["bowling_card"][bn]["balls"]    = inn["bowling_card"][bn].get("balls",0) + cb["balls"]
        # Clear bowler spell so it's not counted again
        inn["bowler"] = {"name":"","balls":0,"runs":0,"wickets":0}
    if s["innings"]==1:
        st.success(f"✅ Innings 1 done — {bt}: {inn['score']}/{inn['wickets']} in {ostr(inn['balls'])} overs")
        st.markdown(f"### 🎯 Target for {bwt}: **{inn['score']+1}**")
        render_card(inn,bt,bwt)
        st.subheader(f"Setup Innings 2 — {bwt} Batting")
        p1=st.selectbox("Striker",TEAMS[bwt]["players"],key="i2s")
        p2=st.selectbox("Non-Striker",[p for p in TEAMS[bwt]["players"] if p!=p1],key="i2n")
        b1=st.selectbox("Opening Bowler",TEAMS[bt]["players"],key="i2b")
        if st.button("▶ Start Innings 2",type="primary"):
            i2=s["inn2"]
            i2["batting_team"]=bwt; i2["bowling_team"]=bt; i2["target"]=inn["score"]+1
            i2["batsmen"]["striker"]["name"]=p1; i2["batsmen"]["non_striker"]["name"]=p2
            i2["bowler"]["name"]=b1
            i2["batting_card"][p1]={"name":p1,"runs":0,"balls":0,"fours":0,"sixes":0,"out":False}
            i2["batting_card"][p2]={"name":p2,"runs":0,"balls":0,"fours":0,"sixes":0,"out":False}
            inn["completed"]=True; s["innings"]=2; push(); st.rerun()
    else:
        inn["completed"]=True; page_result(s)

# ═══════════════════════════════════════════════════════════════════════════════
# MATCH RESULT
# ═══════════════════════════════════════════════════════════════════════════════
def page_result(s):
    i1=s["inn1"]; i2=s["inn2"]
    t1=i1["batting_team"]; t2=i2["batting_team"]
    s1,s2=i1["score"],i2["score"]
    tgt=i2.get("target",s1+1)

    if s2>=tgt:   winner=t2; mg=f"{MAX_WICKETS-i2['wickets']} wickets"; rs=f"{t2} won by {mg}"
    elif s2==tgt-1: winner="TIE"; mg="Tie"; rs="Match Tied"
    else:          winner=t1; mg=f"{(tgt-1)-s2} run(s)"; rs=f"{t1} won by {mg}"

    # Update points once
    match=next((m for m in s["schedule"] if m["match_no"]==s["match_no"]),None)
    if match and match["result"] is None:
        match["result"]=rs; match["winner"]=winner
        pt=s["points_table"]
        for t in [t1,t2]:
            if t in pt: pt[t]["P"]+=1
        if winner=="TIE":
            for t in [t1,t2]:
                if t in pt: pt[t]["T"]+=1; pt[t]["Pts"]+=1
        else:
            if winner in pt: pt[winner]["W"]+=1; pt[winner]["Pts"]+=2
            loser=t2 if winner==t1 else t1
            if loser in pt: pt[loser]["L"]+=1

        # NRR: accumulate runs scored/conceded and overs faced/bowled
        def balls_to_overs(balls):
            full = balls // 6
            partial = balls % 6
            return full + partial/6.0

        o1 = balls_to_overs(i1["balls"]) or (OVERS)  # if all out, use full overs for NRR
        o2 = balls_to_overs(i2["balls"]) or (OVERS)

        # t1 batted inn1, bowled inn2
        if t1 in pt:
            pt[t1]["RS"]  += s1           # runs scored by t1
            pt[t1]["RO"]  += o1           # overs t1 faced
            pt[t1]["RC"]  += s2           # runs conceded by t1
            pt[t1]["RCO"] += o2           # overs t1 bowled
            nrr1 = round((pt[t1]["RS"]/pt[t1]["RO"]) - (pt[t1]["RC"]/pt[t1]["RCO"]), 3) if pt[t1]["RO"]>0 and pt[t1]["RCO"]>0 else 0.0
            pt[t1]["NRR"] = nrr1

        if t2 in pt:
            pt[t2]["RS"]  += s2
            pt[t2]["RO"]  += o2
            pt[t2]["RC"]  += s1
            pt[t2]["RCO"] += o1
            nrr2 = round((pt[t2]["RS"]/pt[t2]["RO"]) - (pt[t2]["RC"]/pt[t2]["RCO"]), 3) if pt[t2]["RO"]>0 and pt[t2]["RCO"]>0 else 0.0
            pt[t2]["NRR"] = nrr2
        import copy
        s["_saved_inn1_"+str(s["match_no"])] = copy.deepcopy(i1)
        s["_saved_inn2_"+str(s["match_no"])] = copy.deepcopy(i2)
        # Compute MOM
        pstats = get_player_match_stats(s, s["match_no"])
        mom_name = max(pstats, key=lambda p: pstats[p]["impact"]) if pstats else "-"
        mom_d = pstats.get(mom_name, {})
        s["match_results"].append({
            "Match No":s["match_no"],"Stage":match.get("stage","League"),
            "Team 1":t1,"Inn 1 Score":f"{s1}/{i1['wickets']}","Inn 1 Overs":ostr(i1["balls"]),
            "Team 2":t2,"Inn 2 Score":f"{s2}/{i2['wickets']}","Inn 2 Overs":ostr(i2["balls"]),
            "Winner":winner,"Result":rs,
            "Man of the Match":mom_name,
            "MOM Runs":mom_d.get("runs",0),"MOM Wickets":mom_d.get("wickets",0),
            "MOM Impact":mom_d.get("impact",0),
            "Date":datetime.now().strftime("%d-%m-%Y")
        })
        push()

    st.balloons()
    st.markdown(f"""<div class="wbanner">
        <div style="font-family:Bebas Neue,sans-serif;font-size:1.3rem;color:#aaa;letter-spacing:4px;">MATCH RESULT</div>
        <div style="font-family:Bebas Neue,sans-serif;font-size:3rem;color:#f9a825;letter-spacing:3px;">
            {'🏆 '+winner+' WIN!' if winner!='TIE' else '🤝 MATCH TIED'}</div>
        <div style="font-family:Rajdhani,sans-serif;font-size:1.5rem;color:#fff;margin-top:8px;">
            {t1}: {s1}/{i1['wickets']} &nbsp;|&nbsp; {t2}: {s2}/{i2['wickets']}</div>
        <div style="font-family:Rajdhani,sans-serif;font-size:1.1rem;color:#aaa;margin-top:4px;">{rs}</div>
    </div>""", unsafe_allow_html=True)

    c1,c2=st.columns(2)
    with c1: render_card(i1,t1,i1["bowling_team"])
    with c2: render_card(i2,t2,i2["bowling_team"])

    if st.button("🏠 Home & Next Match",type="primary",use_container_width=True):
        s["mode"]="home"; s["match_no"]=None; s["innings"]=1
        s["inn1"]=blank_inn(); s["inn2"]=blank_inn(); push(); st.rerun()

def render_card(inn,bt,bwt):
    st.markdown(f"#### 🏏 {bt} — Batting")
    rows=[]
    for n,d in inn["batting_card"].items():
        if d.get("out"):
            dismissal = d.get("dismissal","out")
            status = dismissal
        elif n == inn["batsmen"]["striker"]["name"]:
            status = "batting ★"
        elif n == inn["batsmen"]["non_striker"]["name"]:
            status = "not out"
        else:
            status = "DNB"
        sr=round((d["runs"]/d["balls"])*100,1) if d.get("balls",0)>0 else 0
        rows.append({"Batsman":n,"R":d["runs"],"B":d.get("balls",0),"4s":d.get("fours",0),"SR":sr,"Dismissal":status})
    if rows:
        # Render as HTML table for centre alignment on numeric columns
        bat_html = """<table style="width:100%;border-collapse:collapse;font-family:Rajdhani,sans-serif;font-size:0.9rem;">
        <thead><tr style="border-bottom:1px solid #333;">
          <th style="padding:8px;text-align:left;color:#aaa;">Batsman</th>
          <th style="padding:8px;text-align:center;color:#aaa;">R</th>
          <th style="padding:8px;text-align:center;color:#aaa;">B</th>
          <th style="padding:8px;text-align:center;color:#aaa;">4s</th>
          <th style="padding:8px;text-align:center;color:#aaa;">SR</th>
          <th style="padding:8px;text-align:left;color:#aaa;">Dismissal</th>
        </tr></thead><tbody>"""
        for row in rows:
            name_color = "#f9a825" if "batting" in str(row["Dismissal"]) else "#fff"
            bat_html += f"""<tr style="border-bottom:1px solid #1a1a2e;">
              <td style="padding:7px 8px;color:{name_color};font-weight:700;">{row["Batsman"]}</td>
              <td style="padding:7px 8px;text-align:center;color:#fff;font-weight:700;">{row["R"]}</td>
              <td style="padding:7px 8px;text-align:center;color:#ccc;">{row["B"]}</td>
              <td style="padding:7px 8px;text-align:center;color:#1565c0;font-weight:700;">{row["4s"]}</td>
              <td style="padding:7px 8px;text-align:center;color:#aaa;">{row["SR"]}</td>
              <td style="padding:7px 8px;color:#888;font-size:0.82rem;">{row["Dismissal"]}</td>
            </tr>"""
        bat_html += "</tbody></table>"
        st.markdown(bat_html, unsafe_allow_html=True)

    # Fall of wickets
    if inn.get("fall_of_wickets"):
        fow_str = "  ·  ".join([f"{f['score']}/{f['wicket']} ({f['batsman']}, {f['overs']} ov)" for f in inn["fall_of_wickets"]])
        st.markdown(f"<div style='font-size:.8rem;color:#888;padding:4px 0;'><b>Fall of Wickets:</b> {fow_str}</div>", unsafe_allow_html=True)

    st.markdown(f"#### 🎳 {bwt} — Bowling")
    brows=[]
    # Build combined bowling: saved overs + current in-progress spell
    combined = {}
    for n,d in inn["bowling_card"].items():
        # total_balls = completed overs * 6 + extra balls stored
        tb = d["overs"]*6 + d.get("balls",0)
        combined[n] = {"total_balls": tb, "runs": d["runs"], "wickets": d["wickets"]}
    # Add current bowler's live spell
    cb = inn["bowler"]
    if cb.get("name") and cb["balls"] > 0:
        cn = cb["name"]
        if cn in combined:
            combined[cn]["total_balls"] += cb["balls"]
            combined[cn]["runs"]        += cb["runs"]
            combined[cn]["wickets"]     += cb["wickets"]
        else:
            combined[cn] = {"total_balls": cb["balls"], "runs": cb["runs"], "wickets": cb["wickets"]}
    for n,d in combined.items():
        tb = d["total_balls"]
        overs_disp = ostr(tb)   # use ostr() = "overs.balls" correctly e.g 0.4 not 0.8
        ec = round((d["runs"] / tb) * 6, 2) if tb > 0 else 0.0
        brows.append({"Bowler": n, "O": overs_disp, "R": d["runs"], "W": d["wickets"], "Econ": ec})
    if brows:
        bowl_html = """<table style="width:100%;border-collapse:collapse;font-family:Rajdhani,sans-serif;font-size:0.9rem;">
        <thead><tr style="border-bottom:1px solid #333;">
          <th style="padding:8px;text-align:left;color:#aaa;">Bowler</th>
          <th style="padding:8px;text-align:center;color:#aaa;">O</th>
          <th style="padding:8px;text-align:center;color:#aaa;">R</th>
          <th style="padding:8px;text-align:center;color:#aaa;">W</th>
          <th style="padding:8px;text-align:center;color:#aaa;">Econ</th>
        </tr></thead><tbody>"""
        for row in brows:
            w_color = "#4caf50" if row["W"] > 0 else "#ccc"
            bowl_html += f"""<tr style="border-bottom:1px solid #1a1a2e;">
              <td style="padding:7px 8px;color:#fff;font-weight:700;">{row["Bowler"]}</td>
              <td style="padding:7px 8px;text-align:center;color:#ccc;">{row["O"]}</td>
              <td style="padding:7px 8px;text-align:center;color:#ef5350;">{row["R"]}</td>
              <td style="padding:7px 8px;text-align:center;color:{w_color};font-weight:700;">{row["W"]}</td>
              <td style="padding:7px 8px;text-align:center;color:#aaa;">{row["Econ"]}</td>
            </tr>"""
        bowl_html += "</tbody></table>"
        st.markdown(bowl_html, unsafe_allow_html=True)
    else: st.caption("No bowling data yet")

# ═══════════════════════════════════════════════════════════════════════════════
# TOURNAMENT TABLE
# ═══════════════════════════════════════════════════════════════════════════════
def award_card(icon, title, player, team, value, unit, how=""):
    b = get_b64(f"{pkey(player)}.jpg") if player != "-" else None
    img = (f'<img src="data:image/jpeg;base64,{b}" style="border-radius:50%;width:80px;height:80px;object-fit:cover;border:3px solid #f9a825;display:block;margin:auto;">' if b
           else f'<div style="width:80px;height:80px;border-radius:50%;background:#2a2a3e;display:flex;align-items:center;justify-content:center;font-size:22px;font-weight:700;color:#f9a825;border:3px solid #f9a825;margin:auto;">{"".join([x[0] for x in player.split()[:2]])}</div>')
    how_html = ""  # Formula hidden from display
    return (f'<div style="background:linear-gradient(135deg,#1a1a2e,#0d1b2a);border:1px solid #f9a82566;'
            f'border-radius:14px;padding:18px 12px;text-align:center;">' 
            f'<div style="font-size:1.5rem;">{icon}</div>'
            f'<div style="font-family:Bebas Neue,sans-serif;font-size:.85rem;color:#aaa;letter-spacing:2px;margin-bottom:10px;">{title}</div>'
            f'{img}'
            f'<div style="font-family:Rajdhani,sans-serif;font-weight:700;font-size:1rem;color:#f9a825;margin-top:8px;">{player}</div>'
            f'<div style="font-size:.8rem;color:#888;">{team}</div>'
            f'<div style="font-family:Bebas Neue,sans-serif;font-size:1.8rem;color:#fff;">{value} <span style="font-size:.9rem;color:#aaa;">{unit}</span></div>'
            f'{how_html}</div>')

def page_tournament():
    s=get_gs()
    st.markdown('<div class="hdr"><h1>📊 TOURNAMENT TABLE</h1></div>',unsafe_allow_html=True)
    buf=export_excel(s)
    st.download_button("📥 Export Full Stats to Excel",buf,"5APL_2026.xlsx","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # ── Points Table ──────────────────────────────────────────────────────────
    st.markdown("### 🏆 Points Table")
    pt=s["points_table"]
    rows=sorted(pt.items(),key=lambda x:(-x[1]["Pts"],-x[1].get("NRR",0),-x[1]["W"]))
    medals=["🥇","🥈","🥉","4️⃣","5️⃣"]
    # Build points table as styled HTML for full control over alignment
    pt_html = """
    <table style="width:100%;border-collapse:collapse;font-family:Rajdhani,sans-serif;font-size:0.95rem;">
    <thead>
      <tr style="background:#1a1a2e;border-bottom:2px solid #f9a825;">
        <th style="padding:10px 8px;text-align:left;color:#f9a825;">#</th>
        <th style="padding:10px 8px;text-align:left;color:#f9a825;">Team</th>
        <th style="padding:10px 8px;text-align:center;color:#f9a825;">Played</th>
        <th style="padding:10px 8px;text-align:center;color:#f9a825;">Won</th>
        <th style="padding:10px 8px;text-align:center;color:#f9a825;">Lost</th>
        <th style="padding:10px 8px;text-align:center;color:#f9a825;">Tied</th>
        <th style="padding:10px 8px;text-align:center;color:#f9a825;">Points</th>
        <th style="padding:10px 8px;text-align:center;color:#f9a825;">NRR</th>
      </tr>
    </thead><tbody>"""
    for i,(t,d) in enumerate(rows):
        medal = medals[i]
        bg = "#1a2a1a" if i < 2 else "#0f0f1a"
        nrr = round(d.get("NRR",0.0),3)
        nrr_color = "#4caf50" if nrr > 0 else "#ef5350" if nrr < 0 else "#aaa"
        nrr_str = f"+{nrr}" if nrr > 0 else str(nrr)
        pt_html += f"""
        <tr style="background:{bg};border-bottom:1px solid #222;">
          <td style="padding:10px 8px;text-align:left;">{medal}</td>
          <td style="padding:10px 8px;text-align:left;font-weight:700;color:#fff;">{t}</td>
          <td style="padding:10px 8px;text-align:center;color:#ccc;">{d["P"]}</td>
          <td style="padding:10px 8px;text-align:center;color:#4caf50;font-weight:700;">{d["W"]}</td>
          <td style="padding:10px 8px;text-align:center;color:#ef5350;">{d["L"]}</td>
          <td style="padding:10px 8px;text-align:center;color:#aaa;">{d["T"]}</td>
          <td style="padding:10px 8px;text-align:center;color:#f9a825;font-weight:700;font-size:1.1rem;">{d["Pts"]}</td>
          <td style="padding:10px 8px;text-align:center;color:{nrr_color};font-weight:700;">{nrr_str}</td>
        </tr>"""
    pt_html += "</tbody></table>"
    st.markdown(pt_html, unsafe_allow_html=True)

    # ── Tournament Awards ─────────────────────────────────────────────────────
    mom_list, top_scorer, top_wicket, mot, agg_bat_aw, agg_bowl_aw, agg_impact_aw = get_awards(s)

    if mom_list or top_scorer or top_wicket or mot:
        st.markdown("---")
        st.markdown("### 🏅 Tournament Awards")

        c1,c2,c3=st.columns(3)
        if top_scorer:
            with c1:
                ts_runs = top_scorer[1]["runs"]
                st.markdown(award_card("🏏","MOST RUNS",top_scorer[0],top_scorer[1]["team"],ts_runs,"Runs"),unsafe_allow_html=True)
        if top_wicket:
            with c2:
                tw_wkts = top_wicket[1]["wickets"]
                st.markdown(award_card("🎳","MOST WICKETS",top_wicket[0],top_wicket[1]["team"],tw_wkts,"Wickets"),unsafe_allow_html=True)
        if mot:
            with c3:
                mot_imp = round(mot[1]["impact"],1)
                how_txt = "Impact = Runs + 4s×2 + 6s×4 + SR÷10 + Wickets×20"
                st.markdown(award_card("⭐","MAN OF THE TOURNAMENT",mot[0],mot[1]["team"],mot_imp,"Impact",how_txt),unsafe_allow_html=True)

        # ── Man of the Match history ──────────────────────────────────────────
        if mom_list:
            st.markdown("---")
            st.markdown("### 🌟 Man of the Match — Match History")
            st.markdown('<div style="font-size:.75rem;color:#888;margin-bottom:8px;">Impact Score = Runs + 4s×2 + 6s×4 + SR÷10 + Wickets×20 &nbsp;|&nbsp; Highest Impact wins MOM</div>',unsafe_allow_html=True)
            for m in mom_list:
                bp = get_b64(f'{pkey(m["Man of the Match"])}.jpg')
                img_s = (f'<img src="data:image/jpeg;base64,{bp}" style="border-radius:50%;width:44px;height:44px;object-fit:cover;border:2px solid #f9a825;vertical-align:middle;margin-right:10px;">' if bp
                         else f'<span style="display:inline-block;width:44px;height:44px;border-radius:50%;background:#2a2a3e;border:2px solid #f9a825;text-align:center;line-height:44px;font-size:12px;font-weight:700;color:#f9a825;vertical-align:middle;margin-right:10px;">{"".join([x[0] for x in m["Man of the Match"].split()[:2]])}</span>')
                st.markdown(
                    f'<div style="background:#1a1a2e;border:1px solid #333;border-radius:10px;padding:10px 16px;margin:4px 0;font-family:Rajdhani,sans-serif;display:flex;align-items:center;gap:8px;">' 
                    f'<span style="color:#aaa;min-width:28px;font-weight:700;">M{m["Match No"]}</span>'
                    f'<span style="color:#555;font-size:.8rem;min-width:70px;">{m["Stage"]}</span>'
                    f'<span style="color:#888;flex:1;font-size:.85rem;">{m["Teams"]}</span>'
                    f'{img_s}'
                    f'<span style="font-weight:700;color:#f9a825;min-width:160px;">{m["Man of the Match"]}</span>'
                    f'<span style="color:#aaa;font-size:.8rem;min-width:160px;">🏏{m["Runs"]}({m["Balls"]}b) 🎳{m["Wickets"]}wkts</span>'
                    f'<span style="background:#f9a82522;color:#f9a825;border-radius:6px;padding:2px 8px;font-size:.8rem;min-width:60px;text-align:center;">⚡{m["Impact Score"]}</span>'
                    f'</div>', unsafe_allow_html=True)

    # ── Knockout auto-fill ────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🏟️ Knockout Stage")
    league_done=all(m["result"] is not None for m in s["schedule"] if m.get("stage","League")=="League")
    if league_done:
        ranked=[t for t,_ in sorted(pt.items(),key=lambda x:(-x[1]["Pts"],-x[1].get("NRR",0),-x[1]["W"]))]
        t1r,t2r,t3r = ranked[0],ranked[1],ranked[2]
        st.success(f"🏆 **Direct Finalist:** {t1r}  |  ⚡ **Qualifier:** {t2r} vs {t3r} (winner faces {t1r} in Final)")
        for m in s["schedule"]:
            if m["match_no"]==11 and m["team1"]=="TBD": m["team1"]=t2r; m["team2"]=t3r
            elif m["match_no"]==12 and m["team1"]=="TBD": m["team1"]=t1r; m["team2"]="Qualifier Winner"
        push()
    else:
        rem=sum(1 for m in s["schedule"] if m.get("stage","League")=="League" and not m["result"])
        st.warning(f"{rem} league match(es) remaining before knockouts unlock.")

    st.markdown("---")
    st.markdown("### 📅 Full Schedule (13 Matches)")
    for stage in ["League","Qualifier","FINAL"]:
        sm=[m for m in s["schedule"] if m.get("stage","League")==stage]
        if not sm: continue
        label={"League":"🏏 League Stage (10 Matches)","Qualifier":"⚡ Qualifier","FINAL":"🏆 FINAL"}.get(stage,stage)
        st.markdown(f"**{label}**")
        for m in sm:
            res=m["result"] or "🕐 Upcoming"; rc="#4caf50" if m["result"] else "#888"; bg="#1a2a1a" if m["result"] else "#1a1a2e"
            day=m.get("day","")
            mom_info=""
            if m["result"]:
                for mr in s.get("match_results",[]):
                    if mr.get("Match No")==m["match_no"]:
                        mom_info=f' &nbsp;·&nbsp; <span style="color:#f9a825;">⭐ {mr.get("Man of the Match","")}</span>'
                        break
            st.markdown(
                f'<div style="background:{bg};border:1px solid #333;border-radius:8px;padding:10px 16px;margin:3px 0;font-family:Rajdhani,sans-serif;display:flex;align-items:center;gap:12px;">' 
                f'<span style="color:#666;min-width:24px;font-weight:700;font-size:.85rem;">M{m["match_no"]}</span>'
                f'<span style="color:#555;font-size:.78rem;min-width:90px;">{day}</span>'
                f'<span style="color:#fff;font-weight:700;flex:1;">{m["team1"]} <span style="color:#f9a825;">vs</span> {m["team2"]}{mom_info}</span>'
                f'<span style="color:{rc};min-width:80px;text-align:right;">{res}</span></div>', unsafe_allow_html=True)

    if st.button("🏠 Home",use_container_width=True): s["mode"]="home"; push(); st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ═══════════════════════════════════════════════════════════════════════════════
s=get_gs()
m=s.get("mode","home")
if   m=="home":       page_home()
elif m=="setup":      page_setup()
elif m=="live":       page_live()
elif m=="tournament": page_tournament()