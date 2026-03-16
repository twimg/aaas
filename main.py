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
MAX_SQUAD_SIZE = 24
MAX_YOUTH_SIZE = 8
WEEKS_PER_SEASON = (TEAMS_PER_DIV - 1) * 2  # 18

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
    'バランス': {'atk': 1.00, 'def': 1.00, 'fatigue': 1.00},
    'ポゼッション': {'atk': 1.03, 'def': 1.00, 'fatigue': 1.03},
    'カウンター': {'atk': 1.05, 'def': 0.98, 'fatigue': 0.98},
    'ハイプレス': {'atk': 1.04, 'def': 1.03, 'fatigue': 1.08},
    'ローブロック': {'atk': 0.96, 'def': 1.08, 'fatigue': 0.95},
}

POS_SEQUENCE = ['GK', 'DF', 'DF', 'DF', 'DF', 'MF', 'MF', 'MF', 'MF', 'FW', 'FW', 'GK', 'DF', 'DF', 'MF', 'MF', 'FW', 'FW']

nav_state = {'section': 'dashboard'}

country_select = None
club_select = None
club_picker_container = None
status_container = None
content_container = None
world_setup_container = None

game_state = None


def clamp(x, lo, hi):
    return lo if x < lo else hi if x > hi else x


def avg(values):
    return round(sum(values) / len(values), 1) if values else 0


def avg_attrs(attrs):
    return round(sum(attrs.values()) / len(attrs))


def make_name(country_data):
    return f"{random.choice(country_data['first_names'])} {random.choice(country_data['last_names'])}"


def make_club_name(country_data, used_names):
    for _ in range(3000):
        name = f"{random.choice(country_data['club_prefix'])} {random.choice(country_data['club_suffix'])}"
        if name not in used_names:
            used_names.add(name)
            return name
    name = f"{random.choice(country_data['club_prefix'])} {random.choice(country_data['club_suffix'])} {random.randint(1, 999)}"
    used_names.add(name)
    return name


def base_attrs_by_pos(pos):
    if pos == 'GK':
        return {'SPD': 52, 'PAS': 58, 'TEC': 55, 'DEF': 73, 'PHY': 68, 'SHT': 35, 'MEN': 66}
    if pos == 'DF':
        return {'SPD': 62, 'PAS': 58, 'TEC': 57, 'DEF': 70, 'PHY': 70, 'SHT': 48, 'MEN': 62}
    if pos == 'MF':
        return {'SPD': 64, 'PAS': 68, 'TEC': 68, 'DEF': 58, 'PHY': 62, 'SHT': 60, 'MEN': 64}
    return {'SPD': 72, 'PAS': 60, 'TEC': 67, 'DEF': 42, 'PHY': 66, 'SHT': 72, 'MEN': 61}


def recompute_player(player):
    player['overall'] = avg_attrs(player['attrs'])
    player['value'] = max(30000, int(player['overall'] * player['overall'] * 900 + player['potential'] * 2500 + random.randint(-8000, 8000)))
    player['wage'] = max(800, int(player['overall'] * 85 + random.randint(150, 900)))


def generate_player(country_name, club_name, idx, youth=False):
    country_data = COUNTRIES[country_name]
    pos = POS_SEQUENCE[idx % len(POS_SEQUENCE)] if not youth else random.choice(['GK', 'DF', 'DF', 'MF', 'MF', 'FW'])
    age = random.randint(15, 18) if youth else random.randint(17, 33)
    base = base_attrs_by_pos(pos)

    attrs = {}
    for k, v in base.items():
        bias = country_data['bias'][k]
        spread = 10 if youth else 8
        raw = random.randint(v - spread, v + spread)
        if youth:
            raw -= random.randint(1, 5)
        attrs[k] = clamp(int(raw * bias), 35, 90)

    overall = avg_attrs(attrs)
    potential = clamp(overall + random.randint(4, 18) if youth else overall + random.randint(0, 15), overall, 94)

    player = {
        'id': f'{club_name}_{idx}_{random.randint(1000, 9999)}',
        'name': make_name(country_data),
        'age': age,
        'nationality': country_name,
        'club': club_name,
        'pos': pos,
        'attrs': attrs,
        'overall': overall,
        'potential': potential,
        'stamina': random.randint(85, 100) if not youth else 100,
        'morale': random.randint(55, 75) if not youth else random.randint(60, 80),
        'injury': 0,
        'value': 0,
        'wage': 0,
        'transfer_listed': False,
    }
    recompute_player(player)
    return player


def create_sponsor(country_name, division):
    sponsor_names = {
        'England': ['NorthSea Media', 'Crown Logistics', 'Royal Finance', 'IronWorks Group'],
        'Brazil': ['Rio Energy', 'Sol Telecom', 'Verde Bank', 'Nova Foods'],
        'Germany': ['Rhein Motors', 'Union Technik', 'Nord Industrie', 'Berg Systems'],
        'Spain': ['Costa Air', 'Sol Bank', 'Mar Holdings', 'Deportivo Media'],
        'Italy': ['Roma Invest', 'Milano Foods', 'Verona Tech', 'Lazio Capital'],
        'Japan': ['Aozora Holdings', 'Kouyou Foods', 'Shinsei Tech', 'Hikari Logistics'],
    }

    weekly_base = {1: 45000, 2: 28000, 3: 18000}[division]
    bonus_base = {1: 220000, 2: 140000, 3: 90000}[division]
    target_rank = {1: 5, 2: 4, 3: 3}[division]

    return {
        'name': random.choice(sponsor_names[country_name]),
        'weekly_income': weekly_base + random.randint(-6000, 6000),
        'win_bonus': random.randint(4000, 12000),
        'season_bonus': bonus_base + random.randint(-30000, 30000),
        'target_rank': target_rank,
    }


