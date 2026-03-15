from nicegui import ui
import json
import os
import random
from pathlib import Path

SAVE_FILE = Path('save.json')
PORT = int(os.getenv('PORT', '8080'))

APP_NAME = 'Club Strive'
TEAMS_PER_DIV = 10
DIVISIONS = 3
SQUAD_SIZE = 18
WEEKS_PER_SEASON = (TEAMS_PER_DIV - 1) * 2  # 18
MAX_SQUAD_SIZE = 24

COUNTRIES = {
    'England': {
        'club_prefix': ['North', 'East', 'West', 'South', 'Royal', 'River', 'Iron', 'Blue', 'Red', 'Green', 'King', 'Queen'],
        'club_suffix': ['FC', 'United', 'City', 'Rovers', 'Town', 'Athletic', 'Albion', 'Wanderers'],
        'first_names': ['Jack', 'Oliver', 'Harry', 'George', 'James', 'Noah', 'Leo', 'Charlie', 'Oscar', 'Alfie'],
        'last_names': ['Smith', 'Jones', 'Taylor', 'Brown', 'Wilson', 'Davies', 'Evans', 'Thomas', 'Johnson', 'Clark'],
        'bias': {'SPD': 1.00, 'PAS': 1.00, 'TEC': 0.98, 'DEF': 1.02, 'PHY': 1.06, 'SHT': 1.00, 'MEN': 1.03},
    },
    'Brazil': {
        'club_prefix': ['Real', 'Atletico', 'Nova', 'Santa', 'Porto', 'Rio', 'Samba', 'Verde', 'Sol', 'Cruzeiro'],
        'club_suffix': ['FC', 'SC', 'Clube', 'Athletic', 'United'],
        'first_names': ['Lucas', 'Joao', 'Mateus', 'Gabriel', 'Rafael', 'Pedro', 'Thiago', 'Bruno', 'Felipe', 'Diego'],
        'last_names': ['Silva', 'Souza', 'Costa', 'Santos', 'Oliveira', 'Pereira', 'Almeida', 'Gomes', 'Lima', 'Rocha'],
        'bias': {'SPD': 1.03, 'PAS': 1.03, 'TEC': 1.10, 'DEF': 0.95, 'PHY': 0.97, 'SHT': 1.02, 'MEN': 0.98},
    },
    'Germany': {
        'club_prefix': ['Berg', 'Union', 'Eintracht', 'Rot', 'Blau', 'Schwarz', 'Rhein', 'Bayern', 'Nord', 'Sud'],
        'club_suffix': ['FC', 'SV', 'SC', 'United', 'Athletic'],
        'first_names': ['Lukas', 'Jonas', 'Leon', 'Felix', 'Finn', 'Noah', 'Paul', 'Tim', 'Max', 'Moritz'],
        'last_names': ['Muller', 'Schmidt', 'Schneider', 'Fischer', 'Weber', 'Meyer', 'Wagner', 'Becker', 'Hoffmann', 'Koch'],
        'bias': {'SPD': 0.98, 'PAS': 1.01, 'TEC': 0.99, 'DEF': 1.05, 'PHY': 1.05, 'SHT': 0.99, 'MEN': 1.05},
    },
    'Spain': {
        'club_prefix': ['Real', 'Deportivo', 'Atletico', 'Costa', 'Roja', 'Azul', 'Valle', 'Montana', 'Sol', 'Mar'],
        'club_suffix': ['CF', 'FC', 'United', 'Athletic', 'Club'],
        'first_names': ['Hugo', 'Pablo', 'Alejandro', 'Diego', 'Javier', 'Alvaro', 'Daniel', 'Sergio', 'Ivan', 'Adrian'],
        'last_names': ['Garcia', 'Fernandez', 'Gonzalez', 'Rodriguez', 'Lopez', 'Martinez', 'Sanchez', 'Perez', 'Gomez', 'Martin'],
        'bias': {'SPD': 1.00, 'PAS': 1.08, 'TEC': 1.08, 'DEF': 0.97, 'PHY': 0.96, 'SHT': 1.01, 'MEN': 1.00},
    },
    'Italy': {
        'club_prefix': ['Real', 'Inter', 'Atletico', 'Roma', 'Torino', 'Milano', 'Lazio', 'Verona', 'Napoli', 'Fiora'],
        'club_suffix': ['FC', 'Calcio', 'United', 'SC', 'Club'],
        'first_names': ['Luca', 'Marco', 'Matteo', 'Andrea', 'Davide', 'Federico', 'Stefano', 'Giorgio', 'Antonio', 'Simone'],
        'last_names': ['Rossi', 'Russo', 'Ferrari', 'Esposito', 'Bianchi', 'Romano', 'Gallo', 'Costa', 'Fontana', 'Conti'],
        'bias': {'SPD': 0.97, 'PAS': 1.04, 'TEC': 1.03, 'DEF': 1.04, 'PHY': 0.98, 'SHT': 1.00, 'MEN': 1.03},
    },
    'Japan': {
        'club_prefix': ['Blue', 'Red', 'Shining', 'Phoenix', 'North', 'East', 'West', 'South', 'Rising', 'Ocean'],
        'club_suffix': ['FC', 'United', 'SC', 'Athletic', 'City'],
        'first_names': ['Haruto', 'Ren', 'Yuto', 'Sota', 'Kaito', 'Riku', 'Takumi', 'Daiki', 'Yuma', 'Shota'],
        'last_names': ['Sato', 'Suzuki', 'Takahashi', 'Tanaka', 'Ito', 'Yamamoto', 'Watanabe', 'Nakamura', 'Kobayashi', 'Kato'],
        'bias': {'SPD': 1.01, 'PAS': 1.02, 'TEC': 1.01, 'DEF': 0.98, 'PHY': 0.92, 'SHT': 0.98, 'MEN': 1.05},
    },
}

