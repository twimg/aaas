from nicegui import ui
import random
import json
from pathlib import Path

SAVE_FILE = Path("save.json")

# -------------------------
# 初期ゲームデータ
# -------------------------

def create_initial_state():
    return {
        "club": "Club Strive",
        "money": 1000000,
        "fans": 1200,
        "tactic": "Balanced",
        "players": [
            {"name": "Sato", "pos": "FW", "rating": 72, "stamina": 100},
            {"name": "Tanaka", "pos": "MF", "rating": 68, "stamina": 100},
            {"name": "Suzuki", "pos": "DF", "rating": 70, "stamina": 100},
        ],
        "league": [
            {"team": "Club Strive", "pts": 0, "played": 0},
            {"team": "Tokyo FC", "pts": 0, "played": 0},
            {"team": "Osaka United", "pts": 0, "played": 0},
            {"team": "Nagoya City", "pts": 0, "played": 0},
            {"team": "Sendai Blue", "pts": 0, "played": 0},
            {"team": "Kobe Wave", "pts": 0, "played": 0},
            {"team": "Sapporo North", "pts": 0, "played": 0},
            {"team": "Fukuoka Red", "pts": 0, "played": 0},
        ],
        "last_match": ""
    }

game_state = create_initial_state()

# -------------------------
# セーブ / ロード
# -------------------------

def save_game():
    with open(SAVE_FILE, "w") as f:
        json.dump(game_state, f)

def load_game():
    global game_state
    if SAVE_FILE.exists():
        with open(SAVE_FILE) as f:
            game_state = json.load(f)
        refresh_all()

def export_save():
    save_game()
    ui.download(SAVE_FILE)

def import_save(e):
    global game_state
    data = json.loads(e.content.read().decode())
    game_state = data
    refresh_all()

# -------------------------
# 試合シミュレーション
# -------------------------

def play_match():

    opponent = random.choice(
        [c["team"] for c in game_state["league"] if c["team"] != "Club Strive"]
    )

    team_strength = sum(p["rating"] for p in game_state["players"]) / len(game_state["players"])
    opp_strength = random.randint(60, 75)

    goals_for = max(0, int(random.gauss(team_strength/20, 1)))
    goals_against = max(0, int(random.gauss(opp_strength/20, 1)))

    result = ""

    if goals_for > goals_against:
        pts = 3
        result = "Win"
    elif goals_for == goals_against:
        pts = 1
        result = "Draw"
    else:
        pts = 0
        result = "Loss"

    for team in game_state["league"]:
        if team["team"] == "Club Strive":
            team["pts"] += pts
            team["played"] += 1

    game_state["money"] += random.randint(10000, 30000)
    game_state["fans"] += random.randint(5, 30)

    for p in game_state["players"]:
        p["stamina"] = max(0, p["stamina"] - random.randint(5, 15))

    game_state["last_match"] = f"{result} vs {opponent} ({goals_for}-{goals_against})"

    refresh_all()

# -------------------------
# UI 更新
# -------------------------

def refresh_all():
    money_label.set_text(f"Money: ${game_state['money']}")
    fan_label.set_text(f"Fans: {game_state['fans']}")
    match_label.set_text(game_state["last_match"])

    players_table.rows = game_state["players"]
    league_table.rows = game_state["league"]

# -------------------------
# UI
# -------------------------

ui.label("Club Strive Manager").classes("text-h5")

with ui.tabs() as tabs:
    tab_dashboard = ui.tab("Dashboard")
    tab_players = ui.tab("Players")
    tab_match = ui.tab("Match")
    tab_table = ui.tab("Standings")
    tab_save = ui.tab("Save")

with ui.tab_panels(tabs):

    with ui.tab_panel(tab_dashboard):
        money_label = ui.label()
        fan_label = ui.label()
        match_label = ui.label()

    with ui.tab_panel(tab_players):

        players_table = ui.table(
            columns=[
                {"name": "name", "label": "Name", "field": "name"},
                {"name": "pos", "label": "Position", "field": "pos"},
                {"name": "rating", "label": "Rating", "field": "rating"},
                {"name": "stamina", "label": "Stamina", "field": "stamina"},
            ],
            rows=[]
        )

    with ui.tab_panel(tab_match):

        ui.button("Play Match", on_click=play_match)

    with ui.tab_panel(tab_table):

        league_table = ui.table(
            columns=[
                {"name": "team", "label": "Team", "field": "team"},
                {"name": "played", "label": "Played", "field": "played"},
                {"name": "pts", "label": "Points", "field": "pts"},
            ],
            rows=[]
        )

    with ui.tab_panel(tab_save):

        ui.button("Save Game", on_click=save_game)
        ui.button("Load Game", on_click=load_game)
        ui.button("Export Save", on_click=export_save)
        ui.upload(on_upload=import_save, label="Import Save")

refresh_all()

ui.run(host="0.0.0.0", port=8080)