def create_team(country_name, club_name, division):
    base_rep = {1: 72, 2: 64, 3: 57}[division]
    players = [generate_player(country_name, club_name, i) for i in range(SQUAD_SIZE)]
    youth = [generate_player(country_name, club_name, i + 100, youth=True) for i in range(5)]
    return {
        'name': club_name,
        'country': country_name,
        'division': division,
        'budget': random.randint(700_000, 1_600_000) * (4 - division),
        'fans': random.randint(3000, 18000) * (4 - division),
        'tactic': 'バランス',
        'reputation': base_rep + random.randint(-4, 4),
        'sponsor': create_sponsor(country_name, division),
        'players': players,
        'youth': youth,
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

    second = [[(b, a) for (a, b) in rnd] for rnd in rounds]
    return rounds + second


def create_scout_pool(country_name, n=8):
    pool = []
    for i in range(n):
        p = generate_player(country_name, 'Scout Pool', i)
        p['value'] = int(p['value'] * random.uniform(0.82, 1.15))
        p['wage'] = int(p['wage'] * random.uniform(0.85, 1.1))
        pool.append(p)
    return pool


def init_cup(div1_teams):
    chosen = random.sample([t['name'] for t in div1_teams], 8)
    fixtures = [(chosen[0], chosen[1]), (chosen[2], chosen[3]), (chosen[4], chosen[5]), (chosen[6], chosen[7])]
    return {
        'round': '準々決勝',
        'fixtures': fixtures,
        'winner': '',
        'history': [],
        'active': True,
    }


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
        'news': [f'{selected_country} のワールドを作成しました。'],
        'divisions': divisions,
        'scout_pool': create_scout_pool(selected_country, 10),
        'transfer_offers': [],
        'cup': init_cup(divisions['1']['teams']),
        'finance_history': [],
    }


def get_team(team_name):
    for div in game_state['divisions'].values():
        for team in div['teams']:
            if team['name'] == team_name:
                return team
    return None


def get_selected_team():
    if not game_state['selected_club']:
        return None
    return get_team(game_state['selected_club'])


def get_player_by_id(player_id):
    if not player_id:
        return None
    for div in game_state['divisions'].values():
        for team in div['teams']:
            for p in team['players']:
                if p['id'] == player_id:
                    return p
            for p in team['youth']:
                if p['id'] == player_id:
                    return p
    for p in game_state.get('scout_pool', []):
        if p['id'] == player_id:
            return p
    return None


def available_lineup(team):
    fit = [p for p in team['players'] if p['injury'] == 0]
    return sorted(fit, key=lambda p: p['overall'], reverse=True)[:11]


def team_strength(team):
    players = available_lineup(team)
    if not players:
        return 40.0
    base = sum(p['overall'] for p in players) / len(players)
    stamina = sum(p['stamina'] for p in players) / len(players)
    morale = sum(p['morale'] for p in players) / len(players)
    tactic = TACTICS.get(team['tactic'], TACTICS['バランス'])

    strength = base
    strength *= (0.92 + (stamina / 100) * 0.12)
    strength *= (0.94 + (morale / 100) * 0.10)
    strength *= ((tactic['atk'] + tactic['def']) / 2)
    strength += team['reputation'] * 0.15
    strength -= max(0, 11 - len(players)) * 1.8
    return strength


def maybe_injure_player(team):
    candidates = [p for p in team['players'] if p['injury'] == 0]
    if candidates and random.random() < 0.12:
        p = random.choice(candidates)
        weeks = random.randint(1, 4)
        p['injury'] = weeks
        if team['name'] == game_state['selected_club']:
            game_state['news'].insert(0, f'{p["name"]} が {weeks} 週間の負傷です。')


def apply_fatigue(team):
    tactic = TACTICS.get(team['tactic'], TACTICS['バランス'])
    for p in team['players']:
        if p['injury'] > 0:
            continue
        p['stamina'] = clamp(int(p['stamina'] - random.randint(4, 10) * tactic['fatigue']), 40, 100)
        p['morale'] = clamp(p['morale'] + random.randint(-2, 2), 35, 95)
    maybe_injure_player(team)


def recover_between_weeks():
    for div in game_state['divisions'].values():
        for team in div['teams']:
            for p in team['players']:
                if p['injury'] > 0:
                    p['injury'] -= 1
                    p['stamina'] = clamp(p['stamina'] + random.randint(2, 5), 40, 100)
                    if p['injury'] == 0 and team['name'] == game_state['selected_club']:
                        game_state['news'].insert(0, f'{p["name"]} が負傷から復帰しました。')
                else:
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


def simulate_match(team_a, team_b, cup=False):
    sa = team_strength(team_a)
    sb = team_strength(team_b)

    ga = max(0, int(round(random.gauss(sa / 24, 0.9))))
    gb = max(0, int(round(random.gauss(sb / 24, 0.9))))
    ga = min(6, ga)
    gb = min(6, gb)

    if cup and ga == gb:
        if random.random() < 0.5:
            ga += 1
        else:
            gb += 1

    if not cup:
        update_table(team_a, ga, gb)
        update_table(team_b, gb, ga)

    apply_fatigue(team_a)
    apply_fatigue(team_b)
    return ga, gb