TACTICS = {
    'Balanced': {'atk': 1.00, 'def': 1.00, 'fatigue': 1.00},
    'Possession': {'atk': 1.03, 'def': 1.00, 'fatigue': 1.03},
    'Counter': {'atk': 1.05, 'def': 0.98, 'fatigue': 0.98},
    'Press': {'atk': 1.04, 'def': 1.03, 'fatigue': 1.08},
    'Low Block': {'atk': 0.96, 'def': 1.08, 'fatigue': 0.95},
}

POS_SEQUENCE = ['GK', 'DF', 'DF', 'DF', 'DF', 'MF', 'MF', 'MF', 'MF', 'FW', 'FW', 'GK', 'DF', 'DF', 'MF', 'MF', 'FW', 'FW']


def clamp(x, lo, hi):
    return lo if x < lo else hi if x > hi else x


def make_name(country_data):
    return f"{random.choice(country_data['first_names'])} {random.choice(country_data['last_names'])}"


def make_club_name(country_data, used_names):
    for _ in range(2000):
        name = f"{random.choice(country_data['club_prefix'])} {random.choice(country_data['club_suffix'])}"
        if name not in used_names:
            used_names.add(name)
            return name
    fallback = f"{random.choice(country_data['club_prefix'])} {random.choice(country_data['club_suffix'])} {random.randint(1,999)}"
    used_names.add(fallback)
    return fallback


def average_attrs(attrs):
    return round(sum(attrs.values()) / len(attrs))


def generate_player(country_name, club_name, idx):
    country_data = COUNTRIES[country_name]
    pos = POS_SEQUENCE[idx % len(POS_SEQUENCE)]
    age = random.randint(17, 33)

    if pos == 'GK':
        base = {'SPD': 52, 'PAS': 58, 'TEC': 55, 'DEF': 73, 'PHY': 68, 'SHT': 35, 'MEN': 66}
    elif pos == 'DF':
        base = {'SPD': 62, 'PAS': 58, 'TEC': 57, 'DEF': 70, 'PHY': 70, 'SHT': 48, 'MEN': 62}
    elif pos == 'MF':
        base = {'SPD': 64, 'PAS': 68, 'TEC': 68, 'DEF': 58, 'PHY': 62, 'SHT': 60, 'MEN': 64}
    else:
        base = {'SPD': 72, 'PAS': 60, 'TEC': 67, 'DEF': 42, 'PHY': 66, 'SHT': 72, 'MEN': 61}

    attrs = {}
    for k, v in base.items():
        bias = country_data['bias'][k]
        attrs[k] = clamp(int(random.randint(v - 8, v + 8) * bias), 35, 90)

    overall = average_attrs(attrs)
    potential = clamp(overall + random.randint(0, 15), overall, 94)
    value = int(overall * overall * 900 + potential * 2500 + random.randint(-10000, 10000))
    wage = int(overall * 85 + random.randint(200, 1200))

    return {
        'id': f'{club_name}_{idx}_{random.randint(1000, 9999)}',
        'name': make_name(country_data),
        'age': age,
        'nationality': country_name,
        'club': club_name,
        'pos': pos,
        'attrs': attrs,
        'overall': overall,
        'potential': potential,
        'stamina': random.randint(85, 100),
        'morale': random.randint(55, 75),
        'value': max(30000, value),
        'wage': max(800, wage),
        'transfer_listed': False,
    }