def sort_table(teams):
    return sorted(
        teams,
        key=lambda t: (t['table']['pts'], t['table']['gd'], t['table']['gf'], t['reputation']),
        reverse=True,
    )


def add_finance_log(category, amount, note=''):
    game_state['finance_history'].insert(0, {
        'season': game_state['season'],
        'week': game_state['week'],
        'category': category,
        'amount': amount,
        'note': note,
    })
    game_state['finance_history'] = game_state['finance_history'][:80]


def apply_weekly_finance(team, won=False):
    sponsor = team.get('sponsor', {})
    weekly_income = sponsor.get('weekly_income', 0)
    win_bonus = sponsor.get('win_bonus', 0)

    wage_bill = sum(p['wage'] for p in team['players'])
    team['budget'] += weekly_income
    add_finance_log('スポンサー収入', weekly_income, sponsor.get('name', 'スポンサー不明'))

    team['budget'] -= wage_bill
    add_finance_log('人件費', -wage_bill, '週給支払い')

    if won:
        team['budget'] += win_bonus
        add_finance_log('勝利ボーナス', win_bonus, sponsor.get('name', 'スポンサー不明'))


def club_initial_assessment(team):
    avg_ovr = avg([p['overall'] for p in team['players']])
    avg_pot = avg([p['potential'] for p in team['players']])
    avg_age = avg([p['age'] for p in team['players']])

    baseline = {1: 70, 2: 63, 3: 57}[team['division']]
    strength_gap = avg_ovr - baseline

    if strength_gap >= 5:
        level = '優勝候補'
    elif strength_gap >= 2:
        level = '上位争い'
    elif strength_gap >= -1:
        level = '中位想定'
    elif strength_gap >= -4:
        level = '残留争い'
    else:
        level = 'かなり厳しい戦力'

    return {
        'avg_ovr': avg_ovr,
        'avg_pot': avg_pot,
        'avg_age': avg_age,
        'level': level,
    }


def reset_team_for_new_season(team):
    team['table'] = {'p': 0, 'w': 0, 'd': 0, 'l': 0, 'gf': 0, 'ga': 0, 'gd': 0, 'pts': 0}
    for p in team['players']:
        p['age'] += 1
        if p['age'] <= 23 and p['overall'] < p['potential'] and random.random() < 0.45:
            for k in p['attrs']:
                if random.random() < 0.4:
                    p['attrs'][k] = clamp(p['attrs'][k] + random.randint(0, 2), 35, 95)
        elif p['age'] >= 30 and random.random() < 0.35:
            for k in p['attrs']:
                if random.random() < 0.35:
                    p['attrs'][k] = clamp(p['attrs'][k] - random.randint(0, 1), 35, 95)

        recompute_player(p)
        p['stamina'] = random.randint(88, 100)
        p['morale'] = clamp(p['morale'] + random.randint(-3, 6), 40, 95)
        p['injury'] = 0
        p['transfer_listed'] = False

    while len(team['youth']) < 5:
        team['youth'].append(generate_player(team['country'], team['name'], random.randint(100, 999), youth=True))


def apply_season_sponsor_bonus():
    selected = get_selected_team()
    if not selected:
        return

    ordered = sort_table(game_state['divisions'][str(selected['division'])]['teams'])
    rank = next((i + 1 for i, t in enumerate(ordered) if t['name'] == selected['name']), None)
    sponsor = selected.get('sponsor', {})

    if rank is not None and rank <= sponsor.get('target_rank', 99):
        bonus = sponsor.get('season_bonus', 0)
        selected['budget'] += bonus
        add_finance_log('シーズンスポンサー報酬', bonus, sponsor.get('name', 'スポンサー不明'))
        game_state['news'].insert(0, f'スポンサー目標達成。{sponsor.get("name")} から ${bonus:,} の報酬を受け取りました。')
    else:
        game_state['news'].insert(0, f'{sponsor.get("name", "スポンサー不明")} の目標を達成できませんでした。')


def season_rollover():
    apply_season_sponsor_bonus()

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

    game_state['divisions']['1']['teams'] = [t for t in div1 if t not in down_1_to_2] + up_2_to_1
    game_state['divisions']['2']['teams'] = [t for t in div2 if t not in up_2_to_1 and t not in down_2_to_3] + down_1_to_2 + up_3_to_2
    game_state['divisions']['3']['teams'] = [t for t in div3 if t not in up_3_to_2] + down_2_to_3

    for div_key in ['1', '2', '3']:
        teams = game_state['divisions'][div_key]['teams']
        for t in teams:
            reset_team_for_new_season(t)
        game_state['divisions'][div_key]['schedule'] = round_robin_schedule([t['name'] for t in teams])

    game_state['cup'] = init_cup(game_state['divisions']['1']['teams'])
    game_state['scout_pool'] = create_scout_pool(game_state['selected_country'], 10)
    game_state['transfer_offers'] = []
    game_state['season'] += 1
    game_state['week'] = 1
    game_state['news'].insert(0, 'シーズン終了。昇格・降格を反映しました。')


def generate_transfer_offers():
    selected = get_selected_team()
    if not selected:
        return
    offers = []
    listed = [p for p in selected['players'] if p.get('transfer_listed')]
    ai_teams = [t for div in game_state['divisions'].values() for t in div['teams'] if t['name'] != selected['name']]

    for p in listed:
        if random.random() < 0.45:
            buyer = random.choice(ai_teams)
            fee = int(p['value'] * random.uniform(0.85, 1.25))
            offers.append({'player_id': p['id'], 'player_name': p['name'], 'buyer': buyer['name'], 'fee': fee})
    game_state['transfer_offers'] = offers


def play_next_week():
    if not game_state['selected_club']:
        ui.notify('最初にクラブを選んでください')
        return

    if game_state['week'] > WEEKS_PER_SEASON:
        season_rollover()
        refresh_ui()
        return

    selected_team = get_selected_team()
    logs = []
    selected_won = False

    for div_key in ['1', '2', '3']:
        division = game_state['divisions'][div_key]
        week_matches = division['schedule'][game_state['week'] - 1]
        for home_name, away_name in week_matches:
            home = get_team(home_name)
            away = get_team(away_name)
            hg, ag = simulate_match(home, away, cup=False)

            if selected_team['name'] == home_name and hg > ag:
                selected_won = True
            elif selected_team['name'] == away_name and ag > hg:
                selected_won = True

            if selected_team['name'] in (home_name, away_name):
                result = f'{home_name} {hg} - {ag} {away_name}'
                logs.append(result)
                gate_income = random.randint(18000, 45000)
                selected_team['budget'] += gate_income
                selected_team['fans'] += random.randint(20, 120)
                add_finance_log('試合収入', gate_income, 'リーグ戦')

    apply_weekly_finance(selected_team, won=selected_won)
    recover_between_weeks()
    generate_transfer_offers()

    for line in reversed(logs):
        game_state['news'].insert(0, f'第{game_state["week"]}節: {line}')

    sponsor = selected_team.get('sponsor', {})
    game_state['news'].insert(
        0,
        f'スポンサー収入 {sponsor.get("name", "スポンサー不明")}: '
        f'${sponsor.get("weekly_income", 0):,}'
        + (f' + 勝利ボーナス ${sponsor.get("win_bonus", 0):,}' if selected_won else '')
    )

    game_state['week'] += 1
    refresh_ui()


def play_next_cup_round():
    cup = game_state['cup']
    if not cup['active']:
        ui.notify('カップ戦は終了しています')
        return

    next_winners = []
    results = []
    for home_name, away_name in cup['fixtures']:
        home = get_team(home_name)
        away = get_team(away_name)
        hg, ag = simulate_match(home, away, cup=True)
        winner = home if hg > ag else away
        next_winners.append(winner['name'])
        results.append(f'{home_name} {hg}-{ag} {away_name} | 勝者: {winner["name"]}')

    cup['history'].append({'round': cup['round'], 'results': results})
    for r in reversed(results):
        game_state['news'].insert(0, f'カップ {cup["round"]}: {r}')

    if len(next_winners) == 4:
        cup['round'] = '準決勝'
        cup['fixtures'] = [(next_winners[0], next_winners[1]), (next_winners[2], next_winners[3])]
    elif len(next_winners) == 2:
        cup['round'] = '決勝'
        cup['fixtures'] = [(next_winners[0], next_winners[1])]
    elif len(next_winners) == 1:
        cup['round'] = '終了'
        cup['winner'] = next_winners[0]
        cup['fixtures'] = []
        cup['active'] = False
        game_state['news'].insert(0, f'カップ優勝: {cup["winner"]}')
    refresh_ui()


def refresh_scout_pool():
    game_state['scout_pool'] = create_scout_pool(game_state['selected_country'], 10)
    game_state['news'].insert(0, 'スカウト候補を更新しました。')
    refresh_ui()


def sign_scout_player(player_id):
    selected = get_selected_team()
    if not selected:
        ui.notify('最初にクラブを選んでください')
        return

    player = next((p for p in game_state['scout_pool'] if p['id'] == player_id), None)
    if not player:
        ui.notify('選手が見つかりません')
        return
    if selected['budget'] < player['value']:
        ui.notify('予算が足りません')
        return
    if len(selected['players']) >= MAX_SQUAD_SIZE:
        ui.notify('トップチームの人数が上限です')
        return

    selected['budget'] -= player['value']
    add_finance_log('移籍加入', -player['value'], player['name'])
    player['club'] = selected['name']
    selected['players'].append(player)
    game_state['scout_pool'] = [p for p in game_state['scout_pool'] if p['id'] != player_id]
    game_state['news'].insert(0, f'{player["name"]} を ${player["value"]:,} で獲得しました。')
    refresh_ui()


def promote_youth(player_id):
    selected = get_selected_team()
    if not selected:
        return
    if len(selected['players']) >= MAX_SQUAD_SIZE:
        ui.notify('トップチームが満員です')
        return
    youth = next((p for p in selected['youth'] if p['id'] == player_id), None)
    if not youth:
        return
    selected['youth'] = [p for p in selected['youth'] if p['id'] != player_id]
    youth['club'] = selected['name']
    selected['players'].append(youth)
    game_state['news'].insert(0, f'ユース選手 {youth["name"]} を昇格させました。')
    while len(selected['youth']) < 5:
        selected['youth'].append(generate_player(selected['country'], selected['name'], random.randint(100, 999), youth=True))
    refresh_ui()


def release_youth(player_id):
    selected = get_selected_team()
    if not selected:
        return
    selected['youth'] = [p for p in selected['youth'] if p['id'] != player_id]
    while len(selected['youth']) < 5:
        selected['youth'].append(generate_player(selected['country'], selected['name'], random.randint(100, 999), youth=True))
    game_state['news'].insert(0, 'ユース選手を放出しました。')
    refresh_ui()