def create_team(country_name, club_name, division):
    base_rep = {1: 72, 2: 64, 3: 57}[division]
    players = [generate_player(country_name, club_name, i) for i in range(SQUAD_SIZE)]
    return {
        'name': club_name,
        'country': country_name,
        'division': division,
        'budget': random.randint(700_000, 1_600_000) * (4 - division),
        'fans': random.randint(3000, 18000) * (4 - division),
        'tactic': 'Balanced',
        'reputation': base_rep + random.randint(-4, 4),
        'players': players,
        'table': {'p': 0, 'w': 0, 'd': 0, 'l': 0, 'gf': 0, 'ga': 0, 'gd': 0, 'pts': 0},
    }


def round_robin_schedule(team_names):
    names = team_names[:]
    if len(names) % 2 != 0:
        names.append('BYE')

    rounds = []
    n = len(names)
    arr = names[:]

    for _ in range(n - 1):
        pairs = []
        for i in range(n // 2):
            a = arr[i]
            b = arr[n - 1 - i]
            if a != 'BYE' and b != 'BYE':
                pairs.append((a, b))
        rounds.append(pairs)
        arr = [arr[0]] + [arr[-1]] + arr[1:-1]

    second_half = [[(b, a) for (a, b) in rnd] for rnd in rounds]
    return rounds + second_half


def create_scout_pool(country_name, n=8):
    pool = []
    for i in range(n):
        player = generate_player(country_name, 'Scout Pool', i)
        player['value'] = int(player['value'] * random.uniform(0.8, 1.15))
        player['wage'] = int(player['wage'] * random.uniform(0.85, 1.1))
        pool.append(player)
    return pool


def build_world(selected_country):
    country_data = COUNTRIES[selected_country]
    used_names = set()
    divisions = {}

    for div in range(1, DIVISIONS + 1):
        teams = []
        for _ in range(TEAMS_PER_DIV):
            club_name = make_club_name(country_data, used_names)
            teams.append(create_team(selected_country, club_name, div))
        divisions[str(div)] = {
            'name': f'{selected_country} Division {div}',
            'teams': teams,
            'schedule': round_robin_schedule([t['name'] for t in teams]),
        }

    return {
        'season': 1,
        'week': 1,
        'selected_country': selected_country,
        'selected_club': '',
        'selected_player_id': '',
        'news': [f'Created new world in {selected_country}.'],
        'divisions': divisions,
        'scout_pool': create_scout_pool(selected_country, 10),
        'transfer_offers': [],
    }


def get_team(game_state, team_name):
    for div in game_state['divisions'].values():
        for team in div['teams']:
            if team['name'] == team_name:
                return team
    return None


def get_selected_team():
    if not game_state['selected_club']:
        return None
    return get_team(game_state, game_state['selected_club'])


def get_player_by_id(player_id):
    if not player_id:
        return None
    for div in game_state['divisions'].values():
        for team in div['teams']:
            for p in team['players']:
                if p['id'] == player_id:
                    return p
    for p in game_state.get('scout_pool', []):
        if p['id'] == player_id:
            return p
    return None


def team_strength(team):
    players = sorted(team['players'], key=lambda p: p['overall'], reverse=True)[:11]
    if not players:
        return 50.0

    base = sum(p['overall'] for p in players) / len(players)
    stamina = sum(p['stamina'] for p in players) / len(players)
    morale = sum(p['morale'] for p in players) / len(players)
    tactic = TACTICS.get(team['tactic'], TACTICS['Balanced'])

    strength = base
    strength *= (0.92 + (stamina / 100) * 0.12)
    strength *= (0.94 + (morale / 100) * 0.10)
    strength *= ((tactic['atk'] + tactic['def']) / 2)
    strength += team['reputation'] * 0.15
    return strength


def apply_fatigue(team):
    tactic = TACTICS.get(team['tactic'], TACTICS['Balanced'])
    for p in team['players']:
        p['stamina'] = clamp(p['stamina'] - random.randint(4, 10) * tactic['fatigue'], 40, 100)
        p['morale'] = clamp(p['morale'] + random.randint(-2, 2), 35, 95)


def recover_between_weeks(game_state):
    for div in game_state['divisions'].values():
        for team in div['teams']:
            for p in team['players']:
                p['stamina'] = clamp(p['stamina'] + random.randint(3, 7), 40, 100)
                p['morale'] = clamp(p['morale'] + random.randint(-1, 2), 35, 95)


def update_table(team, gf, ga):
    t = team['table']
    t['p'] += 1
    t['gf'] += gf
    t['ga'] += ga
    t['gd'] = t['gf'] - t['ga']

    if gf > ga:
        t['w'] += 1
        t['pts'] += 3
    elif gf == ga:
        t['d'] += 1
        t['pts'] += 1
    else:
        t['l'] += 1


def simulate_match(team_a, team_b):
    sa = team_strength(team_a)
    sb = team_strength(team_b)

    ga = max(0, int(round(random.gauss(sa / 24, 0.9))))
    gb = max(0, int(round(random.gauss(sb / 24, 0.9))))

    ga = min(6, ga)
    gb = min(6, gb)

    update_table(team_a, ga, gb)
    update_table(team_b, gb, ga)

    apply_fatigue(team_a)
    apply_fatigue(team_b)

    return ga, gb


def sort_table(teams):
    return sorted(
        teams,
        key=lambda t: (
            t['table']['pts'],
            t['table']['gd'],
            t['table']['gf'],
            t['reputation'],
        ),
        reverse=True,
    )


def recompute_player_derived(player):
    player['overall'] = average_attrs(player['attrs'])
    player['value'] = max(30000, int(player['overall'] * player['overall'] * 900 + player['potential'] * 2500 + random.randint(-8000, 8000)))
    player['wage'] = max(800, int(player['overall'] * 85 + random.randint(150, 900)))


def season_rollover(game_state):
    div1 = sort_table(game_state['divisions']['1']['teams'])
    div2 = sort_table(game_state['divisions']['2']['teams'])
    div3 = sort_table(game_state['divisions']['3']['teams'])

    up_2_to_1 = div2[:2]
    down_1_to_2 = div1[-2:]
    up_3_to_2 = div3[:2]
    down_2_to_3 = div2[-2:]

    for team in up_2_to_1:
        team['division'] = 1
    for team in down_1_to_2:
        team['division'] = 2
    for team in up_3_to_2:
        team['division'] = 2
    for team in down_2_to_3:
        team['division'] = 3

    new_div1 = [t for t in div1 if t not in down_1_to_2] + up_2_to_1
    new_div2 = [t for t in div2 if t not in up_2_to_1 and t not in down_2_to_3] + down_1_to_2 + up_3_to_2
    new_div3 = [t for t in div3 if t not in up_3_to_2] + down_2_to_3

    game_state['divisions']['1']['teams'] = new_div1
    game_state['divisions']['2']['teams'] = new_div2
    game_state['divisions']['3']['teams'] = new_div3

    for div_key in ['1', '2', '3']:
        teams = game_state['divisions'][div_key]['teams']
        for t in teams:
            t['table'] = {'p': 0, 'w': 0, 'd': 0, 'l': 0, 'gf': 0, 'ga': 0, 'gd': 0, 'pts': 0}
            for p in t['players']:
                p['age'] += 1
                if p['age'] <= 23 and p['overall'] < p['potential'] and random.random() < 0.45:
                    for k in p['attrs']:
                        if random.random() < 0.4:
                            p['attrs'][k] = clamp(p['attrs'][k] + random.randint(0, 2), 35, 95)
                elif p['age'] >= 30 and random.random() < 0.35:
                    for k in p['attrs']:
                        if random.random() < 0.35:
                            p['attrs'][k] = clamp(p['attrs'][k] - random.randint(0, 1), 35, 95)

                recompute_player_derived(p)
                p['stamina'] = random.randint(88, 100)
                p['morale'] = clamp(p['morale'] + random.randint(-3, 6), 40, 95)

        game_state['divisions'][div_key]['schedule'] = round_robin_schedule([t['name'] for t in teams])

    game_state['scout_pool'] = create_scout_pool(game_state['selected_country'], 10)
    game_state['transfer_offers'] = []
    game_state['season'] += 1
    game_state['week'] = 1
    game_state['news'].insert(0, 'Season ended. Promotion and relegation applied.')


def generate_transfer_offers():
    selected = get_selected_team()
    if not selected:
        return
    offers = []
    listed = [p for p in selected['players'] if p.get('transfer_listed')]
    ai_teams = []
    for div in game_state['divisions'].values():
        for t in div['teams']:
            if t['name'] != selected['name']:
                ai_teams.append(t)

    for p in listed:
        if random.random() < 0.45:
            buyer = random.choice(ai_teams)
            fee = int(p['value'] * random.uniform(0.85, 1.25))
            offers.append({
                'player_id': p['id'],
                'player_name': p['name'],
                'buyer': buyer['name'],
                'fee': fee,
            })

    game_state['transfer_offers'] = offers


def play_next_week(game_state):
    if not game_state['selected_club']:
        return 'Choose your club first.'

    if game_state['week'] > WEEKS_PER_SEASON:
        season_rollover(game_state)
        return 'New season started.'

    selected_team = get_selected_team()
    if not selected_team:
        return 'Selected club not found.'

    logs = []
    for div_key in ['1', '2', '3']:
        division = game_state['divisions'][div_key]
        week_matches = division['schedule'][game_state['week'] - 1]

        for home_name, away_name in week_matches:
            home = get_team(game_state, home_name)
            away = get_team(game_state, away_name)
            hg, ag = simulate_match(home, away)

            if selected_team['name'] in (home_name, away_name):
                result = f'{home_name} {hg} - {ag} {away_name}'
                logs.append(result)

                income = random.randint(18000, 45000)
                selected_team['budget'] += income
                selected_team['fans'] += random.randint(20, 120)

    recover_between_weeks(game_state)
    generate_transfer_offers()
    game_state['week'] += 1

    if logs:
        for line in reversed(logs):
            game_state['news'].insert(0, f'Week {game_state["week"] - 1}: {line}')

    if game_state['week'] > WEEKS_PER_SEASON + 1:
        season_rollover(game_state)

    return 'Week processed.'


def refresh_scout_pool():
    game_state['scout_pool'] = create_scout_pool(game_state['selected_country'], 10)
    game_state['news'].insert(0, 'Scout pool refreshed.')
    refresh_ui()


def sign_scout_player(player_id):
    selected = get_selected_team()
    if not selected:
        ui.notify('Choose a club first')
        return

    player = None
    for p in game_state['scout_pool']:
        if p['id'] == player_id:
            player = p
            break

    if not player:
        ui.notify('Player not found')
        return

    fee = player['value']
    if selected['budget'] < fee:
        ui.notify('Not enough budget')
        return
    if len(selected['players']) >= MAX_SQUAD_SIZE:
        ui.notify('Squad is full')
        return

    selected['budget'] -= fee
    player['club'] = selected['name']
    selected['players'].append(player)
    game_state['scout_pool'] = [p for p in game_state['scout_pool'] if p['id'] != player_id]
    game_state['news'].insert(0, f"Signed {player['name']} for ${fee:,}")
    refresh_ui()


def release_player(player_id):
    selected = get_selected_team()
    if not selected:
        return
    if len(selected['players']) <= 11:
        ui.notify('You need at least 11 players')
        return
    target = get_player_by_id(player_id)
    if not target or target['club'] != selected['name']:
        return
    selected['players'] = [p for p in selected['players'] if p['id'] != player_id]
    game_state['news'].insert(0, f"Released {target['name']}")
    if game_state.get('selected_player_id') == player_id:
        game_state['selected_player_id'] = ''
    refresh_ui()


def toggle_transfer_list(player_id):
    p = get_player_by_id(player_id)
    selected = get_selected_team()
    if not p or not selected or p['club'] != selected['name']:
        return
    p['transfer_listed'] = not p.get('transfer_listed', False)
    state = 'listed' if p['transfer_listed'] else 'removed from list'
    game_state['news'].insert(0, f"{p['name']} {state}.")
    refresh_ui()


def accept_transfer_offer(player_id):
    selected = get_selected_team()
    if not selected:
        return
    offer = None
    for o in game_state['transfer_offers']:
        if o['player_id'] == player_id:
            offer = o
            break
    if not offer:
        ui.notify('Offer not found')
        return
    if len(selected['players']) <= 11:
        ui.notify('You need at least 11 players')
        return

    selected['players'] = [p for p in selected['players'] if p['id'] != player_id]
    selected['budget'] += offer['fee']
    game_state['transfer_offers'] = [o for o in game_state['transfer_offers'] if o['player_id'] != player_id]
    if game_state.get('selected_player_id') == player_id:
        game_state['selected_player_id'] = ''
    game_state['news'].insert(0, f"Sold {offer['player_name']} to {offer['buyer']} for ${offer['fee']:,}")
    refresh_ui()


def reject_transfer_offer(player_id):
    game_state['transfer_offers'] = [o for o in game_state['transfer_offers'] if o['player_id'] != player_id]
    game_state['news'].insert(0, 'Rejected a transfer offer.')
    refresh_ui()


def save_game(game_state):
    with open(SAVE_FILE, 'w', encoding='utf-8') as f:
        json.dump(game_state, f, ensure_ascii=False, indent=2)


def load_game():
    global game_state
    if SAVE_FILE.exists():
        with open(SAVE_FILE, 'r', encoding='utf-8') as f:
            game_state = json.load(f)
        refresh_ui()
        ui.notify('Loaded save.json')
    else:
        ui.notify('No local save.json found')


def export_save():
    save_game(game_state)
    ui.download(str(SAVE_FILE))


def import_save(e):
    global game_state
    try:
        content = e.content.read().decode('utf-8')
        game_state = json.loads(content)
        refresh_ui()
        ui.notify('Imported save data')
    except Exception as ex:
        ui.notify(f'Import failed: {ex}')


def set_team_tactic(team_name, tactic_name):
    team = get_team(game_state, team_name)
    if team:
        team['tactic'] = tactic_name
        refresh_ui()
        ui.notify(f'Tactic changed to {tactic_name}')


game_state = build_world('England')

country_select = None
club_select = None

status_container = None
dashboard_container = None
squad_container = None
player_detail_container = None
match_container = None
standings_container = None
scout_container = None
transfer_container = None
save_container = None


def player_label(p):
    return f"{p['name']} | {p['pos']} | OVR {p['overall']}"


def render_status():
    status_container.clear()
    with status_container:
        with ui.card().classes('w-full'):
            ui.label(APP_NAME).classes('text-h5')
            ui.label(f"Country: {game_state['selected_country']}")
            ui.label(f"Season {game_state['season']} / Week {min(game_state['week'], WEEKS_PER_SEASON)}")
            ui.label(f"Club: {game_state['selected_club'] or 'Not selected'}")


def render_dashboard():
    dashboard_container.clear()
    with dashboard_container:
        selected = get_selected_team()
        if not selected:
            ui.label('Choose a club first from the selector above.')
            return

        ordered = sort_table(game_state['divisions'][str(selected['division'])]['teams'])
        rank = next((i + 1 for i, t in enumerate(ordered) if t['name'] == selected['name']), '-')
        avg_overall = round(sum(p['overall'] for p in selected['players']) / len(selected['players']), 1)
        wage_bill = sum(p['wage'] for p in selected['players'])

        with ui.card().classes('w-full'):
            ui.label(selected['name']).classes('text-h6')
            ui.label(f"Division: {selected['division']} | Rank: {rank}/{len(ordered)}")
            ui.label(f"Budget: ${selected['budget']:,}")
            ui.label(f"Fans: {selected['fans']:,}")
            ui.label(f"Squad Avg: {avg_overall}")
            ui.label(f"Weekly Wage Bill: ${wage_bill:,}")
            ui.label(f"Tactic: {selected['tactic']}")

        with ui.card().classes('w-full'):
            ui.label('Recent News').classes('text-subtitle1')
            for line in game_state['news'][:8]:
                ui.label(f'• {line}')


def render_squad():
    squad_container.clear()
    with squad_container:
        selected = get_selected_team()
        if not selected:
            ui.label('Choose a club first.')
            return

        with ui.card().classes('w-full'):
            ui.label('Tactic').classes('text-subtitle1')
            ui.select(
                options=list(TACTICS.keys()),
                value=selected['tactic'],
                on_change=lambda e: set_team_tactic(selected['name'], e.value),
            ).classes('w-full')

        ui.label('Squad').classes('text-subtitle1')
        for p in sorted(selected['players'], key=lambda x: (x['pos'], -x['overall'])):
            with ui.card().classes('w-full'):
                ui.label(f"{p['name']} | {p['pos']} | OVR {p['overall']} | POT {p['potential']}")
                ui.label(f"Age {p['age']} | STA {p['stamina']} | MOR {p['morale']} | Value ${p['value']:,}")
                row = ui.row().classes('w-full')
                with row:
                    ui.button('Detail', on_click=lambda _, pid=p['id']: select_player(pid)).props('dense')
                    ui.button(
                        'Unlist' if p.get('transfer_listed') else 'List',
                        on_click=lambda _, pid=p['id']: toggle_transfer_list(pid)
                    ).props('dense')
                    ui.button('Release', on_click=lambda _, pid=p['id']: release_player(pid)).props('dense color=negative')

        ui.separator()
        ui.label('Player Detail').classes('text-subtitle1')
        with ui.card().classes('w-full'):
            player_detail_container.clear()
            with player_detail_container:
                selected_player = get_player_by_id(game_state.get('selected_player_id'))
                if selected_player:
                    render_player_detail_content(selected_player)
                else:
                    ui.label('Tap Detail on a player.')


def render_player_detail_content(player):
    ui.label(f"{player['name']}").classes('text-h6')
    ui.label(f"{player['pos']} | Age {player['age']} | {player['nationality']}")
    ui.label(f"OVR {player['overall']} | POT {player['potential']}")
    ui.label(f"Value ${player['value']:,} | Wage ${player['wage']:,}")
    ui.label(f"Stamina {player['stamina']} | Morale {player['morale']}")
    for k, v in player['attrs'].items():
        ui.label(f'{k}: {v}')


def render_match():
    match_container.clear()
    with match_container:
        selected = get_selected_team()
        if not selected:
            ui.label('Choose a club first.')
            return

        with ui.card().classes('w-full'):
            ui.label('Weekly Progress').classes('text-subtitle1')
            ui.label(f"Current week: {min(game_state['week'], WEEKS_PER_SEASON)} / {WEEKS_PER_SEASON}")
            ui.button(
                'Play Next Week',
                on_click=lambda: (play_next_week(game_state), refresh_ui()),
            ).classes('w-full')

        div = game_state['divisions'][str(selected['division'])]
        week_index = min(game_state['week'] - 1, len(div['schedule']) - 1)
        with ui.card().classes('w-full'):
            ui.label('This Division Fixtures').classes('text-subtitle1')
            if 0 <= week_index < len(div['schedule']):
                for home, away in div['schedule'][week_index]:
                    ui.label(f'{home} vs {away}')


def render_standings():
    standings_container.clear()
    with standings_container:
        for div_key in ['1', '2', '3']:
            division = game_state['divisions'][div_key]
            with ui.card().classes('w-full'):
                ui.label(division['name']).classes('text-subtitle1')
                ordered = sort_table(division['teams'])
                for idx, t in enumerate(ordered, start=1):
                    mark = '⭐ ' if t['name'] == game_state['selected_club'] else ''
                    row = (
                        f"{idx}. {mark}{t['name']} | "
                        f"P {t['table']['p']} W {t['table']['w']} D {t['table']['d']} L {t['table']['l']} | "
                        f"GF {t['table']['gf']} GA {t['table']['ga']} GD {t['table']['gd']} | "
                        f"PTS {t['table']['pts']}"
                    )
                    ui.label(row).classes('text-body2')


def render_scout():
    scout_container.clear()
    with scout_container:
        selected = get_selected_team()
        if not selected:
            ui.label('Choose a club first.')
            return

        with ui.card().classes('w-full'):
            ui.label('Scout Market').classes('text-subtitle1')
            ui.button('Refresh Scouts', on_click=refresh_scout_pool).classes('w-full')
            ui.label(f"Budget: ${selected['budget']:,}")

        for p in sorted(game_state['scout_pool'], key=lambda x: (-x['overall'], x['age'])):
            with ui.card().classes('w-full'):
                ui.label(f"{p['name']} | {p['pos']} | OVR {p['overall']} | POT {p['potential']}")
                ui.label(f"Age {p['age']} | {p['nationality']} | Value ${p['value']:,} | Wage ${p['wage']:,}")
                ui.label(' / '.join(f'{k}:{v}' for k, v in p['attrs'].items())).classes('text-caption')
                with ui.row():
                    ui.button('Detail', on_click=lambda _, pid=p['id']: select_player(pid)).props('dense')
                    ui.button('Sign', on_click=lambda _, pid=p['id']: sign_scout_player(pid)).props('dense color=positive')


def render_transfer():
    transfer_container.clear()
    with transfer_container:
        selected = get_selected_team()
        if not selected:
            ui.label('Choose a club first.')
            return

        with ui.card().classes('w-full'):
            ui.label('Transfer List').classes('text-subtitle1')
            listed = [p for p in selected['players'] if p.get('transfer_listed')]
            if not listed:
                ui.label('No players listed.')
            else:
                for p in listed:
                    ui.label(f"{p['name']} | {p['pos']} | OVR {p['overall']} | Asking Value ${p['value']:,}")

        with ui.card().classes('w-full'):
            ui.label('Incoming Offers').classes('text-subtitle1')
            if not game_state['transfer_offers']:
                ui.label('No offers this week.')
            else:
                for o in game_state['transfer_offers']:
                    with ui.row().classes('w-full items-center'):
                        ui.label(f"{o['player_name']} ← {o['buyer']} | ${o['fee']:,}")
                        ui.button('Accept', on_click=lambda _, pid=o['player_id']: accept_transfer_offer(pid)).props('dense color=positive')
                        ui.button('Reject', on_click=lambda _, pid=o['player_id']: reject_transfer_offer(pid)).props('dense color=negative')


def render_save():
    save_container.clear()
    with save_container:
        with ui.card().classes('w-full'):
            ui.label('Save Management').classes('text-subtitle1')
            ui.button('Save', on_click=lambda: (save_game(game_state), ui.notify('Saved to save.json'))).classes('w-full')
            ui.button('Load', on_click=load_game).classes('w-full')
            ui.button('Export JSON', on_click=export_save).classes('w-full')
            ui.upload(on_upload=import_save, label='Import JSON').classes('w-full')


def select_player(player_id):
    game_state['selected_player_id'] = player_id
    refresh_ui()


def refresh_ui():
    if game_state['selected_country'] != country_select.value:
        country_select.value = game_state['selected_country']

    clubs = []
    for div_key in ['1', '2', '3']:
        for t in sort_table(game_state['divisions'][div_key]['teams']):
            clubs.append(f"Div {div_key} | {t['name']}")

    club_select.options = clubs
    if game_state['selected_club']:
        team = get_team(game_state, game_state['selected_club'])
        if team:
            club_select.value = f"Div {team['division']} | {team['name']}"
    else:
        club_select.value = None

    render_status()
    render_dashboard()
    render_squad()
    render_match()
    render_standings()
    render_scout()
    render_transfer()
    render_save()


def on_new_world(country_name):
    global game_state
    game_state = build_world(country_name)
    refresh_ui()
    ui.notify(f'Created world: {country_name}')


def on_select_club(label):
    if not label:
        return
    _, club_name = label.split('|', 1)
    game_state['selected_club'] = club_name.strip()
    game_state['news'].insert(0, f"Selected club: {game_state['selected_club']}")
    refresh_ui()


ui.add_head_html('''
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
    body { background: #0f172a; color: #e5e7eb; }
    .nicegui-content { max-width: 900px; margin: 0 auto; }
</style>
''')

ui.label(APP_NAME).classes('text-h4')

with ui.card().classes('w-full'):
    ui.label('World Setup').classes('text-subtitle1')
    country_select = ui.select(
        options=list(COUNTRIES.keys()),
        value=game_state['selected_country'],
        label='Country',
    ).classes('w-full')
    ui.button(
        'Create New World',
        on_click=lambda: on_new_world(country_select.value),
    ).classes('w-full')

    club_select = ui.select(
        options=[],
        value=None,
        label='Choose Club',
        on_change=lambda e: on_select_club(e.value),
    ).classes('w-full')

status_container = ui.column().classes('w-full')

with ui.tabs().classes('w-full') as tabs:
    t_dashboard = ui.tab('Dashboard')
    t_squad = ui.tab('Squad')
    t_match = ui.tab('Match')
    t_standings = ui.tab('Standings')
    t_scout = ui.tab('Scout')
    t_transfer = ui.tab('Transfer')
    t_save = ui.tab('Save')

with ui.tab_panels(tabs, value=t_dashboard).classes('w-full'):
    with ui.tab_panel(t_dashboard):
        dashboard_container = ui.column().classes('w-full')
    with ui.tab_panel(t_squad):
        squad_container = ui.column().classes('w-full')
        player_detail_container = ui.column().classes('w-full')
    with ui.tab_panel(t_match):
        match_container = ui.column().classes('w-full')
    with ui.tab_panel(t_standings):
        standings_container = ui.column().classes('w-full')
    with ui.tab_panel(t_scout):
        scout_container = ui.column().classes('w-full')
    with ui.tab_panel(t_transfer):
        transfer_container = ui.column().classes('w-full')
    with ui.tab_panel(t_save):
        save_container = ui.column().classes('w-full')

refresh_ui()

ui.run(host='0.0.0.0', port=PORT)