def release_player(player_id):
    selected = get_selected_team()
    if not selected:
        return
    if len(selected['players']) <= 11:
        ui.notify('最低11人は必要です')
        return
    target = get_player_by_id(player_id)
    if not target or target['club'] != selected['name']:
        return
    selected['players'] = [p for p in selected['players'] if p['id'] != player_id]
    game_state['news'].insert(0, f'{target["name"]} を放出しました。')
    if game_state.get('selected_player_id') == player_id:
        game_state['selected_player_id'] = ''
    refresh_ui()


def toggle_transfer_list(player_id):
    p = get_player_by_id(player_id)
    selected = get_selected_team()
    if not p or not selected or p['club'] != selected['name']:
        return
    p['transfer_listed'] = not p.get('transfer_listed', False)
    state = '移籍リストに掲載' if p['transfer_listed'] else '移籍リストから解除'
    game_state['news'].insert(0, f'{p["name"]} を {state} しました。')
    refresh_ui()


def accept_transfer_offer(player_id):
    selected = get_selected_team()
    if not selected:
        return
    offer = next((o for o in game_state['transfer_offers'] if o['player_id'] == player_id), None)
    if not offer:
        return
    if len(selected['players']) <= 11:
        ui.notify('最低11人は必要です')
        return
    selected['players'] = [p for p in selected['players'] if p['id'] != player_id]
    selected['budget'] += offer['fee']
    add_finance_log('移籍売却', offer['fee'], offer['player_name'])
    game_state['transfer_offers'] = [o for o in game_state['transfer_offers'] if o['player_id'] != player_id]
    if game_state.get('selected_player_id') == player_id:
        game_state['selected_player_id'] = ''
    game_state['news'].insert(0, f'{offer["player_name"]} を {offer["buyer"]} に ${offer["fee"]:,} で売却しました。')
    refresh_ui()


def reject_transfer_offer(player_id):
    game_state['transfer_offers'] = [o for o in game_state['transfer_offers'] if o['player_id'] != player_id]
    game_state['news'].insert(0, 'オファーを拒否しました。')
    refresh_ui()


def select_player(player_id):
    game_state['selected_player_id'] = player_id
    nav_state['section'] = 'squad'
    refresh_ui()
    player = get_player_by_id(player_id)
    if player:
        ui.notify(f'{player["name"]} の詳細を表示しました')


def save_game():
    with open(SAVE_FILE, 'w', encoding='utf-8') as f:
        json.dump(game_state, f, ensure_ascii=False, indent=2)
    ui.notify('save.json に保存しました')


def load_game():
    global game_state
    if SAVE_FILE.exists():
        with open(SAVE_FILE, 'r', encoding='utf-8') as f:
            game_state = json.load(f)
        refresh_ui()
        ui.notify('save.json を読み込みました')
    else:
        ui.notify('save.json が見つかりません')


def export_save():
    save_game()
    ui.download(str(SAVE_FILE))


def import_save(e):
    global game_state
    try:
        game_state = json.loads(e.content.read().decode('utf-8'))
        refresh_ui()
        ui.notify('セーブデータを読み込みました')
    except Exception as ex:
        ui.notify(f'読込失敗: {ex}')


def set_team_tactic(tactic_name):
    team = get_selected_team()
    if team:
        team['tactic'] = tactic_name
        game_state['news'].insert(0, f'戦術を {tactic_name} に変更しました。')
        refresh_ui()


def on_new_world(country_name):
    global game_state
    game_state = build_world(country_name)
    nav_state['section'] = 'dashboard'
    refresh_ui()
    ui.notify(f'{country_name} で新規ワールドを作成しました')


def on_select_club(label):
    if not label:
        return
    _, club_name = label.split('|', 1)
    game_state['selected_club'] = club_name.strip()
    game_state['news'].insert(0, f'クラブを選択: {game_state["selected_club"]}')
    refresh_ui()


def select_club_direct(club_name):
    game_state['selected_club'] = club_name
    game_state['news'].insert(0, f'クラブを選択: {club_name}')
    refresh_ui()


def render_world_setup():
    world_setup_container.clear()
    with world_setup_container:
        with ui.card().classes('w-full mobile-card'):
            ui.label('ワールド設定').classes('section-title')
            ui.select(
                options=list(COUNTRIES.keys()),
                value=game_state['selected_country'],
                label='国を選択',
                on_change=lambda e: None,
            ).bind_value(country_select, 'value').classes('w-full')
            ui.button('新しい世界を作成', on_click=lambda: on_new_world(country_select.value)).classes('w-full mobile-btn')

            if not game_state['selected_club']:
                ui.label('最初のクラブを選んでください').classes('text-body2')
                club_select.classes('w-full')
                club_picker_container.classes('w-full')
            else:
                ui.label(f'選択中クラブ: {game_state["selected_club"]}').classes('text-body2')
                ui.label('クラブの選び直しはできません。変更したい場合は新しい世界を作成してください。').classes('text-caption')


def render_club_picker():
    club_picker_container.clear()
    if game_state['selected_club']:
        return
    with club_picker_container:
        ui.label('ディビジョン別クラブ選択').classes('section-title')
        for div_key in ['1', '2', '3']:
            division = game_state['divisions'][div_key]
            with ui.card().classes('w-full mobile-card'):
                ui.label(division['name']).classes('text-body1')
                for team in sort_table(division['teams']):
                    label = f'{team["name"]} | 評判 {team["reputation"]} | 予算 ${team["budget"]:,}'
                    ui.button(
                        label,
                        on_click=lambda _, name=team['name']: select_club_direct(name),
                    ).props('outline color=primary').classes('w-full mobile-btn')


def render_status():
    status_container.clear()
    with status_container:
        selected = get_selected_team()
        with ui.card().classes('w-full mobile-card status-card'):
            ui.label(APP_NAME).classes('text-h6 strong-text')
            ui.label(f'{game_state["selected_country"]} | シーズン {game_state["season"]} | 週 {min(game_state["week"], WEEKS_PER_SEASON)}').classes('muted-text')
            ui.label(f'クラブ: {game_state["selected_club"] or "未選択"}').classes('body-text')
            if selected:
                ui.label(f'予算 ${selected["budget"]:,} | ファン {selected["fans"]:,} | Div {selected["division"]}').classes('muted-text')


def render_dashboard():
    selected = get_selected_team()
    if not selected:
        with ui.card().classes('w-full mobile-card'):
            ui.label('最初にクラブを選択してください').classes('body-text')
        return

    ordered = sort_table(game_state['divisions'][str(selected['division'])]['teams'])
    rank = next((i + 1 for i, t in enumerate(ordered) if t['name'] == selected['name']), '-')
    wage_bill = sum(p['wage'] for p in selected['players'])
    assessment = club_initial_assessment(selected)
    sponsor = selected.get('sponsor', {})

    with ui.card().classes('w-full mobile-card'):
        ui.label(selected['name']).classes('section-title')
        ui.label(f'Division {selected["division"]} | 順位 {rank}/{len(ordered)}').classes('body-text')
        ui.label(f'戦術: {selected["tactic"]}').classes('body-text')
        ui.label(f'チーム平均: {avg([p["overall"] for p in selected["players"]])}').classes('body-text')
        ui.label(f'週給総額: ${wage_bill:,}').classes('body-text')
        ui.label(f'初期評価: {assessment["level"]}').classes('body-text')
        ui.label(f'平均能力 {assessment["avg_ovr"]} | 平均ポテンシャル {assessment["avg_pot"]} | 平均年齢 {assessment["avg_age"]}').classes('muted-text')
        ui.label(f'スポンサー: {sponsor.get("name", "-")}').classes('body-text')
        ui.label(
            f'週次 ${sponsor.get("weekly_income", 0):,} | '
            f'勝利ボーナス ${sponsor.get("win_bonus", 0):,} | '
            f'目標順位 {sponsor.get("target_rank", "-")}'
        ).classes('muted-text')

    with ui.card().classes('w-full mobile-card'):
        ui.label('最新ニュース').classes('section-title')
        for line in game_state['news'][:8]:
            ui.label(f'• {line}').classes('body-text')

    with ui.card().classes('w-full mobile-card'):
        ui.label('財務履歴').classes('section-title')
        if not game_state['finance_history']:
            ui.label('まだ履歴はありません').classes('body-text')
        else:
            for item in game_state['finance_history'][:10]:
                sign = '+' if item['amount'] >= 0 else ''
                ui.label(
                    f'S{item["season"]} W{item["week"]} | '
                    f'{item["category"]} | {sign}${item["amount"]:,} | {item["note"]}'
                ).classes('body-text')


def render_squad():
    selected = get_selected_team()
    if not selected:
        with ui.card().classes('w-full mobile-card'):
            ui.label('最初にクラブを選択してください').classes('body-text')
        return

    with ui.card().classes('w-full mobile-card'):
        ui.label('戦術設定').classes('section-title')
        ui.select(
            options=list(TACTICS.keys()),
            value=selected['tactic'],
            on_change=lambda e: set_team_tactic(e.value),
        ).classes('w-full')

    for p in sorted(selected['players'], key=lambda x: (x['pos'], -x['overall'])):
        with ui.card().classes('w-full mobile-card'):
            status = f' | 負傷 {p["injury"]}週' if p['injury'] > 0 else ''
            listed = ' | 移籍リスト' if p.get('transfer_listed') else ''
            ui.label(f'{p["name"]} | {p["pos"]} | OVR {p["overall"]}{listed}{status}').classes('body-text')
            ui.label(f'年齢 {p["age"]} | 体力 {p["stamina"]} | 士気 {p["morale"]} | 価値 ${p["value"]:,}').classes('muted-text')
            with ui.row().classes('w-full gap-2'):
                ui.button('詳細', on_click=lambda _, pid=p['id']: select_player(pid)).props('dense')
                ui.button('リスト' if not p.get('transfer_listed') else '解除',
                          on_click=lambda _, pid=p['id']: toggle_transfer_list(pid)).props('dense')
                ui.button('放出', on_click=lambda _, pid=p['id']: release_player(pid)).props('dense color=negative')

    selected_player = get_player_by_id(game_state.get('selected_player_id'))
    if selected_player:
        with ui.card().classes('w-full mobile-card highlight-card'):
            ui.label('選手詳細').classes('section-title')
            ui.label(f'{selected_player["name"]} | {selected_player["pos"]}').classes('text-h6 strong-text')
            ui.label(f'年齢 {selected_player["age"]} | 国籍 {selected_player["nationality"]}').classes('body-text')
            ui.label(f'総合 {selected_player["overall"]} | ポテンシャル {selected_player["potential"]}').classes('body-text')
            ui.label(f'価値 ${selected_player["value"]:,} | 週給 ${selected_player["wage"]:,}').classes('body-text')
            ui.label(' / '.join(f'{k}:{v}' for k, v in selected_player['attrs'].items())).classes('muted-text')


def render_match():
    selected = get_selected_team()
    if not selected:
        with ui.card().classes('w-full mobile-card'):
            ui.label('最初にクラブを選択してください').classes('body-text')
        return

    with ui.card().classes('w-full mobile-card'):
        ui.label('リーグ進行').classes('section-title')
        ui.label(f'現在の週: {min(game_state["week"], WEEKS_PER_SEASON)} / {WEEKS_PER_SEASON}').classes('body-text')
        ui.button('次の週へ進む', on_click=play_next_week).classes('w-full mobile-btn')

    div = game_state['divisions'][str(selected['division'])]
    week_index = min(game_state['week'] - 1, len(div['schedule']) - 1)
    with ui.card().classes('w-full mobile-card'):
        ui.label('今週のカード').classes('section-title')
        if 0 <= week_index < len(div['schedule']):
            for home, away in div['schedule'][week_index]:
                ui.label(f'{home} vs {away}').classes('body-text')


def render_standings():
    for div_key in ['1', '2', '3']:
        division = game_state['divisions'][div_key]
        with ui.card().classes('w-full mobile-card'):
            ui.label(division['name']).classes('section-title')
            ordered = sort_table(division['teams'])
            for idx, t in enumerate(ordered, start=1):
                mark = '⭐ ' if t['name'] == game_state['selected_club'] else ''
                ui.label(
                    f'{idx}. {mark}{t["name"]} | 試合 {t["table"]["p"]} 勝 {t["table"]["w"]} 分 {t["table"]["d"]} '
                    f'敗 {t["table"]["l"]} | 得失点差 {t["table"]["gd"]} | 勝点 {t["table"]["pts"]}'
                ).classes('body-text')


def render_youth():
    selected = get_selected_team()
    if not selected:
        with ui.card().classes('w-full mobile-card'):
            ui.label('最初にクラブを選択してください').classes('body-text')
        return

    with ui.card().classes('w-full mobile-card'):
        ui.label('ユース').classes('section-title')
        ui.label(f'ユース人数: {len(selected["youth"])} / {MAX_YOUTH_SIZE}').classes('body-text')
        ui.label('昇格でトップチームへ送れます').classes('muted-text')

    for p in sorted(selected['youth'], key=lambda x: (-x['potential'], -x['overall'])):
        with ui.card().classes('w-full mobile-card'):
            ui.label(f'{p["name"]} | {p["pos"]} | OVR {p["overall"]} | POT {p["potential"]}').classes('body-text')
            ui.label(f'年齢 {p["age"]} | {p["nationality"]}').classes('muted-text')
            ui.label(' / '.join(f'{k}:{v}' for k, v in p['attrs'].items())).classes('muted-text')
            with ui.row().classes('w-full gap-2'):
                ui.button('詳細', on_click=lambda _, pid=p['id']: select_player(pid)).props('dense')
                ui.button('昇格', on_click=lambda _, pid=p['id']: promote_youth(pid)).props('dense color=positive')
                ui.button('放出', on_click=lambda _, pid=p['id']: release_youth(pid)).props('dense color=negative')


def render_cup():
    cup = game_state['cup']
    with ui.card().classes('w-full mobile-card'):
        ui.label('国内カップ').classes('section-title')
        if cup['active']:
            ui.label(f'ラウンド: {cup["round"]}').classes('body-text')
            for home, away in cup['fixtures']:
                ui.label(f'{home} vs {away}').classes('body-text')
            ui.button('カップ戦を進める', on_click=play_next_cup_round).classes('w-full mobile-btn')
        else:
            ui.label(f'優勝: {cup["winner"]}').classes('body-text')

    if cup['history']:
        with ui.card().classes('w-full mobile-card'):
            ui.label('カップ結果履歴').classes('section-title')
            for block in reversed(cup['history']):
                ui.label(block['round']).classes('body-text')
                for r in block['results']:
                    ui.label(f'• {r}').classes('muted-text')


def render_scout():
    selected = get_selected_team()
    if not selected:
        with ui.card().classes('w-full mobile-card'):
            ui.label('最初にクラブを選択してください').classes('body-text')
        return

    with ui.card().classes('w-full mobile-card'):
        ui.label('スカウト市場').classes('section-title')
        ui.label(f'予算: ${selected["budget"]:,}').classes('body-text')
        ui.button('候補更新', on_click=refresh_scout_pool).classes('w-full mobile-btn')

    for p in sorted(game_state['scout_pool'], key=lambda x: (-x['overall'], x['age'])):
        with ui.card().classes('w-full mobile-card'):
            ui.label(f'{p["name"]} | {p["pos"]} | OVR {p["overall"]} | POT {p["potential"]}').classes('body-text')
            ui.label(f'年齢 {p["age"]} | {p["nationality"]} | 価値 ${p["value"]:,}').classes('muted-text')
            with ui.row().classes('w-full gap-2'):
                ui.button('詳細', on_click=lambda _, pid=p['id']: select_player(pid)).props('dense')
                ui.button('獲得', on_click=lambda _, pid=p['id']: sign_scout_player(pid)).props('dense color=positive')


def render_transfer():
    selected = get_selected_team()
    if not selected:
        with ui.card().classes('w-full mobile-card'):
            ui.label('最初にクラブを選択してください').classes('body-text')
        return

    with ui.card().classes('w-full mobile-card'):
        ui.label('移籍リスト').classes('section-title')
        listed = [p for p in selected['players'] if p.get('transfer_listed')]
        if not listed:
            ui.label('掲載中の選手はいません').classes('body-text')
        else:
            for p in listed:
                ui.label(f'{p["name"]} | {p["pos"]} | OVR {p["overall"]} | 価値 ${p["value"]:,}').classes('body-text')

    with ui.card().classes('w-full mobile-card'):
        ui.label('オファー一覧').classes('section-title')
        if not game_state['transfer_offers']:
            ui.label('今週のオファーはありません').classes('body-text')
        else:
            for o in game_state['transfer_offers']:
                ui.label(f'{o["player_name"]} ← {o["buyer"]} | ${o["fee"]:,}').classes('body-text')
                with ui.row().classes('w-full gap-2'):
                    ui.button('承諾', on_click=lambda _, pid=o['player_id']: accept_transfer_offer(pid)).props('dense color=positive')
                    ui.button('拒否', on_click=lambda _, pid=o['player_id']: reject_transfer_offer(pid)).props('dense color=negative')


def render_save():
    with ui.card().classes('w-full mobile-card'):
        ui.label('セーブ管理').classes('section-title')
        ui.button('保存', on_click=save_game).classes('w-full mobile-btn')
        ui.button('読込', on_click=load_game).classes('w-full mobile-btn')
        ui.button('JSON書き出し', on_click=export_save).classes('w-full mobile-btn')
        ui.upload(on_upload=import_save, label='JSON読み込み').classes('w-full')


def render_content():
    content_container.clear()
    with content_container:
        section = nav_state['section']
        if section == 'dashboard':
            render_dashboard()
        elif section == 'squad':
            render_squad()
        elif section == 'match':
            render_match()
        elif section == 'standings':
            render_standings()
        elif section == 'youth':
            render_youth()
        elif section == 'cup':
            render_cup()
        elif section == 'scout':
            render_scout()
        elif section == 'transfer':
            render_transfer()
        elif section == 'save':
            render_save()


def refresh_ui():
    if game_state['selected_country'] != country_select.value:
        country_select.value = game_state['selected_country']

    clubs = []
    for div_key in ['1', '2', '3']:
        for t in sort_table(game_state['divisions'][div_key]['teams']):
            clubs.append(f'Div {div_key} | {t["name"]}')
    club_select.options = clubs

    if game_state['selected_club']:
        team = get_team(game_state['selected_club'])
        if team:
            club_select.value = f'Div {team["division"]} | {team["name"]}'
    else:
        club_select.value = None

    render_world_setup()
    render_club_picker()
    render_status()
    render_content()


game_state = build_world('England')

ui.add_head_html('''
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<style>
    body {
        background: #0f172a;
        color: #f8fafc;
    }
    .nicegui-content {
        max-width: 860px;
        margin: 0 auto;
        padding: 74px 12px 92px 12px;
        box-sizing: border-box;
    }
    .mobile-card {
        border-radius: 14px;
        margin-bottom: 10px;
        background: #182334 !important;
        color: #f8fafc !important;
        border: 1px solid rgba(148, 163, 184, 0.14);
    }
    .mobile-btn {
        min-height: 44px;
        font-weight: 700;
    }
    .footer-nav {
        padding-bottom: env(safe-area-inset-bottom);
        background: rgba(15, 23, 42, 0.96);
        backdrop-filter: blur(10px);
        border-top: 1px solid rgba(148, 163, 184, 0.18);
    }
    .strong-text {
        color: #ffffff !important;
        font-weight: 700;
    }
    .body-text {
        color: #f1f5f9 !important;
    }
    .muted-text {
        color: #cbd5e1 !important;
    }
    .section-title {
        color: #ffffff !important;
        font-size: 1.05rem;
        font-weight: 700;
    }
    .status-card {
        background: #1d2a3f !important;
    }
    .highlight-card {
        border: 1px solid rgba(96, 165, 250, 0.45);
        background: #1b2940 !important;
    }
</style>
''')

with ui.header(fixed=True).classes('items-center justify-between bg-slate-900 text-white'):
    ui.label(APP_NAME).classes('text-h6')
    ui.label('モバイル版').classes('text-caption')

world_setup_container = ui.column().classes('w-full')

with ui.card().classes('w-full mobile-card').style('display:none'):
    country_select = ui.select(
        options=list(COUNTRIES.keys()),
        value=game_state['selected_country'],
        label='国を選択',
    ).classes('w-full')
    club_select = ui.select(
        options=[],
        value=None,
        label='クラブを選択',
        on_change=lambda e: on_select_club(e.value),
    ).classes('w-full')
    club_picker_container = ui.column().classes('w-full')

status_container = ui.column().classes('w-full')
content_container = ui.column().classes('w-full')

with ui.footer(fixed=True).classes('footer-nav'):
    with ui.row().classes('w-full no-wrap justify-around items-center gap-1'):
        for key, label in [
            ('dashboard', 'ホーム'),
            ('squad', 'チーム'),
            ('match', '試合'),
            ('standings', '順位'),
            ('youth', 'ユース'),
            ('cup', 'カップ'),
            ('scout', 'スカウト'),
            ('transfer', '移籍'),
            ('save', '保存'),
        ]:
            ui.button(
                label,
                on_click=lambda _, k=key: (nav_state.__setitem__('section', k), render_content()),
            ).props('flat dense').classes('text-xs text-white')

refresh_ui()

ui.run(host='0.0.0.0', port=PORT)
