from nicegui import ui
import random, math, copy, json

# =========================================================

# 定数・設定

# =========================================================

APP_TITLE    = ‘Club Strive v6’
MAX_SQUAD    = 25
MIN_YOUTH    = 10
MAX_YOUTH    = 15
SEASON_WEEKS = 36
CUP_START    = 10
TRANSFER_WINDOWS = [(1,6),(19,22)]
SALARY_CAP   = {‘D1’:420000,‘D2’:270000,‘D3’:165000}

COUNTRIES = [‘England’,‘Spain’,‘Germany’,‘Italy’,‘France’,‘Brazil’,‘Japan’]
POSITIONS = [‘GK’,‘DF’,‘MF’,‘FW’]
LEAGUE_STRENGTH = {‘England’:92,‘Spain’:90,‘Germany’:88,‘Italy’:87,‘France’:86,‘Brazil’:85,‘Japan’:78}

PLAY_STYLES = {
‘FW’:[‘ストライカー’,‘ポーチャー’,‘ターゲットマン’,‘カウンターランナー’,‘トリックスター’],
‘MF’:[‘プレイメーカー’,‘ボックス・トゥ・ボックス’,‘ディストラクター’,‘チャンスクリエイター’,‘シャドーストライカー’],
‘DF’:[‘タックルマスター’,‘スイーパー’,‘ビルドアップ型’,‘空中戦マスター’],
‘GK’:[‘ショットストッパー’,‘スイーパーキーパー’],
}
PERSONALITIES = [‘真面目’,‘野心家’,‘ムードメーカー’,‘気分屋’,‘忠誠心高い’,‘努力家’,‘スター気質’,‘短気’,‘チームプレイヤー’]
YOUTH_POLICIES = {
‘バランス’:{‘SPD’:1.00,‘TEC’:1.00,‘PHY’:1.00},
‘スピード’:{‘SPD’:1.15,‘TEC’:0.95,‘PHY’:1.00},
‘テクニック’:{‘SPD’:0.95,‘TEC’:1.15,‘PHY’:0.95},
‘フィジカル’:{‘SPD’:0.95,‘TEC’:0.95,‘PHY’:1.15},
}
TACTICS = {
‘バランス’:{‘atk’:1.00,‘def’:1.00},
‘攻撃的’:{‘atk’:1.12,‘def’:0.90},
‘守備的’:{‘atk’:0.90,‘def’:1.12},
‘プレス’:{‘atk’:1.06,‘def’:1.06},
‘カウンター’:{‘atk’:1.08,‘def’:1.04},
}
FORMATIONS = {
‘4-3-3’:{‘GK’:1,‘DF’:4,‘MF’:3,‘FW’:3},
‘4-4-2’:{‘GK’:1,‘DF’:4,‘MF’:4,‘FW’:2},
‘3-5-2’:{‘GK’:1,‘DF’:3,‘MF’:5,‘FW’:2},
‘5-3-2’:{‘GK’:1,‘DF’:5,‘MF’:3,‘FW’:2},
‘4-2-3-1’:{‘GK’:1,‘DF’:4,‘MF’:5,‘FW’:1},
}
MANAGER_SKILLS = {
‘戦術家’:{‘desc’:‘戦術補正+10%’,‘req_exp’:30},
‘育成型’:{‘desc’:‘ユース成長+15%’,‘req_exp’:50},
‘モチベーター’:{‘desc’:‘morale+5/週’,‘req_exp’:40},
‘スカウト眼’:{‘desc’:‘スカウット質+3’,‘req_exp’:35},
‘財務手腕’:{‘desc’:‘スポンサー+10%’,‘req_exp’:60},
‘鉄のメンタル’:{‘desc’:‘評価下落-50%’,‘req_exp’:45},
}
PLAYER_STATES = {
‘normal’:{‘label’:‘通常’,‘goal_mult’:1.00,‘assist_mult’:1.00},
‘hot’:{‘label’:‘🔥覚醒’,‘goal_mult’:1.40,‘assist_mult’:1.30},
‘slump’:{‘label’:‘📉スランプ’,‘goal_mult’:0.65,‘assist_mult’:0.75},
}
CAPTAIN_EFFECTS = {
‘ムードメーカー’:{‘locker_room’:5,‘morale’:3},
‘真面目’:{‘locker_room’:2,‘morale’:2},
‘忠誠心高い’:{‘locker_room’:3,‘fan_happiness’:2},
‘チームプレイヤー’:{‘locker_room’:4,‘morale’:2},
‘スター気質’:{‘club_brand’:3,‘fan_base’:100},
‘短気’:{‘locker_room’:-2,‘morale’:-1},
}
WEATHER = {
‘晴れ’:{‘atk_mod’:1.00,‘def_mod’:1.00,‘injury_mod’:1.00,‘att_mod’:1.05},
‘曇り’:{‘atk_mod’:1.00,‘def_mod’:1.00,‘injury_mod’:1.00,‘att_mod’:1.00},
‘雨’:{‘atk_mod’:0.93,‘def_mod’:1.03,‘injury_mod’:1.15,‘att_mod’:0.90},
‘強風’:{‘atk_mod’:0.88,‘def_mod’:1.05,‘injury_mod’:1.10,‘att_mod’:0.85},
‘雪’:{‘atk_mod’:0.80,‘def_mod’:1.08,‘injury_mod’:1.25,‘att_mod’:0.75},
}

# ランダムイベント定義

RANDOM_EVENTS = [
{‘id’:‘scandal’,‘text’:’{name}がスキャンダル報道！’,‘choices’:[‘謝罪声明を出す’,‘沈黙を保つ’,‘完全否定する’],‘effects’:{‘謝罪声明を出す’:{‘fan_happiness’:-3,‘locker_room_mood’:3,‘manager_rating’:2},‘沈黙を保つ’:{‘fan_happiness’:-6,‘board_rating’:-2},‘完全否定する’:{‘fan_happiness’:-4,‘board_rating’:3,‘morale_player’:5}}},
{‘id’:‘rival_poach’,‘text’:‘ライバル{rival}が{name}の引き抜きを企てている’,‘choices’:[‘即刻契約延長’,‘無視する’,‘売却を検討’],‘effects’:{‘即刻契約延長’:{‘budget’:-50000,‘morale_player’:10,‘unhappiness_player’:-20},‘無視する’:{‘unhappiness_player’:15},‘売却を検討’:{‘fan_happiness’:-4,‘morale_player’:-10}}},
{‘id’:‘ob_coach’,‘text’:‘クラブOB {name}がコーチ就任を申し出ている’,‘choices’:[‘採用する(無料)’,‘断る’],‘effects’:{‘採用する(無料)’:{‘locker_room_mood’:5,‘fan_happiness’:4,‘new_staff’:True},‘断る’:{}}},
{‘id’:‘local_hero’,‘text’:‘地元出身の{name}がスタメン定着！ファン熱狂’,‘choices’:[‘アピール’],‘effects’:{‘アピール’:{‘fan_happiness’:6,‘fan_base’:500,‘club_brand’:2}}},
{‘id’:‘anniversary’,‘text’:‘クラブ創立記念日！特別試合を開催’,‘choices’:[‘盛大に祝う’,‘通常通り’],‘effects’:{‘盛大に祝う’:{‘fan_happiness’:8,‘fan_base’:1000,‘budget’:-30000},‘通常通り’:{‘fan_happiness’:3}}},
{‘id’:‘youth_bigclub’,‘text’:‘ビッグクラブが育成選手{name}を狙っている’,‘choices’:[‘全力で守る(契約延長)’,‘交渉に応じる’],‘effects’:{‘全力で守る(契約延長)’:{‘budget’:-40000,‘locker_room_mood’:3},‘交渉に応じる’:{‘transfer_youth’:True,‘fan_happiness’:-2}}},
{‘id’:‘intl_return_boost’,‘text’:‘代表から帰還した{name}が一回り成長した’,‘choices’:[‘歓迎する’],‘effects’:{‘歓迎する’:{‘attr_boost’:True,‘morale_player’:8}}},
{‘id’:‘media_praise’,‘text’:‘メディアが監督の采配を絶賛！’,‘choices’:[‘コメントする’],‘effects’:{‘コメントする’:{‘manager_rating’:5,‘fan_happiness’:3,‘club_brand’:2}}},
{‘id’:‘training_accident’,‘text’:‘トレーニング中に{name}が軽傷’,‘choices’:[‘安静にさせる’],‘effects’:{‘安静にさせる’:{‘injury_minor’:True}}},
{‘id’:‘fan_protest’,‘text’:‘ファンが成績に不満でデモ！’,‘choices’:[‘謝罪する’,‘強気でいく’],‘effects’:{‘謝罪する’:{‘fan_happiness’:4,‘board_rating’:-2},‘強気でいく’:{‘fan_happiness’:-3,‘manager_rating’:3}}},
]

ACHIEVEMENTS = {
‘first_win’:{‘name’:‘初勝利’,‘desc’:‘リーグ戦で初勝利’,‘icon’:‘⚽’},
‘first_title’:{‘name’:‘初優勝’,‘desc’:‘リーグ優勝’,‘icon’:‘🏆’},
‘cup_winner’:{‘name’:‘カップ制覇’,‘desc’:‘国内カップ優勝’,‘icon’:‘🥇’},
‘unbeaten_5’:{‘name’:‘5連勝’,‘desc’:‘5試合連続勝利’,‘icon’:‘🔥’},
‘youth_promoted’:{‘name’:‘育成の鬼’,‘desc’:‘ユース昇格5人達成’,‘icon’:‘🌱’},
‘season3’:{‘name’:‘3年生存’,‘desc’:‘3シーズン続投’,‘icon’:‘📅’},
‘intl_winner’:{‘name’:‘国際制覇’,‘desc’:‘国際大会優勝’,‘icon’:‘🌍’},
‘promoted’:{‘name’:‘昇格！’,‘desc’:‘ディビジョン昇格’,‘icon’:‘🔺’},
‘rich_club’:{‘name’:‘大富豪’,‘desc’:‘予算$5,000,000超’,‘icon’:‘💰’},
‘wonder_scout’:{‘name’:‘名スカウト’,‘desc’:‘ウォンダーキッド発見3人’,‘icon’:‘🌟’},
‘max_facility’:{‘name’:‘最高施設’,‘desc’:‘全施設Lv5達成’,‘icon’:‘🏗️’},
‘career_move’:{‘name’:‘渡り鳥監督’,‘desc’:‘別クラブへ転身’,‘icon’:‘✈️’},
‘pk_hero’:{‘name’:‘PKの英雄’,‘desc’:‘PKシューターアウトを制した’,‘icon’:‘🥅’},
}

COUNTRY_NAME_POOLS = {
‘England’:{‘first’:[‘Jack’,‘Noah’,‘Oliver’,‘Harry’,‘George’,‘Leo’,‘James’,‘Charlie’,‘Oscar’,‘Alfie’],‘last’:[‘Smith’,‘Brown’,‘Taylor’,‘Johnson’,‘Walker’,‘Wilson’,‘Davis’,‘Miller’,‘Clark’,‘Hall’],‘clubs’:[‘London’,‘Manchester’,‘Merseyside’,‘Northbridge’,‘Royal’,‘River’,‘Eastford’,‘Westham’,‘Redcastle’,‘Blueport’]},
‘Spain’:{‘first’:[‘Pablo’,‘Alvaro’,‘Hugo’,‘Diego’,‘Javier’,‘Adrian’,‘Sergio’,‘Mario’,‘Iker’,‘Ruben’],‘last’:[‘Garcia’,‘Lopez’,‘Martinez’,‘Sanchez’,‘Perez’,‘Gomez’,‘Diaz’,‘Torres’,‘Ruiz’,‘Navarro’],‘clubs’:[‘Madrid’,‘Catalunya’,‘Valencia’,‘Sevilla’,‘Bilbao’,‘Costa’,‘Atletico’,‘Real’,‘Granada’,‘Murcia’]},
‘Germany’:{‘first’:[‘Lukas’,‘Leon’,‘Felix’,‘Max’,‘Finn’,‘Jonas’,‘Noah’,‘Paul’,‘Tim’,‘Moritz’],‘last’:[‘Muller’,‘Schmidt’,‘Schneider’,‘Fischer’,‘Weber’,‘Meyer’,‘Wagner’,‘Becker’,‘Hoffmann’,‘Koch’],‘clubs’:[‘Berlin’,‘Munich’,‘Rhein’,‘Nord’,‘Union’,‘Eintracht’,‘Bayern’,‘Ruhr’,‘Hamburg’,‘Stuttgart’]},
‘Italy’:{‘first’:[‘Luca’,‘Marco’,‘Matteo’,‘Davide’,‘Andrea’,‘Federico’,‘Stefano’,‘Giorgio’,‘Antonio’,‘Simone’],‘last’:[‘Rossi’,‘Russo’,‘Ferrari’,‘Esposito’,‘Romano’,‘Gallo’,‘Costa’,‘Fontana’,‘Conti’,‘Greco’],‘clubs’:[‘Milano’,‘Roma’,‘Torino’,‘Napoli’,‘Lazio’,‘Verona’,‘Atletico’,‘Inter’,‘Calcio’,‘Fiora’]},
‘France’:{‘first’:[‘Lucas’,‘Nathan’,‘Hugo’,‘Leo’,‘Gabriel’,‘Louis’,‘Enzo’,‘Arthur’,‘Theo’,‘Jules’],‘last’:[‘Martin’,‘Bernard’,‘Dubois’,‘Thomas’,‘Robert’,‘Richard’,‘Petit’,‘Durand’,‘Leroy’,‘Moreau’],‘clubs’:[‘Paris’,‘Lyon’,‘Marseille’,‘Monaco’,‘Nord’,‘Bleu’,‘Rouge’,‘Avenir’,‘Royal’,‘Provence’]},
‘Brazil’:{‘first’:[‘Lucas’,‘Joao’,‘Mateus’,‘Gabriel’,‘Rafael’,‘Pedro’,‘Thiago’,‘Bruno’,‘Felipe’,‘Diego’],‘last’:[‘Silva’,‘Souza’,‘Costa’,‘Santos’,‘Oliveira’,‘Pereira’,‘Almeida’,‘Gomes’,‘Lima’,‘Rocha’],‘clubs’:[‘Rio’,‘Samba’,‘Verde’,‘Cruzeiro’,‘Porto’,‘Atletico’,‘Nova’,‘Sol’,‘Santa’,‘Bahia’]},
‘Japan’:{‘first’:[‘Haruto’,‘Ren’,‘Yuto’,‘Sota’,‘Kaito’,‘Riku’,‘Takumi’,‘Daiki’,‘Yuma’,‘Shota’],‘last’:[‘Sato’,‘Suzuki’,‘Takahashi’,‘Tanaka’,‘Ito’,‘Yamamoto’,‘Watanabe’,‘Nakamura’,‘Kobayashi’,‘Kato’],‘clubs’:[‘Blue’,‘Red’,‘Phoenix’,‘Ocean’,‘North’,‘East’,‘West’,‘South’,‘Rising’,‘United’]},
}
STAFF_TYPES=[‘ヘッドコーチ’,‘スカウト’,‘フィジオ’,‘アシスタント’]
FACILITY_TYPES=[‘youth’,‘training’,‘medical’,‘scouting’,‘stadium’]
BASE_ATTRS={
‘GK’:{‘SPD’:45,‘TEC’:52,‘PAS’:50,‘PHY’:62,‘SHT’:30,‘DEF’:72,‘MEN’:60,‘STA’:75},
‘DF’:{‘SPD’:56,‘TEC’:53,‘PAS’:54,‘PHY’:66,‘SHT’:38,‘DEF’:68,‘MEN’:58,‘STA’:72},
‘MF’:{‘SPD’:60,‘TEC’:63,‘PAS’:65,‘PHY’:58,‘SHT’:52,‘DEF’:52,‘MEN’:60,‘STA’:70},
‘FW’:{‘SPD’:67,‘TEC’:61,‘PAS’:54,‘PHY’:62,‘SHT’:68,‘DEF’:35,‘MEN’:62,‘STA’:68},
}
OVR_WEIGHTS={
‘GK’:{‘SPD’:0.05,‘TEC’:0.10,‘PAS’:0.08,‘PHY’:0.15,‘SHT’:0.02,‘DEF’:0.35,‘MEN’:0.13,‘STA’:0.12},
‘DF’:{‘SPD’:0.10,‘TEC’:0.12,‘PAS’:0.12,‘PHY’:0.18,‘SHT’:0.05,‘DEF’:0.25,‘MEN’:0.10,‘STA’:0.08},
‘MF’:{‘SPD’:0.12,‘TEC’:0.18,‘PAS’:0.20,‘PHY’:0.12,‘SHT’:0.12,‘DEF’:0.10,‘MEN’:0.08,‘STA’:0.08},
‘FW’:{‘SPD’:0.15,‘TEC’:0.15,‘PAS’:0.10,‘PHY’:0.12,‘SHT’:0.28,‘DEF’:0.03,‘MEN’:0.10,‘STA’:0.07},
}
ATTR_ICONS={‘SPD’:‘💨’,‘TEC’:‘⚽’,‘PAS’:‘🎯’,‘PHY’:‘💪’,‘SHT’:‘🔫’,‘DEF’:‘🛡️’,‘MEN’:‘🧠’,‘STA’:‘❤️’}

game_state=None
nav_state={‘tab’:‘dashboard’,‘halftime_mode’:False,‘live_mode’:False,‘live_events’:[]}
dashboard_box=status_box=None

# =========================================================

# ユーティリティ

# =========================================================

def clamp(v,lo,hi): return max(lo,min(v,hi))
def avg(vals): return sum(vals)/len(vals) if vals else 0
def wc(items,weights): return random.choices(items,weights=weights,k=1)[0]
def fmt_m(v): return f’${int(v):,}’
def find_team(name):
for d in game_state[‘divisions’]:
for t in game_state[‘divisions’][d]:
if t[‘name’]==name: return t
return None
def get_sel(): return find_team(game_state[‘selected_club’]) if game_state[‘selected_club’] else None
def all_players(youth=False):
pl=[]
for d in game_state[‘divisions’]:
for t in game_state[‘divisions’][d]:
pl+=t[‘players’]
if youth: pl+=t[‘youth’]
return pl
def player_by_id(pid):
for p in all_players(True):
if p[‘id’]==pid: return p
for d in game_state[‘divisions’]:
for t in game_state[‘divisions’][d]:
for p in t.get(‘loan_in’,[]):
if p[‘id’]==pid: return p
return None
def div_of(name):
for d in game_state[‘divisions’]:
for t in game_state[‘divisions’][d]:
if t[‘name’]==name: return d
return None
def sorted_table(div):
return sorted(game_state[‘divisions’][div],key=lambda t:(t[‘season_stats’][‘pts’],t[‘season_stats’][‘gd’],t[‘season_stats’][‘gf’],t[‘reputation’]),reverse=True)
def add_news(txt,cat=‘general’):
game_state[‘news’].insert(0,{‘text’:txt,‘cat’:cat,‘season’:game_state[‘season’],‘week’:game_state[‘week’]})
game_state[‘news’]=game_state[‘news’][:200]
def add_fin(cat,amt,note=’’):
game_state.setdefault(‘finance_logs’,[]).insert(0,{‘season’:game_state[‘season’],‘week’:game_state[‘week’],‘cat’:cat,‘amt’:amt,‘note’:note})
game_state[‘finance_logs’]=game_state[‘finance_logs’][:200]
def add_sf(cat,amt):
game_state[‘season_finance’][cat]=game_state[‘season_finance’].get(cat,0)+amt
def has_skill(s): return s in game_state.get(‘manager_skills’,[])
def gain_exp(amt):
game_state[‘manager_exp’]=game_state.get(‘manager_exp’,0)+amt
pts=sum(1 for t in [50,120,220,350,500] if game_state[‘manager_exp’]>=t)
game_state[‘manager_skill_points’]=max(0,pts-len(game_state.get(‘manager_skills’,[])))
def in_transfer_window():
w=game_state[‘week’]
return any(lo<=w<=hi for lo,hi in TRANSFER_WINDOWS)
def get_weather(): return game_state.get(‘current_weather’,‘晴れ’)
def roll_weather():
w=wc([‘晴れ’,‘曇り’,‘雨’,‘強風’,‘雪’],[40,25,20,10,5])
game_state[‘current_weather’]=w; return w
def check_achievement(key):
done=game_state.setdefault(‘achievements’,[])
if key not in done and key in ACHIEVEMENTS:
done.append(key); a=ACHIEVEMENTS[key]
add_news(f’🏅実績解除: {a[“icon”]}{a[“name”]} — {a[“desc”]}’,‘club’)

# =========================================================

# 選手・チーム生成

# =========================================================

def _recompute(p):
w=OVR_WEIGHTS.get(p[‘pos’],{k:0.125 for k in p[‘attrs’]})
p[‘overall’]=clamp(int(sum(p[‘attrs’].get(k,50)*v for k,v in w.items())),35,99)
p[‘value’]=int(p[‘overall’]*2500+p[‘potential’]*1800)
p[‘wage’]=int(1800+p[‘overall’]*140)

def gen_player(country,club,idx,youth=False):
pos=random.choice(POSITIONS)
attrs=copy.deepcopy(BASE_ATTRS[pos])
lmod=(LEAGUE_STRENGTH.get(country,80)-80)*0.1
for k in attrs: attrs[k]+=random.randint(-8,8)+int(lmod)
if youth:
pol=YOUTH_POLICIES.get(game_state[‘youth_policy’] if game_state else ‘バランス’,YOUTH_POLICIES[‘バランス’])
attrs[‘SPD’]=int(attrs[‘SPD’]*pol[‘SPD’]); attrs[‘TEC’]=int(attrs[‘TEC’]*pol[‘TEC’])
attrs[‘PAS’]=int(attrs[‘PAS’]*pol[‘TEC’]); attrs[‘PHY’]=int(attrs[‘PHY’]*pol[‘PHY’])
fac=game_state[‘facilities’][‘youth’] if game_state else 1
for k in attrs: attrs[k]-=random.randint(1,max(2,6-min(4,fac)))
for k in attrs: attrs[k]=clamp(attrs[k],30,95)
age=random.randint(16,18) if youth else random.randint(18,35)
p={
‘id’:f’{club}*{idx}*{random.randint(10000,99999)}’,
‘name’:f’{random.choice(COUNTRY_NAME_POOLS[country][“first”])} {random.choice(COUNTRY_NAME_POOLS[country][“last”])}’,
‘club’:club,‘nationality’:country,‘pos’:pos,‘age’:age,‘attrs’:attrs,
‘overall’:50,‘potential’:0,
‘playstyle’:random.choice(PLAY_STYLES[pos]),
‘personality’:random.choice(PERSONALITIES),
‘trait’:wc([‘なし’,‘勝負師’,‘ムードメーカー’,‘スペ体質’],[60,15,15,10]),
‘growth_type’:wc([‘早熟’,‘標準’,‘晩成’],[30,50,20]) if youth else None,
‘contract_years’:random.randint(2,4) if youth else random.randint(1,5),
‘unhappiness’:0,‘injury_weeks’:0,‘injury_severity’:‘なし’,
‘stamina’:100,‘morale’:50,‘is_wonderkid’:False,‘transfer_request’:False,
‘state’:‘normal’,‘state_weeks’:0,‘intl_weeks’:0,
‘stats’:{‘apps’:0,‘goals’:0,‘assists’:0,‘mom’:0,‘clean_sheets’:0,‘yellow_cards’:0,‘red_cards’:0,‘shots’:0,‘saves’:0,‘tackles’:0},
‘value’:0,‘wage’:0,
‘loan_club’:None,‘loan_origin’:None,‘loan_weeks’:0,
‘buyback_fee’:None,‘buyback_club’:None,
‘retiring’:False,‘training_focus’:None,
‘has_agent’:random.random()<0.3,‘agent_fee_pct’:random.choice([5,8,10]),
# スカウトグレード（不確実性）
‘scout_grade’:wc([‘A’,‘B’,‘C’,‘D’,‘E’],[10,20,35,25,10]),
# コンバート
‘original_pos’:pos,‘convert_weeks’:0,
# 希望ポジション
‘preferred_pos’:pos,
# プレー頻度希望
‘role_wish’:‘どちらでも’,  # 主力/控えでも/主力のみ
# 代表帰還ブースト
‘intl_boost_pending’:False,
# 地元出身フラグ
‘is_local’:random.random()<0.15,
}
_recompute(p); p[‘potential’]=clamp(p[‘overall’]+random.randint(5,20),p[‘overall’],95)
if youth and random.random()<0.02:
p[‘potential’]=random.randint(88,94)
for k in p[‘attrs’]: p[‘attrs’][k]=clamp(p[‘attrs’][k]+random.randint(6,12),50,95)
p[‘is_wonderkid’]=True
_recompute(p); return p

def create_team(country,name,rmin=50,rmax=75):
players=[gen_player(country,name,i) for i in range(18)]
youth=[gen_player(country,name,1000+i,True) for i in range(random.randint(MIN_YOUTH,MAX_YOUTH))]
return {
‘name’:name,‘country’:country,‘players’:players,‘youth’:youth,‘loan_in’:[],
‘budget’:random.randint(700000,1600000),
‘reputation’:random.randint(rmin,rmax),
‘fan_base’:random.randint(8000,20000),
‘stadium_capacity’:random.randint(12000,35000),
‘tactic’:‘バランス’,‘formation’:‘4-4-2’,
‘rivals’:[],‘board_expectation’:‘中位確保’,
‘derby_record’:{},‘sponsor’:None,‘player_season_goal’:None,
‘captain_id’:None,‘vip_level’:0,‘rank_history’:[],
‘starting_xi’:[],‘preseason_done’:False,
‘board_meeting_week’:8,‘naming_rights’:None,
‘chemistry’:50,‘budget_transfer’:0,‘budget_facility’:0,‘budget_staff’:0,
# PKシューター・セットプレー担当
‘pk_taker_id’:None,‘ck_taker_id’:None,‘fk_taker_id’:None,
# 監督キャリア用
‘manager_offer_pending’:False,
# ローン記録
‘bank_loan’:None,
# 歴史記録
‘season_history’:[],
}

def build_league(country):
used=set()
def rc(rmin,rmax): return [create_team(country,_rname(country,used),rmin,rmax) for _ in range(10)]
divs={‘D1’:rc(62,78),‘D2’:rc(54,70),‘D3’:rc(46,64)}
for div in divs:
tms=divs[div]
for i in range(0,len(tms),2):
if i+1<len(tms):
tms[i][‘rivals’].append(tms[i+1][‘name’]); tms[i+1][‘rivals’].append(tms[i][‘name’])
for t in tms:
if div==‘D1’: t[‘board_expectation’]=wc([‘優勝争い’,‘上位進出’,‘残留’],[20,35,45])
elif div==‘D2’: t[‘board_expectation’]=wc([‘昇格争い’,‘中位確保’,‘残留’],[30,40,30])
else: t[‘board_expectation’]=wc([‘昇格’,‘上位進出’,‘中位確保’],[30,35,35])
return divs

def _rname(country,used):
pool=COUNTRY_NAME_POOLS[country][‘clubs’]
suffs=[‘FC’,‘United’,‘City’,‘SC’,‘Athletic’,‘Club’]
while True:
n=f’{random.choice(pool)} {random.choice(suffs)}’
if n not in used: used.add(n); return n

def build_world(country):
divs=build_league(country)
return {
‘season’:1,‘week’:1,
‘selected_country’:country,‘selected_club’:’’,‘selected_player_id’:’’,
‘divisions’:divs,
‘news’:[{‘text’:f’{country}で新しい世界を作成しました’,‘cat’:‘general’,‘season’:1,‘week’:1}],
‘transfer_offers’:[],‘foreign_offers’:[],‘loan_offers’:[],‘loan_out_requests’:[],
‘season_awards’:None,‘history_awards’:[],‘club_hall_of_fame’:[],‘last_match’:None,
‘manager_rating’:50,‘board_rating’:50,‘locker_room_mood’:50,‘fan_happiness’:50,‘club_brand’:50,
‘manager_exp’:0,‘manager_skill_points’:0,‘manager_skills’:[],
# 監督キャリア
‘manager_career’:[],  # [{club, season, div, rank}]
‘manager_career_offers’:[],
‘facilities’:{‘youth’:1,‘training’:1,‘medical’:1,‘scouting’:1,‘stadium’:1},
‘staff’:[],‘international_cup’:None,
‘youth_policy’:‘バランス’,‘youth_decision_queue’:[],
‘season_finance’:{k:0 for k in [‘sponsor’,‘matchday’,‘transfers_in’,‘transfers_out’,‘prize’,‘wages’,‘facility’,‘staff’,‘broadcast’,‘merch’,‘naming_rights’,‘preseason’,‘loan_interest’,‘insurance’]},
‘pending_sponsor_negotiation’:None,
‘manager_fired’:False,‘season_goal_declared’:False,
‘domestic_cup’:None,‘pending_press’:False,‘press_effect’:None,
‘intl_call_queue’:[],‘financial_crisis’:False,
‘rank_history’:[],‘current_weather’:‘晴れ’,
‘preseason_phase’:True,
‘pending_lineup’:False,‘halftime_data’:None,
‘pending_board_meeting’:False,
‘buyout_offer’:None,‘achievements’:[],‘training_results’:[],
‘win_streak’:0,‘clean_streak’:0,‘youth_promoted_count’:0,‘wonderkid_found’:0,
# ランダムイベントキュー
‘pending_event’:None,
‘event_history’:[],
# テキスト実況
‘live_commentary’:[],
# クラブ歴史書
‘club_history’:[],
‘news_filter’:‘全て’,
# 複数週一括進行中フラグ
‘bulk_advancing’:False,‘bulk_weeks_left’:0,
# 銀行ローン
‘bank_loans’:[],
# 選手保険
‘injury_insurance_active’:False,
# 肖像権収入
‘portrait_income_weekly’:0,
# 海外スカウト派遣
‘overseas_scout’:None,
# win_bonus支払い記録
‘last_match_won’:False,
}

def init_stats():
for d in game_state[‘divisions’]:
for t in game_state[‘divisions’][d]:
if ‘season_stats’ not in t:
t[‘season_stats’]={‘p’:0,‘w’:0,‘d’:0,‘l’:0,‘gf’:0,‘ga’:0,‘gd’:0,‘pts’:0}

# =========================================================

# スターティングイレブン

# =========================================================

def best_lineup(team,override_xi=None):
pool=team[‘players’]+team.get(‘loan_in’,[])
avail=[p for p in pool if p[‘injury_weeks’]<=0 and p.get(‘intl_weeks’,0)<=0]
if not avail: return pool[:11]
xi_ids=override_xi or team.get(‘starting_xi’,[])
if xi_ids:
xi=[p for p in avail if p[‘id’] in xi_ids]
if len(xi)<11:
rest=sorted([p for p in avail if p[‘id’] not in xi_ids],key=lambda p:p[‘overall’],reverse=True)
xi+=rest[:11-len(xi)]
return xi[:11]
req=FORMATIONS.get(team.get(‘formation’,‘4-4-2’),FORMATIONS[‘4-4-2’])
lineup=[]; rem=list(avail)
for pos,cnt in req.items():
chosen=sorted([p for p in rem if p[‘pos’]==pos],key=lambda p:p[‘overall’],reverse=True)[:cnt]
lineup+=chosen
for p in chosen: rem.remove(p)
if len(lineup)<11:
lineup+=sorted(rem,key=lambda p:p[‘overall’],reverse=True)[:11-len(lineup)]
return lineup[:11]

def set_starting_xi(player_ids):
sel=get_sel()
if not sel: return
sel[‘starting_xi’]=player_ids[:11]; game_state[‘pending_lineup’]=False
add_news(‘スターティングイレブンを設定’,‘match’); refresh_ui()

def auto_lineup():
sel=get_sel()
if not sel: return
sel[‘starting_xi’]=[]; game_state[‘pending_lineup’]=False
add_news(‘ラインナップを自動選出に設定’,‘match’); refresh_ui()

# =========================================================

# 試合強度計算（ホーム補正追加）

# =========================================================

def team_str(team,opp=None,tactic_override=None,is_home=False):
lu=best_lineup(team)
if not lu: return 40
base=avg([p[‘overall’] for p in lu])
league_b=(LEAGUE_STRENGTH.get(team.get(‘country’,‘England’),80)-80)*0.05
morale_b=avg([p[‘morale’] for p in lu])*0.05
stamina_b=avg([p[‘stamina’] for p in lu])*0.03
style_b=sum({‘ストライカー’:0.30,‘ポーチャー’:0.22,‘プレイメーカー’:0.25,‘ディストラクター’:0.22,‘タックルマスター’:0.18,‘ショットストッパー’:0.15}.get(p.get(‘playstyle’,’’),0)+({‘勝負師’:0.12,‘ムードメーカー’:0.08}.get(p.get(‘trait’,’’),0)) for p in lu)
derby_b=2.5 if opp and opp[‘name’] in team.get(‘rivals’,[]) else 0
# ホーム補正
home_b=2.5 if is_home else 0
fac_b=game_state[‘facilities’][‘training’]*0.8+game_state[‘facilities’][‘medical’]*0.2
tn=tactic_override or team.get(‘tactic’,‘バランス’)
tac=TACTICS.get(tn,TACTICS[‘バランス’])
tac_b=(tac[‘atk’]+tac[‘def’])/2*base*0.05-base*0.05
staff_b=sum(s[‘skill’]*0.01 for s in game_state[‘staff’] if s[‘type’]==‘ヘッドコーチ’)
staff_b+=sum(s[‘skill’]*0.005 for s in game_state[‘staff’] if s[‘type’]==‘フィジオ’)
brand_b=(game_state[‘club_brand’]-50)*0.02
frm=FORMATIONS.get(team.get(‘formation’,‘4-4-2’),FORMATIONS[‘4-4-2’])
pos_cnt={p[‘pos’]:0 for p in lu}
for p in lu: pos_cnt[p[‘pos’]]=pos_cnt.get(p[‘pos’],0)+1
frm_b=sum(0.3 for pos,cnt in frm.items() if pos_cnt.get(pos,0)>=cnt)
skill_b=base*0.10 if has_skill(‘戦術家’) else 0
cap_id=team.get(‘captain_id’)
cap_b=0
if cap_id:
cap=next((p for p in lu if p[‘id’]==cap_id),None)
if cap: cap_b=CAPTAIN_EFFECTS.get(cap[‘personality’],{}).get(‘morale’,0)*0.1
# セットプレー担当者ボーナス（CK/FKのTEC・SHT属性を反映）
setpiece_b=0
ck_id=team.get(‘ck_taker_id’)
fk_id=team.get(‘fk_taker_id’)
if ck_id:
ck=next((p for p in lu if p[‘id’]==ck_id),None)
if ck: setpiece_b+=ck[‘attrs’].get(‘TEC’,50)*0.015
if fk_id:
fk=next((p for p in lu if p[‘id’]==fk_id),None)
if fk: setpiece_b+=fk[‘attrs’].get(‘SHT’,50)*0.012
state_b=(avg([1.1 if p.get(‘state’)==‘hot’ else(0.9 if p.get(‘state’)==‘slump’ else 1.0) for p in lu])-1.0)*base*0.05
chem_b=(team.get(‘chemistry’,50)-50)*0.01
weather=WEATHER.get(get_weather(),WEATHER[‘晴れ’])
weather_b=(weather[‘atk_mod’]-1.0)*base
# コンバート中ペナルティ
convert_penalty=sum(3 for p in lu if p.get(‘convert_weeks’,0)>0)
return base+league_b+morale_b+stamina_b+style_b+derby_b+home_b+fac_b+tac_b+staff_b+brand_b+frm_b+skill_b+cap_b+setpiece_b+state_b+chem_b+weather_b-convert_penalty

# =========================================================

# テキスト実況生成

# =========================================================

def gen_live_events(ta,tb,ga1,gb1,ga2,gb2,cards,weather):
events=[]
t=0
events.append({‘t’:t,‘txt’:f’⚽ キックオフ！ {ta[“name”]} vs {tb[“name”]} | 天候:{weather}’})
# 前半ゴール
for i in range(ga1):
t=random.randint(5,44)
scorer=random.choice(best_lineup(ta))
apos=”’”; events.append({‘t’:t,‘txt’:f’⚽ GOAL! {ta[“name”]} | {scorer[“name”]} ({t}{apos})  {i+1}-{0 if i==0 else i}’})
for i in range(gb1):
t=random.randint(5,44)
scorer=random.choice(best_lineup(tb))
apos=”’”; events.append({‘t’:t,‘txt’:f’⚽ GOAL! {tb[“name”]} | {scorer[“name”]} ({t}{apos})’})
events.append({‘t’:45,‘txt’:f’📯 ハーフタイム | {ta[“name”]} {ga1}-{gb1} {tb[“name”]}’})
# カード
apos=”’”
for col,name in cards[:3]:
t=random.randint(46,89)
events.append({‘t’:t,‘txt’:f’{col} カード: {name} ({t}{apos})’})
# 後半ゴール
for i in range(ga2):
t=random.randint(46,90)
scorer=random.choice(best_lineup(ta))
apos=”’”; events.append({‘t’:t,‘txt’:f’⚽ GOAL! {ta[“name”]} | {scorer[“name”]} ({t}{apos})’})
for i in range(gb2):
t=random.randint(46,90)
scorer=random.choice(best_lineup(tb))
apos=”’”; events.append({‘t’:t,‘txt’:f’⚽ GOAL! {tb[“name”]} | {scorer[“name”]} ({t}{apos})’})
if random.random()<0.12:
t=random.randint(90,93)
events.append({‘t’:t,‘txt’:f’⚡ アディショナルタイム弾！ ({t}+)’})
events.append({‘t’:95,‘txt’:f’🔔 試合終了 | {ta[“name”]} {ga1+ga2}-{gb1+gb2} {tb[“name”]}’})
events.sort(key=lambda e:e[‘t’])
return events

# =========================================================

# 試合シミュレーション（PKシュートアウト対応）

# =========================================================

def simulate_pk_shootout(ta,tb):
“”“PKシューターアウト（カップ戦延長後）”””
pk_a=ta.get(‘pk_taker_id’)
pk_b=tb.get(‘pk_taker_id’)
taker_a=next((p for p in ta[‘players’] if p[‘id’]==pk_a),None) if pk_a else None
taker_b=next((p for p in tb[‘players’] if p[‘id’]==pk_b),None) if pk_b else None
shot_a=taker_a[‘attrs’].get(‘SHT’,60)/100 if taker_a else 0.65
shot_b=taker_b[‘attrs’].get(‘SHT’,60)/100 if taker_b else 0.65
score_a=sum(1 for _ in range(5) if random.random()<shot_a)
score_b=sum(1 for _ in range(5) if random.random()<shot_b)
while score_a==score_b:
score_a+=1 if random.random()<shot_a else 0
score_b+=1 if random.random()<shot_b else 0
winner=ta if score_a>score_b else tb
return winner,score_a,score_b

def simulate_half(ta,tb,tactic_a=None,tactic_b=None,home_team=None):
sa=team_str(ta,tb,tactic_a,is_home=(home_team==ta[‘name’]))
sb=team_str(tb,ta,tactic_b,is_home=(home_team==tb[‘name’]))
ga=min(4,max(0,int(round(random.gauss(sa/48,0.7)))))
gb=min(4,max(0,int(round(random.gauss(sb/48,0.7)))))
return ga,gb

def simulate_match_full(ta,tb,cup=False,ht_tac_a=None,ht_tac_b=None,substitutions_a=None):
derby=tb[‘name’] in ta.get(‘rivals’,[])
weather=get_weather(); wdat=WEATHER.get(weather,WEATHER[‘晴れ’])
ga1,gb1=simulate_half(ta,tb,home_team=ta[‘name’])
# 交代処理（ハーフタイム）
if substitutions_a:
_apply_substitutions(ta,substitutions_a)
ga2,gb2=simulate_half(ta,tb,ht_tac_a,None,home_team=ta[‘name’])
ga=min(8,ga1+ga2); gb=min(8,gb1+gb2)
# カップ戦PKシュートアウト
pk_result=None
if cup and ga==gb:
# 延長戦
gex_a,gex_b=simulate_half(ta,tb,home_team=ta[‘name’])
ga+=gex_a; gb+=gex_b
if ga==gb:
winner,sa_pk,sb_pk=simulate_pk_shootout(ta,tb)
pk_result={‘winner’:winner[‘name’],‘score_a’:sa_pk,‘score_b’:sb_pk}
if winner[‘name’]==ta[‘name’]: ga+=1
else: gb+=1
add_news(f’⚽PKシュートアウト: {ta[“name”]} {sa_pk}-{sb_pk} {tb[“name”]} → {winner[“name”]}が勝利’,‘match’)
if winner[‘name’]==game_state[‘selected_club’]: check_achievement(‘pk_hero’)

```
sa=team_str(ta,tb,is_home=True); sb=team_str(tb,ta)
shots_a=max(3,int(sa/5.5)+random.randint(-2,3)); shots_b=max(3,int(sb/5.5)+random.randint(-2,3))
tot=max(1,sa+sb); pa=clamp(int(sa/tot*100+random.randint(-6,6)),34,66)
stats={'team_a':{'name':ta['name'],'shots':shots_a,'on_target':min(shots_a,max(ga,int(shots_a*random.uniform(0.35,0.55)))),'possession':pa},'team_b':{'name':tb['name'],'shots':shots_b,'on_target':min(shots_b,max(gb,int(shots_b*random.uniform(0.35,0.55)))),'possession':100-pa}}
mom,sclog,cards=_match_stats_full(ta,tb,ga,gb,wdat)
# win_bonus支払い
if ta['name']==game_state['selected_club'] and ga>gb:
    _pay_win_bonus(ta)
elif tb['name']==game_state['selected_club'] and gb>ga:
    _pay_win_bonus(tb)
hl=[]
if weather not in ['晴れ','曇り']: hl.append(f'🌦️{weather}の中での試合')
if derby: hl.append('🔥ダービーマッチ')
if abs(ga-gb)>=3: hl.append('一方的な試合展開')
if random.random()<0.18: hl.append('スーパーセーブ')
if random.random()<0.12: hl.append('ポスト直撃')
if random.random()<0.08: hl.append('⚠️VARチェック発生')
if ga1<gb1 and ga>gb: hl.append('🔄逆転劇！')
if random.random()<0.12: hl.append('⚡ロスタイムの劇的展開')
if pk_result: hl.append(f'🥅PKシュートアウト({pk_result["score_a"]}-{pk_result["score_b"]})')
att=_attendance(ta,tb,derby,wdat); rev=_match_income(ta,att)
res_a='win' if ga>gb else('draw' if ga==gb else 'loss')
res_b='loss' if res_a=='win' else('draw' if res_a=='draw' else 'win')
_update_fanbase(ta,res_a,derby); _update_fanbase(tb,res_b,derby)
_update_table(ta,ga,gb); _update_table(tb,gb,ga)
if derby:
    ra=ta.setdefault('derby_record',{}).setdefault(tb['name'],{'w':0,'d':0,'l':0})
    rb=tb.setdefault('derby_record',{}).setdefault(ta['name'],{'w':0,'d':0,'l':0})
    if ga>gb: ra['w']+=1;rb['l']+=1
    elif ga==gb: ra['d']+=1;rb['d']+=1
    else: ra['l']+=1;rb['w']+=1
_fatigue_weather(ta,wdat); _fatigue_weather(tb,wdat)
# テキスト実況イベント生成
live_evts=gen_live_events(ta,tb,ga1,gb1,ga2,gb2,cards,weather)
game_state['live_commentary']=live_evts
return ga,gb,att,rev,stats,{'mom':mom,'scorers':sclog,'highlights':hl,'derby':derby,'weather':weather,'halfscore':(ga1,gb1,ga2,gb2),'cards':cards}
```

def _pay_win_bonus(team):
sp=team.get(‘sponsor’)
if not sp: return
bonus=sp.get(‘win_bonus’,0)
if bonus>0:
team[‘budget’]+=bonus; add_fin(‘スポンサー勝利ボーナス’,bonus,sp[‘name’]); add_sf(‘sponsor’,bonus)
if team[‘name’]==game_state[‘selected_club’]:
add_news(f’🎉スポンサー勝利ボーナス: {fmt_m(bonus)}’,‘club’)

def _apply_substitutions(team,subs):
“”“ハーフタイム交代: [(out_id, in_id), …]”””
for out_id,in_id in subs[:3]:
out_p=next((p for p in team[‘players’] if p[‘id’]==out_id),None)
in_p=next((p for p in team[‘players’] if p[‘id’]==in_id and p[‘id’] not in team.get(‘starting_xi’,[])),None)
if out_p and in_p and out_id in team.get(‘starting_xi’,[]):
xi=list(team.get(‘starting_xi’,[])); xi.remove(out_id); xi.append(in_id); team[‘starting_xi’]=xi

def _match_stats_full(ta,tb,ga,gb,wdat):
lu_a=best_lineup(ta); lu_b=best_lineup(tb)
for p in lu_a: p[‘stats’][‘apps’]+=1; p[‘stats’][‘shots’]=p[‘stats’].get(‘shots’,0)+random.randint(0,3)
for p in lu_b: p[‘stats’][‘apps’]+=1; p[‘stats’][‘shots’]=p[‘stats’].get(‘shots’,0)+random.randint(0,3)
for p in lu_a:
if p[‘pos’]==‘GK’: p[‘stats’][‘saves’]=p[‘stats’].get(‘saves’,0)+gb
if p[‘pos’]==‘DF’: p[‘stats’][‘tackles’]=p[‘stats’].get(‘tackles’,0)+random.randint(1,4)
for p in lu_b:
if p[‘pos’]==‘GK’: p[‘stats’][‘saves’]=p[‘stats’].get(‘saves’,0)+ga
if p[‘pos’]==‘DF’: p[‘stats’][‘tackles’]=p[‘stats’].get(‘tackles’,0)+random.randint(1,4)
if gb==0:
for p in lu_a:
if p[‘pos’]==‘GK’: p[‘stats’][‘clean_sheets’]=p[‘stats’].get(‘clean_sheets’,0)+1
if ga==0:
for p in lu_b:
if p[‘pos’]==‘GK’: p[‘stats’][‘clean_sheets’]=p[‘stats’].get(‘clean_sheets’,0)+1
contrib={p[‘id’]:0 for p in lu_a+lu_b}; sclog=[]
for _ in range(ga):
weights=[PLAYER_STATES.get(p.get(‘state’,‘normal’),PLAYER_STATES[‘normal’])[‘goal_mult’] for p in lu_a]
sc=random.choices(lu_a,weights=weights,k=1)[0]
sc[‘stats’][‘goals’]+=1; contrib[sc[‘id’]]+=4
if sc.get(‘trait’)==‘勝負師’: contrib[sc[‘id’]]+=1
ast=random.choice(lu_a)
if ast[‘id’]!=sc[‘id’]: ast[‘stats’][‘assists’]+=1; contrib[ast[‘id’]]+=2
sclog.append((ta[‘name’],sc[‘name’]))
for _ in range(gb):
weights=[PLAYER_STATES.get(p.get(‘state’,‘normal’),PLAYER_STATES[‘normal’])[‘goal_mult’] for p in lu_b]
sc=random.choices(lu_b,weights=weights,k=1)[0]
sc[‘stats’][‘goals’]+=1; contrib[sc[‘id’]]+=4
if sc.get(‘trait’)==‘勝負師’: contrib[sc[‘id’]]+=1
ast=random.choice(lu_b)
if ast[‘id’]!=sc[‘id’]: ast[‘stats’][‘assists’]+=1; contrib[ast[‘id’]]+=2
sclog.append((tb[‘name’],sc[‘name’]))
cards=[]
for p in lu_a+lu_b:
if random.random()<0.08*wdat.get(‘injury_mod’,1.0):
p[‘stats’][‘yellow_cards’]=p[‘stats’].get(‘yellow_cards’,0)+1
cards.append((‘🟨’,p[‘name’]))
if p[‘stats’][‘yellow_cards’]%5==0: p[‘injury_weeks’]=max(p[‘injury_weeks’],1)
if random.random()<0.01:
p[‘stats’][‘red_cards’]=p[‘stats’].get(‘red_cards’,0)+1
cards.append((‘🟥’,p[‘name’])); p[‘injury_weeks’]=max(p[‘injury_weeks’],1)
mom=max(lu_a+lu_b,key=lambda p:contrib[p[‘id’]]+p[‘overall’]*0.1+random.uniform(0,1.5))
mom[‘stats’][‘mom’]+=1; return mom,sclog,cards

def _update_table(t,gf,ga):
s=t[‘season_stats’]; s[‘p’]+=1; s[‘gf’]+=gf; s[‘ga’]+=ga; s[‘gd’]=s[‘gf’]-s[‘ga’]
if gf>ga: s[‘w’]+=1;s[‘pts’]+=3
elif gf==ga: s[‘d’]+=1;s[‘pts’]+=1
else: s[‘l’]+=1

def _update_fanbase(t,res,derby=False):
ch={‘win’:random.randint(120,260),‘draw’:random.randint(-30,60),‘loss’:random.randint(-220,-80)}[res]
if derby: ch*=2
t[‘fan_base’]=max(2000,t[‘fan_base’]+ch)

def _attendance(ta,tb,derby=False,wdat=None):
att=int(ta[‘fan_base’]*random.uniform(0.65,1.10))+(ta[‘reputation’]+tb[‘reputation’])//2*120
if derby: att=int(att*1.35)
att=int(att*(1+game_state[‘facilities’][‘stadium’]*0.02+(game_state[‘club_brand’]-50)*0.003))
if wdat: att=int(att*wdat.get(‘att_mod’,1.0))
return min(att,ta[‘stadium_capacity’])

def _match_income(ht,att):
ticket=random.randint(18,28)
vip_bonus=ht.get(‘vip_level’,0)*random.randint(8000,15000)
nr_bonus=50000 if ht.get(‘naming_rights’) else 0
rev=att*ticket+vip_bonus+nr_bonus
ht[‘budget’]+=rev; add_fin(‘観客収入’,rev,‘ホームゲーム’); add_sf(‘matchday’,rev); return rev

def _fatigue_weather(team,wdat):
tr=game_state[‘facilities’][‘training’]
for p in best_lineup(team):
loss=max(3,int(random.randint(6,12)-(tr*0.3))); loss=int(loss*wdat.get(‘injury_mod’,1.0))
p[‘stamina’]=clamp(p[‘stamina’]-loss,20,100)
res=_injure_weather(team,wdat)
if res and team[‘name’]==game_state[‘selected_club’]:
p,sev=res; add_news(f’⚕️{p[“name”]}が{sev}（{p[“injury_weeks”]}週間）’,‘injury’)

def _injure_weather(team,wdat):
med=game_state[‘facilities’][‘medical’]
phys=sum(s[‘skill’]*0.002 for s in game_state[‘staff’] if s[‘type’]==‘フィジオ’)
cands=[p for p in team[‘players’]+team.get(‘loan_in’,[]) if p[‘injury_weeks’]<=0]
if not cands: return None
for p in cands:
risk=0.20 if p.get(‘trait’)==‘スペ体質’ else 0.10
risk*=(1-med*0.05-phys)*wdat.get(‘injury_mod’,1.0); risk=max(0.02,risk)
if random.random()<risk/len(cands):
r=random.random()
if r<0.60: weeks,sev=random.randint(1,2),‘軽傷’
elif r<0.85: weeks,sev=random.randint(3,8),‘中傷’
else: weeks,sev=random.randint(9,20),‘重傷’
if p.get(‘trait’)==‘スペ体質’: weeks=int(weeks*1.5)
p[‘injury_weeks’]=weeks; p[‘injury_severity’]=sev
# 保険支払い
if game_state.get(‘injury_insurance_active’) and sev in [‘中傷’,‘重傷’]:
payout=int(p[‘wage’]*weeks*0.5); get_sel()[‘budget’]+=payout
add_news(f’🏥選手保険支払い: {p[“name”]} {fmt_m(payout)}’,‘club’)
return p,sev
return None

# =========================================================

# 選手状態・ケミストリー

# =========================================================

def update_player_states(team):
for p in team[‘players’]+team.get(‘loan_in’,[]):
if p.get(‘state’,‘normal’)!=‘normal’:
p[‘state_weeks’]=p.get(‘state_weeks’,0)-1
if p[‘state_weeks’]<=0:
p[‘state’]=‘normal’; p[‘state_weeks’]=0
elif random.random()<0.04:
state=random.choice([‘hot’,‘slump’]); dur=random.randint(2,5)
p[‘state’]=state; p[‘state_weeks’]=dur
if team[‘name’]==game_state[‘selected_club’]:
add_news(f’⚡{p[“name”]}が{PLAYER_STATES[state][“label”]}！({dur}週間)’,‘player’)
# 代表帰還ブースト
if p.get(‘intl_boost_pending’) and p.get(‘intl_weeks’,0)<=0:
for k in [‘SHT’,‘TEC’,‘MEN’]: p[‘attrs’][k]=clamp(p[‘attrs’][k]+random.randint(1,2),30,99)
_recompute(p); p[‘intl_boost_pending’]=False
add_news(f’🌍{p[“name”]}が代表経験で成長！’,‘player’)
# コンバート進行
if p.get(‘convert_weeks’,0)>0:
p[‘convert_weeks’]-=1
if p[‘convert_weeks’]==0:
p[‘pos’]=p.get(‘target_pos’,p[‘pos’]); _recompute(p)
add_news(f’{p[“name”]}のコンバート完了 → {p[“pos”]}’,‘player’)

def update_chemistry(team):
pl=team[‘players’]
if not pl: return
nat_counts={}
for p in pl: nat_counts[p[‘nationality’]]=nat_counts.get(p[‘nationality’],0)+1
dom_ratio=max(nat_counts.values())/len(pl)
young=sum(1 for p in pl if p[‘age’]<=24); old=sum(1 for p in pl if p[‘age’]>=32)
age_balance=1.0-(abs(young-old)/max(1,len(pl)))*0.5
cap_bonus=5 if team.get(‘captain_id’) else 0
mood_bonus=sum(3 for p in pl if p.get(‘trait’)==‘ムードメーカー’)
local_bonus=sum(2 for p in pl if p.get(‘is_local’))
team[‘chemistry’]=clamp(int(50+dom_ratio*20+age_balance*10+cap_bonus+mood_bonus+local_bonus-old*2),0,100)

def update_player_feelings(team,won=False,drew=False,lost=False):
mood_d=0
for p in team[‘players’]+team.get(‘loan_in’,[]):
d=2 if lost else(-1 if won else 0)
pers=p.get(‘personality’,’’)
if pers==‘野心家’ and div_of(team[‘name’]) in [‘D2’,‘D3’] and team[‘reputation’]<68: d+=1
if pers==‘気分屋’: d+=random.choice([-1,0,1,2])
if pers==‘忠誠心高い’: d-=1
if pers==‘ムードメーカー’: mood_d+=1
if pers==‘短気’ and lost: d+=2
# 役割不満（主力のみ希望なのにスタメン外）
xi_set=set(team.get(‘starting_xi’,[]))
if p.get(‘role_wish’)==‘主力のみ’ and xi_set and p[‘id’] not in xi_set: d+=2
p[‘unhappiness’]=clamp(p.get(‘unhappiness’,0)+d,0,100)
p[‘morale’]=clamp(p[‘morale’]+(clamp(100-p[‘unhappiness’],0,100)-p[‘morale’])*0.15,0,100)
if p[‘unhappiness’]>=80 and not p.get(‘transfer_request’):
p[‘transfer_request’]=True
if team[‘name’]==game_state[‘selected_club’]:
add_news(f’⚠️{p[“name”]}が移籍要求（不満{p[“unhappiness”]}）’,‘transfer’)
cap_id=team.get(‘captain_id’)
if cap_id:
cap=next((p for p in team[‘players’] if p[‘id’]==cap_id),None)
if cap: mood_d+=CAPTAIN_EFFECTS.get(cap[‘personality’],{}).get(‘locker_room’,0)
base_mood=100-avg([p[‘unhappiness’] for p in team[‘players’]])+mood_d
if won: base_mood+=4
elif lost: base_mood-=4
game_state[‘locker_room_mood’]=clamp(int(base_mood),0,100)

def update_fan_happiness(team,won=False,drew=False,lost=False):
d=4 if won else(1 if drew else -4)
obj=team.get(‘board_expectation’,’’)
tbl=sorted_table(div_of(team[‘name’]))
rank=next((i+1 for i,t in enumerate(tbl) if t[‘name’]==team[‘name’]),10)
if obj==‘優勝争い’: d+=2 if rank<=3 else(-2 if rank>=7 else 0)
elif obj==‘上位進出’: d+=2 if rank<=5 else(-2 if rank>=8 else 0)
elif obj in [‘昇格争い’,‘昇格’]: d+=2 if rank<=3 else(-2 if rank>=7 else 0)
elif obj==‘残留’: d+=1 if rank<=7 else -2
elif obj==‘中位確保’: d+=1 if 4<=rank<=7 else(-2 if rank>=9 else 0)
if game_state[‘club_brand’]>=70: d+=1
elif game_state[‘club_brand’]<=30: d-=1
game_state[‘fan_happiness’]=clamp(game_state[‘fan_happiness’]+d,0,100)

def update_manager_rating(team,won=False,drew=False,lost=False):
d=3 if won else(1 if drew else -3)
if has_skill(‘鉄のメンタル’) and lost: d=int(d*0.5)
tbl=sorted_table(div_of(team[‘name’]))
rank=next((i+1 for i,t in enumerate(tbl) if t[‘name’]==team[‘name’]),10)
obj=team.get(‘board_expectation’,’’)
if obj==‘優勝争い’ and rank<=3: d+=2
elif obj==‘上位進出’ and rank<=5: d+=2
elif obj in [‘昇格争い’,‘昇格’] and rank<=2: d+=3
elif obj==‘残留’ and rank>=9: d-=3
elif obj==‘中位確保’ and rank>=9: d-=2
if game_state[‘locker_room_mood’]>=70: d+=1
elif game_state[‘locker_room_mood’]<=30: d-=2
game_state[‘manager_rating’]=clamp(game_state[‘manager_rating’]+d,0,100)
gain_exp(2 if won else(1 if drew else 0))
if game_state[‘manager_rating’]<=25 and game_state[‘board_rating’]<=30 and not game_state[‘manager_fired’]:
game_state[‘manager_fired’]=True; add_news(‘🚨監督解任危機！’,‘club’)

def update_board_rating(team):
tbl=sorted_table(div_of(team[‘name’]))
rank=next((i+1 for i,t in enumerate(tbl) if t[‘name’]==team[‘name’]),10)
d=4 if rank<=3 else(1 if rank<=6 else(-4 if rank>=9 else 0))
if team[‘budget’]>800000: d+=1
elif team[‘budget’]<100000: d-=2
game_state[‘board_rating’]=clamp(game_state[‘board_rating’]+d,0,100)
team[‘reputation’]=clamp(team.get(‘reputation’,60)+(3 if rank<=2 else(1 if rank<=4 else(-1 if rank>=8 else 0))),30,99)
bd=2 if rank<=3 else(-1 if rank>=8 else 0)
if team[‘budget’]>1000000: bd+=1
game_state[‘club_brand’]=clamp(game_state[‘club_brand’]+bd,0,100)
if team[‘budget’]<-200000 and not game_state[‘financial_crisis’]:
game_state[‘financial_crisis’]=True; add_news(‘💸財政危機！’,‘club’)
elif team[‘budget’]>0 and game_state[‘financial_crisis’]:
game_state[‘financial_crisis’]=False; add_news(‘財政が回復しました’,‘club’)
_check_buyout(team)
# 肖像権収入更新
stars=sum(1 for p in team[‘players’] if p[‘overall’]>=80)
game_state[‘portrait_income_weekly’]=stars*random.randint(5000,12000)

# =========================================================

# 収入・支出

# =========================================================

def weekly_expenses(team):
fac=sum(game_state[‘facilities’].values())*5000
wage=sum(p[‘wage’] for p in team[‘players’])
loan_w=sum(p[‘wage’]//2 for p in team.get(‘loan_in’,[]))
staff=sum(s[‘salary’] for s in game_state[‘staff’])
# 銀行ローン返済
loan_payment=0
for loan in game_state[‘bank_loans’]:
loan[‘remaining_weeks’]=loan.get(‘remaining_weeks’,1)-1
weekly=int(int(loan[‘amount’]/loan[‘weeks’])*(1+loan[‘interest_rate’]))
loan_payment+=weekly; team[‘budget’]-=weekly; add_sf(‘loan_interest’,int(weekly))
total=fac+wage+loan_w+staff
team[‘budget’]-=total
add_fin(‘クラブ運営費’,-total,‘週次支出’); add_sf(‘wages’,wage+loan_w); add_sf(‘facility’,fac); add_sf(‘staff’,staff)
game_state[‘bank_loans’]=[l for l in game_state[‘bank_loans’] if l.get(‘remaining_weeks’,1)>0]
dn=div_of(team[‘name’]); cap=SALARY_CAP.get(dn,999999)
if wage>cap:
penalty=int((wage-cap)*0.1); team[‘budget’]-=penalty
add_news(f’⚠️給与上限超過ペナルティ: {fmt_m(penalty)}’,‘club’)

def weekly_sponsor(team):
if not team.get(‘sponsor’): team[‘sponsor’]=_gen_sponsor(team[‘country’],div_of(team[‘name’]))
sp=team[‘sponsor’]; inc=sp[‘weekly_income’]
if has_skill(‘財務手腕’): inc=int(inc*1.10)
team[‘budget’]+=inc; add_fin(‘スポンサー収入’,inc,sp[‘name’]); add_sf(‘sponsor’,inc)

def weekly_broadcast(team):
d=div_of(team[‘name’]); base={‘D1’:30000,‘D2’:15000,‘D3’:5000}.get(d,0)
rev=int(base*(1+(team[‘reputation’]-60)*0.01)); team[‘budget’]+=rev; add_sf(‘broadcast’,rev)

def weekly_merch(team):
# グッズ収入修正（係数を0.02に）
rev=int(team[‘fan_base’]*game_state[‘club_brand’]*0.02)
team[‘budget’]+=rev; add_sf(‘merch’,rev)

def weekly_naming_rights(team):
nr=team.get(‘naming_rights’)
if nr: team[‘budget’]+=nr[‘weekly’]; add_sf(‘naming_rights’,nr[‘weekly’])

def weekly_portrait_income(team):
inc=game_state.get(‘portrait_income_weekly’,0)
if inc>0: team[‘budget’]+=inc; add_sf(‘merch’,inc)

def weekly_overseas_scout(team):
os_data=game_state.get(‘overseas_scout’)
if not os_data: return
os_data[‘weeks_left’]=os_data.get(‘weeks_left’,4)-1
if os_data[‘weeks_left’]<=0:
# 海外スカウトの結果
country=os_data[‘country’]
ps=[gen_player(country,‘OverseasPool’,random.randint(500000,599999)) for _ in range(5)]
for p in ps:
sb=game_state[‘facilities’][‘scouting’]*3+(3 if has_skill(‘スカウト眼’) else 0)
for k in p[‘attrs’]: p[‘attrs’][k]=clamp(p[‘attrs’][k]+random.randint(0,sb),30,99)
_recompute(p)
# スカウト不確実性
p[‘scout_ovr_min’]=max(35,p[‘overall’]-10)
p[‘scout_ovr_max’]=min(99,p[‘overall’]+10)
game_state[‘overseas_pool’]=ps
game_state[‘overseas_scout’]=None
add_news(f’🌍海外スカウト({country})帰還！{len(ps)}名の候補を発見’,‘player’)
refresh_ui()

def recover_players():
for p in all_players(True):
if p[‘injury_weeks’]>0:
p[‘injury_weeks’]-=1
if p[‘injury_weeks’]==0: p[‘injury_severity’]=‘なし’
if p.get(‘intl_weeks’,0)>0: p[‘intl_weeks’]-=1
p[‘stamina’]=clamp(p[‘stamina’]+random.randint(5,12),40,100)

def apply_individual_training(team):
tr_lv=game_state[‘facilities’][‘training’]; results=[]
for p in team[‘players’]:
focus=p.get(‘training_focus’)
if not focus or focus not in p[‘attrs’]: continue
if random.random()<(0.3+tr_lv*0.1):
p[‘attrs’][focus]=clamp(p[‘attrs’][focus]+1,30,99); _recompute(p)
results.append(f’{p[“name”]}の{ATTR_ICONS.get(focus,focus)}{focus}が+1向上’)
if results: game_state[‘training_results’]=results[-5:]

def check_retirements(team):
for p in list(team[‘players’]):
if p[‘age’]>=35 and not p.get(‘retiring’) and random.random()<(p[‘age’]-34)*0.12:
p[‘retiring’]=True; add_news(f’💐{p[“name”]}が今季引退を発表（{p[“age”]}歳）’,‘player’)
if p.get(‘retiring’) and p[‘age’]>=36 and random.random()<0.6:
team[‘players’].remove(p)
score=p[‘stats’][‘goals’]*3+p[‘stats’][‘assists’]*2+p[‘stats’][‘mom’]*4
game_state[‘club_hall_of_fame’].append({‘name’:p[‘name’],‘score’:score,‘reason’:‘引退’})
add_news(f’🎖️{p[“name”]}が現役引退’,‘player’)

# =========================================================

# ランダムイベント

# =========================================================

def gen_random_event():
sel=get_sel()
if not sel or random.random()>0.20: return
if game_state.get(‘pending_event’): return
evt_template=random.choice(RANDOM_EVENTS)
# プレースホルダー埋め
player=random.choice(sel[‘players’]) if sel[‘players’] else None
rival=sel[‘rivals’][0] if sel.get(‘rivals’) else ‘ライバル’
text=evt_template[‘text’].replace(’{name}’,player[‘name’] if player else ‘選手’).replace(’{rival}’,rival)
event={‘id’:evt_template[‘id’],‘text’:text,‘choices’:evt_template[‘choices’],‘effects’:evt_template[‘effects’],‘player_id’:player[‘id’] if player else None}
game_state[‘pending_event’]=event
add_news(f’📌イベント発生: {text}’,‘club’)

def resolve_event(choice):
evt=game_state.get(‘pending_event’)
if not evt: return
effs=evt[‘effects’].get(choice,{})
sel=get_sel()
if not sel: return
pid=evt.get(‘player_id’)
p=player_by_id(pid) if pid else None
for k,v in effs.items():
if k==‘fan_happiness’: game_state[‘fan_happiness’]=clamp(game_state[‘fan_happiness’]+v,0,100)
elif k==‘locker_room_mood’: game_state[‘locker_room_mood’]=clamp(game_state[‘locker_room_mood’]+v,0,100)
elif k==‘manager_rating’: game_state[‘manager_rating’]=clamp(game_state[‘manager_rating’]+v,0,100)
elif k==‘board_rating’: game_state[‘board_rating’]=clamp(game_state[‘board_rating’]+v,0,100)
elif k==‘club_brand’: game_state[‘club_brand’]=clamp(game_state[‘club_brand’]+v,0,100)
elif k==‘fan_base’ and sel: sel[‘fan_base’]+=v
elif k==‘budget’ and sel: sel[‘budget’]+=v; add_fin(‘イベント支出’,v,evt[‘text’])
elif k==‘morale_player’ and p: p[‘morale’]=clamp(p.get(‘morale’,50)+v,0,100)
elif k==‘unhappiness_player’ and p: p[‘unhappiness’]=clamp(p.get(‘unhappiness’,0)+v,0,100)
elif k==‘attr_boost’ and p:
attr=random.choice(list(p[‘attrs’].keys())); p[‘attrs’][attr]=clamp(p[‘attrs’][attr]+random.randint(1,3),30,99); _recompute(p)
elif k==‘injury_minor’ and p: p[‘injury_weeks’]=max(p[‘injury_weeks’],random.randint(1,2)); p[‘injury_severity’]=‘軽傷’
elif k==‘new_staff’:
game_state[‘staff’].append({‘type’:‘ヘッドコーチ’,‘skill’:random.randint(60,80),‘salary’:0}); add_news(‘OBコーチが無償で就任’,‘club’)
elif k==‘transfer_youth’ and p:
if sel and p in sel[‘youth’]: sel[‘youth’].remove(p); sel[‘budget’]+=int(p[‘value’]*0.5); add_news(f’{p[“name”]}をビッグクラブに売却’,‘transfer’)
game_state[‘event_history’].append({‘text’:evt[‘text’],‘choice’:choice,‘season’:game_state[‘season’],‘week’:game_state[‘week’]})
game_state[‘pending_event’]=None
add_news(f’イベント対応:「{choice}」’,‘club’); refresh_ui()

# =========================================================

# 銀行ローン・保険

# =========================================================

def take_bank_loan(amount):
sel=get_sel()
if not sel: return
weeks=random.choice([12,18,24]); rate=random.choice([0.03,0.05,0.08])
loan={‘amount’:amount,‘weeks’:weeks,‘interest_rate’:rate,‘remaining_weeks’:weeks}
game_state[‘bank_loans’].append(loan); sel[‘budget’]+=amount
add_fin(‘銀行ローン’,amount,f’返済{weeks}週 金利{int(rate*100)}%’); add_news(f’銀行ローン: {fmt_m(amount)}（{weeks}週返済 金利{int(rate*100)}%）’,‘club’); refresh_ui()

def activate_insurance():
sel=get_sel()
if not sel: return
cost=8000
if sel[‘budget’]<cost: ui.notify(‘予算不足’); return
sel[‘budget’]-=cost; game_state[‘injury_insurance_active’]=True
add_fin(‘選手保険料’,-cost,‘週次’); add_news(‘🏥選手保険を契約（重傷時に給与補償）’,‘club’); refresh_ui()

# =========================================================

# 監督キャリア

# =========================================================

def gen_manager_offers():
“”“高評価時に他クラブからオファー”””
if game_state[‘manager_rating’]<70: return
if game_state.get(‘manager_career_offers’): return
candidates=[]
for d in game_state[‘divisions’]:
for t in game_state[‘divisions’][d]:
if t[‘name’]==game_state[‘selected_club’]: continue
if t[‘reputation’]>get_sel().get(‘reputation’,50) and random.random()<0.05:
candidates.append(t[‘name’])
if candidates:
game_state[‘manager_career_offers’]=candidates[:2]
add_news(f’📨監督オファー: {”, “.join(candidates[:2])}’,‘club’)

def accept_manager_offer(new_club_name):
sel=get_sel()
if not sel: return
dn=div_of(sel[‘name’]); tbl=sorted_table(dn)
rank=next((i+1 for i,t in enumerate(tbl) if t[‘name’]==sel[‘name’]),10)
# キャリア記録
game_state[‘manager_career’].append({‘club’:sel[‘name’],‘season’:game_state[‘season’],‘div’:dn,‘rank’:rank})
game_state[‘selected_club’]=new_club_name
game_state[‘manager_career_offers’]=[]
# 評価リセット（新クラブで再スタート）
game_state[‘manager_rating’]=50; game_state[‘board_rating’]=50
new_t=find_team(new_club_name)
if new_t and not new_t.get(‘sponsor’):
new_t[‘sponsor’]=_gen_sponsor(new_t[‘country’],div_of(new_club_name))
check_achievement(‘career_move’)
add_news(f’✈️{new_club_name}に転身！’,‘club’); refresh_ui()

# =========================================================

# プレシーズン

# =========================================================

def run_preseason():
sel=get_sel()
if not sel: return
results=[]
for _ in range(3):
opp=random.choice([t for d in game_state[‘divisions’] for t in game_state[‘divisions’][d] if t[‘name’]!=sel[‘name’]])
ga,gb,*_=simulate_match_full(sel,opp)
results.append(f’{sel[“name”]} {ga}-{gb} {opp[“name”]}’)
for p in sel[‘players’]: p[‘stamina’]=clamp(p[‘stamina’]+random.randint(5,15),60,100); p[‘morale’]=clamp(p[‘morale’]+random.randint(0,8),0,100)
income=random.randint(50000,150000); sel[‘budget’]+=income; add_sf(‘preseason’,income)
game_state[‘preseason_phase’]=False; sel[‘preseason_done’]=True
add_news(f’プレシーズン完了！収入: {fmt_m(income)}’,‘club’)
for r in results: add_news(f’親善試合: {r}’,‘match’)
refresh_ui()

# =========================================================

# スポンサー

# =========================================================

def _gen_sponsor(country,div):
bw={‘D1’:65000,‘D2’:42000,‘D3’:26000}[div]; bb={‘D1’:220000,‘D2’:150000,‘D3’:90000}[div]
pool={‘England’:[‘NorthSea Media’,‘Union Logistics’,‘Royal Finance’,‘Harbor Tech’],‘Spain’:[‘Costa Vision’,‘Iberia Foods’,‘Roja Energy’,‘Valle Systems’],‘Germany’:[‘Rhein Motors’,‘Nord Stahl’,‘Union Technik’,‘Berg Trade’],‘Italy’:[‘Milano Foods’,‘Roma Capital’,‘Verona Tech’,‘Lazio Holdings’],‘France’:[‘Paris Media’,‘Bleu Telecom’,‘Avenir Groupe’,‘Marseille Foods’],‘Brazil’:[‘Rio Energy’,‘Sol Telecom’,‘Verde Bank’,‘Nova Foods’],‘Japan’:[‘Aozora Holdings’,‘Hikari Systems’,‘Shinsei Tech’,‘Kouyou Foods’]}
bm=1.0+(game_state.get(‘club_brand’,50)-50)*0.005
return {‘name’:random.choice(pool[country]),‘weekly_income’:int(bw*random.uniform(0.9,1.2)*bm),‘win_bonus’:random.randint(5000,15000),‘season_bonus’:int(bb*random.uniform(0.9,1.25)*bm),‘target_rank’:{‘D1’:5,‘D2’:4,‘D3’:3}[div]}

def gen_sponsor_nego():
sel=get_sel()
if not sel: return
offer=_gen_sponsor(sel[‘country’],div_of(sel[‘name’])); demand=random.choice([‘若手起用’,‘上位進出’,‘堅実経営’,‘観客動員増’])
game_state[‘pending_sponsor_negotiation’]={‘offer’:offer,‘demand’:demand}
add_news(f’スポンサー交渉: {offer[“name”]}が「{demand}」を要求’,‘club’)

def accept_sponsor():
sel=get_sel(); data=game_state.get(‘pending_sponsor_negotiation’)
if not sel or not data: return
o,dem=data[‘offer’],data[‘demand’]
if dem==‘若手起用’: o[‘weekly_income’]=int(o[‘weekly_income’]*0.95); o[‘season_bonus’]=int(o[‘season_bonus’]*1.05)
elif dem==‘上位進出’: o[‘target_rank’]=max(1,o[‘target_rank’]-1); o[‘season_bonus’]=int(o[‘season_bonus’]*1.15)
elif dem==‘堅実経営’: o[‘weekly_income’]=int(o[‘weekly_income’]*1.05)
elif dem==‘観客動員増’: o[‘win_bonus’]=int(o[‘win_bonus’]*1.15)
sel[‘sponsor’]=o; game_state[‘pending_sponsor_negotiation’]=None
add_news(f’スポンサー契約成立: {o[“name”]}’,‘club’); refresh_ui()

def reject_sponsor():
data=game_state.get(‘pending_sponsor_negotiation’)
if data: game_state[‘pending_sponsor_negotiation’]=None; add_news(f’スポンサー交渉決裂: {data[“offer”][“name”]}’,‘club’); refresh_ui()

# =========================================================

# プレス・代表召集・エージェント

# =========================================================

def do_press(choice):
effs={‘強気発言’:{‘fan_happiness’:3,‘locker_room_mood’:4,‘manager_rating_risk’:-3},‘慎重姿勢’:{‘fan_happiness’:-1,‘locker_room_mood’:2},‘選手を称える’:{‘locker_room_mood’:6,‘morale_all’:4,‘fan_happiness’:2},‘批判を受け入れる’:{‘board_rating’:3,‘fan_happiness’:1,‘locker_room_mood’:-2}}
eff=effs.get(choice,{})
game_state[‘fan_happiness’]=clamp(game_state[‘fan_happiness’]+eff.get(‘fan_happiness’,0),0,100)
game_state[‘locker_room_mood’]=clamp(game_state[‘locker_room_mood’]+eff.get(‘locker_room_mood’,0),0,100)
game_state[‘board_rating’]=clamp(game_state[‘board_rating’]+eff.get(‘board_rating’,0),0,100)
sel=get_sel()
if sel and eff.get(‘morale_all’):
for p in sel[‘players’]: p[‘morale’]=clamp(p[‘morale’]+eff[‘morale_all’],0,100)
if eff.get(‘manager_rating_risk’) and random.random()<0.3:
game_state[‘manager_rating’]=clamp(game_state[‘manager_rating’]+eff[‘manager_rating_risk’],0,100)
game_state[‘pending_press’]=False; add_news(f’📰プレス発言:「{choice}」’,‘club’); refresh_ui()

def process_intl_calls(team):
if random.random()>0.15: return
cands=[p for p in team[‘players’] if p[‘overall’]>=68 and p.get(‘intl_weeks’,0)<=0]
if not cands: return
p=random.choice(cands); weeks=random.randint(2,4); p[‘intl_weeks’]=weeks
p[‘intl_boost_pending’]=True  # 帰還後に成長ブースト
add_news(f’🌍{p[“name”]}が代表召集（{weeks}週間）’,‘player’)

def agent_intervention(team):
if random.random()>0.12: return
agents=[p for p in team[‘players’] if p.get(‘has_agent’) and not p.get(‘transfer_request’) and p[‘unhappiness’]>30]
if not agents: return
p=random.choice(agents)
add_news(f’🤝{p[“name”]}のエージェントが介入。移籍金+{p[“agent_fee_pct”]}%要求’,‘transfer’)

# =========================================================

# 理事会・ネーミングライツ・買収

# =========================================================

def trigger_board_meeting():
sel=get_sel()
if not sel: return
dn=div_of(sel[‘name’]); tbl=sorted_table(dn)
rank=next((i+1 for i,t in enumerate(tbl) if t[‘name’]==sel[‘name’]),10)
mood=‘満足’ if rank<=4 else(‘不満’ if rank>=8 else ‘普通’)
add_news(f’📋理事会ミーティング（現状:{mood} {rank}位）’,‘club’)
events=[(‘追加補強資金’,lambda: sel.update({‘budget’:sel[‘budget’]+200000}) or add_news(‘理事会から追加資金$200,000’,‘club’)),(‘節約要求’,lambda: add_news(‘理事会が予算削減を要求’,‘club’)),(‘スタジアム拡張支援’,lambda: sel.update({‘budget’:sel[‘budget’]+300000}) or add_news(‘スタジアム支援金$300,000’,‘club’)),(‘新スポンサー紹介’,lambda: gen_sponsor_nego())]
evt=random.choice(events); add_news(f’理事会決定: {evt[0]}’,‘club’); evt[1]()
# 次回理事会は中盤頃（年2回）
sel[‘board_meeting_week’]=game_state[‘week’]+18 if game_state[‘week’]<18 else game_state[‘week’]+18
game_state[‘pending_board_meeting’]=False

def offer_naming_rights():
sel=get_sel()
if not sel or sel.get(‘naming_rights’): return
companies=[‘TechCorp Arena’,‘MegaBank Stadium’,‘AutoGroup Park’,‘AirlineOne Field’,‘DigitalBiz Ground’]
upfront=random.randint(500000,1500000); weekly=random.randint(15000,40000)
game_state[‘naming_rights_offer’]={‘company’:random.choice(companies),‘upfront’:upfront,‘weekly’:weekly}
add_news(f’💼ネーミングライツ打診 一時金{fmt_m(upfront)}/週{fmt_m(weekly)}’,‘club’)

def accept_naming_rights():
sel=get_sel(); offer=game_state.get(‘naming_rights_offer’)
if not sel or not offer: return
sel[‘budget’]+=offer[‘upfront’]; sel[‘naming_rights’]={‘company’:offer[‘company’],‘weekly’:offer[‘weekly’]}
add_fin(‘ネーミングライツ’,offer[‘upfront’],offer[‘company’]); add_sf(‘naming_rights’,offer[‘upfront’])
game_state[‘fan_happiness’]=clamp(game_state[‘fan_happiness’]-3,0,100)
game_state[‘club_brand’]=clamp(game_state[‘club_brand’]+4,0,100)
game_state[‘naming_rights_offer’]=None; add_news(f’ネーミングライツ契約成立’,‘club’); refresh_ui()

def reject_naming_rights():
game_state[‘naming_rights_offer’]=None; refresh_ui()

def _check_buyout(team):
if game_state.get(‘buyout_offer’): return
if team[‘name’]!=game_state[‘selected_club’]: return
if (game_state[‘club_brand’]>=80 or game_state[‘financial_crisis’]) and random.random()<0.03:
offer_type=‘富豪’ if game_state[‘club_brand’]>=80 else ‘再建型’
boost=random.randint(2000000,5000000) if offer_type==‘富豪’ else random.randint(500000,1200000)
game_state[‘buyout_offer’]={‘type’:offer_type,‘budget_boost’:boost,‘board_control_loss’:offer_type==‘富豪’}
add_news(f’💰オーナー{offer_type}買収オファー！補強資金+{fmt_m(boost)}’,‘club’)

def accept_buyout():
offer=game_state.get(‘buyout_offer’); sel=get_sel()
if not offer or not sel: return
sel[‘budget’]+=offer[‘budget_boost’]; add_fin(‘買収資金’,offer[‘budget_boost’],‘オーナー変更’)
if offer.get(‘board_control_loss’): game_state[‘board_rating’]=clamp(game_state[‘board_rating’]-15,0,100)
game_state[‘club_brand’]=clamp(game_state[‘club_brand’]+8,0,100)
game_state[‘buyout_offer’]=None; add_news(f’オーナー{offer[“type”]}買収受諾！’,‘club’); refresh_ui()

def reject_buyout():
game_state[‘buyout_offer’]=None; refresh_ui()

def set_budget_allocation(tp,fp,sp):
sel=get_sel()
if not sel: return
total=sel[‘budget’]
sel[‘budget_transfer’]=int(total*tp/100); sel[‘budget_facility’]=int(total*fp/100); sel[‘budget_staff’]=int(total*sp/100)
add_news(f’予算配分: 移籍{tp}%/施設{fp}%/スタッフ{sp}%’,‘club’); refresh_ui()

# =========================================================

# 移籍・レンタル・スカウト

# =========================================================

def renew_contract(pid):
sel=get_sel()
if not sel: return
p=next((x for x in sel[‘players’] if x[‘id’]==pid),None)
if not p: ui.notify(‘選手なし’); return
nw=int(p[‘wage’]*random.uniform(1.10,1.25)); cost=nw*8
if sel[‘budget’]<cost: ui.notify(‘予算不足’); return
sel[‘budget’]-=cost; add_fin(‘契約更改’,-cost,p[‘name’]); add_sf(‘transfers_in’,cost)
p[‘wage’]=nw; p[‘contract_years’]=random.randint(2,5)
p[‘unhappiness’]=max(0,p[‘unhappiness’]-20); p[‘transfer_request’]=False
add_news(f’{p[“name”]}と契約延長 年俸{fmt_m(nw)}/{p[“contract_years”]}年’,‘club’); refresh_ui()

def process_expiry():
sel=get_sel()
if not sel: return
stay=[]; go=[]
for p in sel[‘players’]:
p[‘contract_years’]-=1
if p[‘contract_years’]<=0: go.append(p[‘name’])
else: stay.append(p)
if len(stay)>=11:
sel[‘players’]=stay
for n in go: add_news(f’{n}が契約満了退団’,‘transfer’)
else:
for p in sel[‘players’]:
if p[‘contract_years’]<=0: p[‘contract_years’]=1
add_news(‘契約満了選手を人数不足のため暫定残留’,‘club’)

def gen_domestic_offers():
sel=get_sel()
if not sel: return
offers=[]
for p in sel[‘players’]:
if random.random()<0.12 and p[‘overall’]>=60:
buyer=random.choice([t for d in game_state[‘divisions’] for t in game_state[‘divisions’][d] if t[‘name’]!=sel[‘name’]])
offers.append({‘player_id’:p[‘id’],‘player_name’:p[‘name’],‘buyer’:buyer[‘name’],‘fee’:int(p[‘value’]*random.uniform(0.9,1.3)),‘counter_fee’:None})
game_state[‘transfer_offers’]=offers

def accept_transfer(pid,buyback=False):
if not in_transfer_window(): ui.notify(‘移籍ウィンドウ外’); return
sel=get_sel()
if not sel: return
o=next((x for x in game_state[‘transfer_offers’] if x[‘player_id’]==pid),None)
if not o: return
if len(sel[‘players’])<=11: ui.notify(‘最低11人必要’); return
p=next((x for x in sel[‘players’] if x[‘id’]==pid),None)
if not p: return
fee=o.get(‘counter_fee’) or o[‘fee’]
if p.get(‘has_agent’): agent_cut=int(fee*p[‘agent_fee_pct’]/100); fee-=agent_cut; add_news(f’エージェント手数料: {fmt_m(agent_cut)}’,‘transfer’)
sel[‘players’]=[x for x in sel[‘players’] if x[‘id’]!=pid]
sel[‘budget’]+=fee; add_fin(‘移籍売却’,fee,p[‘name’]); add_sf(‘transfers_out’,fee)
if buyback: p[‘buyback_fee’]=int(fee*1.5); p[‘buyback_club’]=sel[‘name’]
game_state[‘transfer_offers’]=[x for x in game_state[‘transfer_offers’] if x[‘player_id’]!=pid]
add_news(f’{p[“name”]}を{o[“buyer”]}に{fmt_m(fee)}で売却’,‘transfer’); refresh_ui()

def counter_offer(pid):
o=next((x for x in game_state[‘transfer_offers’] if x[‘player_id’]==pid),None)
if not o: return
o[‘counter_fee’]=int(o[‘fee’]*1.3)
if random.random()<0.6: add_news(f’カウンター成立: {fmt_m(o[“counter_fee”])}’,‘transfer’)
else: game_state[‘transfer_offers’]=[x for x in game_state[‘transfer_offers’] if x[‘player_id’]!=pid]; add_news(‘カウンター拒否’,‘transfer’)
refresh_ui()

def reject_transfer(pid):
game_state[‘transfer_offers’]=[x for x in game_state[‘transfer_offers’] if x[‘player_id’]!=pid]; refresh_ui()

def gen_foreign_offer():
sel=get_sel()
if not sel or not sel[‘players’] or random.random()>0.25: return
p=random.choice(sel[‘players’])
if p[‘overall’]<65: return
game_state[‘foreign_offers’].append({‘player_id’:p[‘id’],‘club’:random.choice([‘Madrid FC’,‘London United’,‘Milano AC’,‘Munich Blau’,‘Paris Royale’]),‘fee’:int(p[‘value’]*random.uniform(1.2,2.0))})
add_news(f’海外クラブが{p[“name”]}にオファー’,‘transfer’)

def accept_foreign(pid):
if not in_transfer_window(): ui.notify(‘移籍ウィンドウ外’); return
sel=get_sel()
if not sel: return
o=next((x for x in game_state[‘foreign_offers’] if x[‘player_id’]==pid),None)
if not o: return
if len(sel[‘players’])<=11: ui.notify(‘最低11人必要’); return
p=next((x for x in sel[‘players’] if x[‘id’]==pid),None)
if not p: return
sel[‘players’]=[x for x in sel[‘players’] if x[‘id’]!=pid]
sel[‘budget’]+=o[‘fee’]; add_fin(‘海外移籍売却’,o[‘fee’],p[‘name’]); add_sf(‘transfers_out’,o[‘fee’])
game_state[‘foreign_offers’]=[x for x in game_state[‘foreign_offers’] if x[‘player_id’]!=pid]
game_state[‘club_brand’]=clamp(game_state[‘club_brand’]+3,0,100)
add_news(f’{p[“name”]}を海外{o[“club”]}に{fmt_m(o[“fee”])}で売却’,‘transfer’); refresh_ui()

def reject_foreign(pid):
game_state[‘foreign_offers’]=[x for x in game_state[‘foreign_offers’] if x[‘player_id’]!=pid]; refresh_ui()

def gen_loan_offers():
sel=get_sel()
if not sel: return
offers=[]
for d in game_state[‘divisions’]:
for t in game_state[‘divisions’][d]:
if t[‘name’]==sel[‘name’]: continue
for p in t[‘players’]:
if p.get(‘loan_club’) or random.random()>0.04 or p[‘overall’]<58: continue
offers.append({‘player_id’:p[‘id’],‘player_name’:p[‘name’],‘player_pos’:p[‘pos’],‘player_ovr’:p[‘overall’],‘scout_grade’:p.get(‘scout_grade’,‘C’),‘from_club’:t[‘name’],‘loan_fee’:int(p[‘wage’]*random.uniform(4,8)),‘weeks’:random.choice([4,8,12,18])})
random.shuffle(offers); game_state[‘loan_offers’]=offers[:3]

def accept_loan_in(pid):
sel=get_sel()
if not sel: return
o=next((x for x in game_state[‘loan_offers’] if x[‘player_id’]==pid),None)
if not o: return
if len(sel[‘players’])+len(sel.get(‘loan_in’,[]))>=MAX_SQUAD: ui.notify(‘満員’); return
if sel[‘budget’]<o[‘loan_fee’]: ui.notify(‘予算不足’); return
src=find_team(o[‘from_club’])
if not src: return
p=next((x for x in src[‘players’] if x[‘id’]==pid),None)
if not p: return
sel[‘budget’]-=o[‘loan_fee’]; add_fin(‘レンタル借用料’,-o[‘loan_fee’],p[‘name’])
p[‘loan_club’]=sel[‘name’]; p[‘loan_origin’]=src[‘name’]; p[‘loan_weeks’]=o[‘weeks’]
src[‘players’]=[x for x in src[‘players’] if x[‘id’]!=pid]; sel.setdefault(‘loan_in’,[]).append(p)
game_state[‘loan_offers’]=[x for x in game_state[‘loan_offers’] if x[‘player_id’]!=pid]
add_news(f’レンタル加入: {p[“name”]}（{o[“from_club”]}から{o[“weeks”]}週間）’,‘transfer’); refresh_ui()

def reject_loan_in(pid):
game_state[‘loan_offers’]=[x for x in game_state[‘loan_offers’] if x[‘player_id’]!=pid]; refresh_ui()

def send_on_loan(pid):
sel=get_sel()
if not sel: return
if len(sel[‘players’])<=11: ui.notify(‘最低11人必要’); return
p=next((x for x in sel[‘players’] if x[‘id’]==pid),None)
if not p: return
dests=[t for d in game_state[‘divisions’] for t in game_state[‘divisions’][d] if t[‘name’]!=sel[‘name’] and len(t[‘players’])<MAX_SQUAD-2]
if not dests: ui.notify(‘受け入れ先なし’); return
dest=random.choice(dests); weeks=random.choice([4,8,12]); inc=int(p[‘wage’]*random.uniform(3,6))
sel[‘players’]=[x for x in sel[‘players’] if x[‘id’]!=pid]; sel[‘budget’]+=inc; add_fin(‘レンタル放出料’,inc,p[‘name’])
p[‘loan_club’]=dest[‘name’]; p[‘loan_origin’]=sel[‘name’]; p[‘loan_weeks’]=weeks
dest.setdefault(‘loan_in’,[]).append(p)
add_news(f’レンタル放出: {p[“name”]}→{dest[“name”]}（{weeks}週間 収入{fmt_m(inc)}）’,‘transfer’); refresh_ui()

def recall_loan(pid):
sel=get_sel()
if not sel: return
for d in game_state[‘divisions’]:
for t in game_state[‘divisions’][d]:
for p in t.get(‘loan_in’,[]):
if p[‘id’]==pid and p.get(‘loan_origin’)==sel[‘name’]:
if len(sel[‘players’])>=MAX_SQUAD: ui.notify(‘満員’); return
t[‘loan_in’]=[x for x in t[‘loan_in’] if x[‘id’]!=pid]
p[‘loan_club’]=None; p[‘loan_origin’]=None; p[‘loan_weeks’]=0
sel[‘players’].append(p); add_news(f’レンタル召還: {p[“name”]}’,‘transfer’); refresh_ui(); return

def process_loan_returns():
for d in game_state[‘divisions’]:
for t in game_state[‘divisions’][d]:
ret=[]; stay=[]
for p in t.get(‘loan_in’,[]):
p[‘loan_weeks’]=max(0,p[‘loan_weeks’]-1)
if p[‘loan_weeks’]<=0: ret.append(p)
else: stay.append(p)
t[‘loan_in’]=stay
for p in ret:
orig=find_team(p.get(‘loan_origin’,’’))
p[‘loan_club’]=None; p[‘loan_origin’]=None
if orig and len(orig[‘players’])<MAX_SQUAD: orig[‘players’].append(p)

def loaned_out():
sel=get_sel()
if not sel: return []
return [(p,t[‘name’]) for d in game_state[‘divisions’] for t in game_state[‘divisions’][d] for p in t.get(‘loan_in’,[]) if p.get(‘loan_origin’)==sel[‘name’]]

def settle_request(pid):
sel=get_sel()
if not sel: return
p=next((x for x in sel[‘players’] if x[‘id’]==pid),None)
if not p: return
cost=int(p[‘wage’]*4)
if sel[‘budget’]<cost: ui.notify(‘予算不足’); return
sel[‘budget’]-=cost; p[‘unhappiness’]=max(0,p[‘unhappiness’]-40)
p[‘transfer_request’]=False; p[‘wage’]=int(p[‘wage’]*1.15)
add_news(f’{p[“name”]}と交渉成立、移籍要求撤回’,‘transfer’); refresh_ui()

def set_captain(pid):
sel=get_sel()
if not sel: return
sel[‘captain_id’]=pid
p=next((x for x in sel[‘players’] if x[‘id’]==pid),None)
if p: add_news(f’©️{p[“name”]}をキャプテンに任命’,‘club’)
refresh_ui()

def set_pk_taker(pid):
sel=get_sel()
if not sel: return
sel[‘pk_taker_id’]=pid
p=next((x for x in sel[‘players’] if x[‘id’]==pid),None)
if p: add_news(f’⚽{p[“name”]}をPKシューターに指定’,‘club’)
refresh_ui()

def convert_position(pid,target_pos):
“”“ポジション変更/コンバート”””
p=player_by_id(pid)
if not p: return
p[‘target_pos’]=target_pos; p[‘convert_weeks’]=6  # 6週間でコンバート完了
add_news(f’🔄{p[“name”]}を{target_pos}にコンバート中（6週間）’,‘player’); refresh_ui()

def dispatch_overseas_scout(country):
“”“海外スカウト派遣”””
sel=get_sel()
if not sel: return
cost=50000
if sel[‘budget’]<cost: ui.notify(‘予算不足’); return
sel[‘budget’]-=cost; add_fin(‘海外スカウト派遣’,-cost,country)
game_state[‘overseas_scout’]={‘country’:country,‘weeks_left’:4}
add_news(f’🌍{country}に海外スカウトを派遣（4週間後に帰還）’,‘player’); refresh_ui()

def sign_overseas_player(pid):
“”“海外スカウト発掘選手の獲得”””
sel=get_sel()
if not sel: return
p=next((x for x in game_state.get(‘overseas_pool’,[]) if x[‘id’]==pid),None)
if not p: return
if not in_transfer_window(): ui.notify(‘移籍ウィンドウ外’); return
if sel[‘budget’]<p[‘value’]: ui.notify(‘予算不足’); return
sel[‘budget’]-=p[‘value’]; add_fin(‘移籍加入’,-p[‘value’],p[‘name’]); add_sf(‘transfers_in’,p[‘value’])
p[‘club’]=sel[‘name’]; sel[‘players’].append(p)
game_state[‘overseas_pool’]=[x for x in game_state[‘overseas_pool’] if x[‘id’]!=pid]
add_news(f’海外選手獲得: {p[“name”]}を{fmt_m(p[“value”])}で’,‘transfer’); refresh_ui()

def create_scout_pool():
sel=get_sel(); country=game_state[‘selected_country’] if not sel else sel[‘country’]
pool=[]
for i in range(10):
p=gen_player(country,‘ScoutPool’,900000+i)
sb=game_state[‘facilities’][‘scouting’]*2+(3 if has_skill(‘スカウト眼’) else 0)
sk=sum(s[‘skill’]//10 for s in game_state[‘staff’] if s[‘type’]==‘スカウト’)
for k in p[‘attrs’]: p[‘attrs’][k]=clamp(p[‘attrs’][k]+random.randint(0,sb+sk),30,99)
_recompute(p)
# スカウト不確実性: 実力の±10%の幅
p[‘scout_ovr_min’]=max(35,p[‘overall’]-8); p[‘scout_ovr_max’]=min(99,p[‘overall’]+8)
pool.append(p)
game_state[‘scout_pool’]=pool; refresh_ui()

def sign_scout(pid):
sel=get_sel()
if not sel: return
p=next((x for x in game_state.get(‘scout_pool’,[]) if x[‘id’]==pid),None)
if not p: return
if len(sel[‘players’])>=MAX_SQUAD: ui.notify(‘満員’); return
if not in_transfer_window(): ui.notify(‘移籍ウィンドウ外’); return
if sel[‘budget’]<p[‘value’]: ui.notify(‘予算不足’); return
sel[‘budget’]-=p[‘value’]; add_fin(‘移籍加入’,-p[‘value’],p[‘name’]); add_sf(‘transfers_in’,p[‘value’])
p[‘club’]=sel[‘name’]; sel[‘players’].append(p)
game_state[‘scout_pool’]=[x for x in game_state[‘scout_pool’] if x[‘id’]!=pid]
add_news(f’{p[“name”]}を{fmt_m(p[“value”])}で獲得’,‘transfer’); refresh_ui()

def youth_text(p):
diff=p[‘potential’]-p[‘overall’]
if p[‘potential’]>=80 and diff>=10: return ‘かなり有望’
elif p[‘potential’]>=72: return ‘伸びしろ十分’
elif p[‘potential’]>=65: return ‘将来性あり’
return ‘即戦力ではない’

def youth_rec(p):
if p[‘age’]>=19: return ‘昇格/放出必須’
if p[‘age’]>=18 and p[‘overall’]>=60: return ‘昇格推奨’
if p[‘potential’]-p[‘overall’]>=12: return ‘育成推奨’
return ‘様子見’

def refresh_youth_queue():
t=get_sel()
if t: game_state[‘youth_decision_queue’]=[p[‘id’] for p in t[‘youth’] if p[‘age’]>=18]

def promote_youth(pid):
t=get_sel()
if not t: return
p=next((x for x in t[‘youth’] if x[‘id’]==pid),None)
if not p: return
if len(t[‘players’])>=MAX_SQUAD: ui.notify(‘満員’); return
t[‘youth’]=[x for x in t[‘youth’] if x[‘id’]!=pid]; p[‘club’]=t[‘name’]; p[‘contract_years’]=max(p.get(‘contract_years’,0),3)
t[‘players’].append(p)
game_state[‘youth_decision_queue’]=[x for x in game_state[‘youth_decision_queue’] if x!=pid]
game_state[‘youth_promoted_count’]=game_state.get(‘youth_promoted_count’,0)+1
if game_state[‘youth_promoted_count’]>=5: check_achievement(‘youth_promoted’)
add_news(f’ユース昇格: {p[“name”]}’,‘player’); refresh_ui()

def retain_youth(pid):
t=get_sel()
if not t: return
p=next((x for x in t[‘youth’] if x[‘id’]==pid),None)
if not p or p[‘age’]>=19: ui.notify(‘19歳以上は不可’); return
p[‘contract_years’]=max(p.get(‘contract_years’,0),1)
game_state[‘youth_decision_queue’]=[x for x in game_state[‘youth_decision_queue’] if x!=pid]
add_news(f’ユース残留: {p[“name”]}’,‘player’); refresh_ui()

def release_youth(pid):
t=get_sel()
if not t: return
p=next((x for x in t[‘youth’] if x[‘id’]==pid),None)
if not p: return
t[‘youth’]=[x for x in t[‘youth’] if x[‘id’]!=pid]
game_state[‘youth_decision_queue’]=[x for x in game_state[‘youth_decision_queue’] if x!=pid]
add_news(f’ユース放出: {p[“name”]}’,‘player’); refresh_ui()

def refill_youth(team):
target=random.randint(MIN_YOUTH,MAX_YOUTH)
while len(team[‘youth’])<target:
p=gen_player(team[‘country’],team[‘name’],random.randint(100000,999999),True)
p[‘age’]=16; p[‘contract_years’]=random.randint(2,4); team[‘youth’].append(p)
if p[‘is_wonderkid’] and team[‘name’]==game_state.get(‘selected_club’):
game_state[‘wonderkid_found’]=game_state.get(‘wonderkid_found’,0)+1
if game_state[‘wonderkid_found’]>=3: check_achievement(‘wonder_scout’)
add_news(f’🌟世界的逸材加入: {p[“name”]}(POT {p[“potential”]})’,‘player’)

def poach_youth():
sel=get_sel()
if not sel or len(sel[‘youth’])>=MAX_YOUTH: ui.notify(‘枠満員’); return
srcs=[t for d in game_state[‘divisions’] for t in game_state[‘divisions’][d] if t[‘name’]!=sel[‘name’] and t[‘youth’]]
if not srcs: return
src=random.choice(srcs); cand=max(src[‘youth’],key=lambda p:p[‘potential’])
fee=max(20000,int(cand[‘value’]*0.35))
if sel[‘budget’]<fee: ui.notify(‘予算不足’); return
sel[‘budget’]-=fee; add_fin(‘ユース引き抜き’,-fee,cand[‘name’]); add_sf(‘transfers_in’,fee)
src[‘youth’]=[x for x in src[‘youth’] if x[‘id’]!=cand[‘id’]]
cand[‘club’]=sel[‘name’]; cand[‘contract_years’]=random.randint(2,4); sel[‘youth’].append(cand)
add_news(f’ユース引き抜き: {cand[“name”]}（{src[“name”]}から{fmt_m(fee)}）’,‘transfer’); refresh_ui()

def set_youth_policy(pol):
game_state[‘youth_policy’]=pol; add_news(f’育成方針→{pol}’,‘club’); refresh_ui()

# =========================================================

# 施設・スタッフ

# =========================================================

def upgrade_facility(ft):
sel=get_sel()
if not sel: return
lv=game_state[‘facilities’][ft]
if lv>=5: ui.notify(‘最大Lv’); return
cost=150000*lv
if sel[‘budget’]<cost: ui.notify(‘資金不足’); return
sel[‘budget’]-=cost; game_state[‘facilities’][ft]+=1; add_fin(‘施設投資’,-cost,ft); add_sf(‘facility’,cost)
game_state[‘club_brand’]=clamp(game_state[‘club_brand’]+1,0,100)
if all(v>=5 for v in game_state[‘facilities’].values()): check_achievement(‘max_facility’)
add_news(f’{ft}→Lv{game_state[“facilities”][ft]}に強化’,‘club’); refresh_ui()

def upgrade_youth_fac():
sel=get_sel()
if not sel: return
lv=game_state[‘facilities’][‘youth’]
if lv>=5: ui.notify(‘最大Lv’); return
cost=200000*lv
if sel[‘budget’]<cost: ui.notify(‘資金不足’); return
sel[‘budget’]-=cost; game_state[‘facilities’][‘youth’]+=1; add_fin(‘施設投資’,-cost,‘ユース’); add_sf(‘facility’,cost)
add_news(f’ユース施設→Lv{game_state[“facilities”][“youth”]}’,‘club’); refresh_ui()

def expand_stadium():
sel=get_sel()
if not sel: return
inc=random.randint(3000,8000); cost=inc*35
if sel[‘budget’]<cost: ui.notify(‘資金不足’); return
sel[‘budget’]-=cost; sel[‘stadium_capacity’]+=inc; add_fin(‘スタジアム拡張’,-cost,‘建設’); add_sf(‘facility’,cost)
game_state[‘club_brand’]=clamp(game_state[‘club_brand’]+2,0,100)
add_news(f’スタジアム拡張+{inc}席’,‘club’); refresh_ui()

def upgrade_vip():
sel=get_sel()
if not sel: return
lv=sel.get(‘vip_level’,0)
if lv>=3: ui.notify(‘VIP最大Lv3’); return
cost=300000*(lv+1)
if sel[‘budget’]<cost: ui.notify(‘資金不足’); return
sel[‘budget’]-=cost; sel[‘vip_level’]=lv+1; add_fin(‘VIP席投資’,-cost,‘建設’); add_sf(‘facility’,cost)
add_news(f’VIPエリアLv{sel[“vip_level”]}に拡充’,‘club’); refresh_ui()

def hire_staff():
sel=get_sel()
if not sel or sel[‘budget’]<60000: ui.notify(‘予算不足’); return
s={‘type’:random.choice(STAFF_TYPES),‘skill’:random.randint(50,90),‘salary’:random.randint(4000,9000)}
sel[‘budget’]-=60000; game_state[‘staff’].append(s); add_fin(‘スタッフ雇用’,-60000,s[‘type’])
add_news(f’スタッフ加入: {s[“type”]}(skill {s[“skill”]})’,‘club’); refresh_ui()

def set_tactic(tn):
t=get_sel()
if t: t[‘tactic’]=tn; add_news(f’戦術→{tn}’,‘club’); refresh_ui()

def set_formation(fn):
t=get_sel()
if t: t[‘formation’]=fn; add_news(f’フォーメーション→{fn}’,‘club’); refresh_ui()

def learn_skill(sk):
if game_state.get(‘manager_skill_points’,0)<=0: ui.notify(‘SPなし’); return
if sk in game_state.get(‘manager_skills’,[]): ui.notify(‘習得済み’); return
game_state.setdefault(‘manager_skills’,[]).append(sk); game_state[‘manager_skill_points’]-=1
add_news(f’📚監督スキル:「{sk}」習得’,‘club’); refresh_ui()

def set_training_focus(pid,focus):
p=player_by_id(pid)
if p: p[‘training_focus’]=focus; add_news(f’{p[“name”]}のトレーニング集中: {focus}’,‘player’); refresh_ui()

def set_role_wish(pid,role):
p=player_by_id(pid)
if p: p[‘role_wish’]=role; add_news(f’{p[“name”]}の希望役割: {role}’,‘player’); refresh_ui()

# =========================================================

# CPU管理

# =========================================================

def cpu_contracts(t):
for p in list(t[‘players’]):
p[‘contract_years’]-=1
if p[‘contract_years’]<=0:
cost=int(p[‘wage’]*8)
if t[‘budget’]>cost and random.random()<(0.75 if p[‘overall’]>=65 else 0.45):
t[‘budget’]-=cost; p[‘wage’]=int(p[‘wage’]*random.uniform(1.05,1.20)); p[‘contract_years’]=random.randint(2,4)
else: t[‘players’].remove(p)
while len(t[‘players’])<18:
np=gen_player(t[‘country’],t[‘name’],random.randint(10000,99999))
np[‘overall’]=clamp(np[‘overall’]+random.randint(-4,2),45,75); t[‘players’].append(np)

def cpu_transfers():
for d in game_state[‘divisions’]:
for t in game_state[‘divisions’][d]:
if t[‘name’]==game_state[‘selected_club’]: continue
if random.random()<0.25 and t[‘budget’]>200000:
p=gen_player(t[‘country’],t[‘name’],random.randint(10000,99999))
if p[‘overall’]>60 and t[‘budget’]>p[‘value’]:
t[‘budget’]-=p[‘value’]; t[‘players’].append(p)

def run_cpu():
for d in game_state[‘divisions’]:
for t in game_state[‘divisions’][d]:
if t[‘name’]==game_state[‘selected_club’]: continue
cpu_contracts(t); refill_youth(t)
cpu_transfers()

# =========================================================

# 昇降格・表彰

# =========================================================

def do_promotion():
d1=sorted_table(‘D1’); d2=sorted_table(‘D2’); d3=sorted_table(‘D3’)
rel1=d1[-2:]; prom2=d2[:2]; rel2=d2[-2:]; prom3=d3[:2]
def mv(t,fr,to):
game_state[‘divisions’][fr]=[x for x in game_state[‘divisions’][fr] if x[‘name’]!=t[‘name’]]
game_state[‘divisions’][to].append(t)
for t in rel1:
mv(t,‘D1’,‘D2’); add_news(f’🔻降格: {t[“name”]} D1→D2’,‘club’)
if t[‘name’]==game_state[‘selected_club’]: game_state[‘club_brand’]=clamp(game_state[‘club_brand’]-5,0,100)
for t in prom2:
if t not in rel1:
mv(t,‘D2’,‘D1’); add_news(f’🔺昇格: {t[“name”]} D2→D1’,‘club’)
if t[‘name’]==game_state[‘selected_club’]:
game_state[‘club_brand’]=clamp(game_state[‘club_brand’]+8,0,100); check_achievement(‘promoted’)
for t in rel2:
if t not in prom2: mv(t,‘D2’,‘D3’); add_news(f’🔻降格: {t[“name”]} D2→D3’,‘club’)
for t in prom3:
if t not in rel2: mv(t,‘D3’,‘D2’); add_news(f’🔺昇格: {t[“name”]} D3→D2’,‘club’)
country=game_state[‘selected_country’]; used={t[‘name’] for d in game_state[‘divisions’] for t in game_state[‘divisions’][d]}
for dn,(rmin,rmax) in [(‘D1’,(62,78)),(‘D2’,(54,70)),(‘D3’,(46,64))]:
while len(game_state[‘divisions’][dn])<10:
nt=create_team(country,_rname(country,used),rmin,rmax); init_stats(); game_state[‘divisions’][dn].append(nt)
while len(game_state[‘divisions’][dn])>10: game_state[‘divisions’][dn].pop()

def prize_money(dn,rank):
if dn==‘D1’: t={1:900000,2:700000,3:550000,4:420000,5:320000,6:240000,7:180000,8:140000,9:100000,10:70000}
elif dn==‘D2’: t={1:500000,2:380000,3:280000,4:220000,5:170000,6:130000,7:100000,8:80000,9:60000,10:40000}
else: t={1:300000,2:220000,3:170000,4:130000,5:100000,6:80000,7:60000,8:50000,9:40000,10:30000}
return t.get(rank,0)

def calc_awards():
pl=all_players()
if not pl: return
gb=max(pl,key=lambda p:p[‘stats’][‘goals’]); mvp=max(pl,key=lambda p:p[‘stats’][‘goals’]*4+p[‘stats’][‘assists’]*3+p[‘stats’][‘mom’]*5)
game_state[‘season_awards’]={‘golden_boot’:gb,‘mvp’:mvp}
game_state[‘history_awards’].append({‘season’:game_state[‘season’],‘golden_boot’:gb[‘name’],‘mvp’:mvp[‘name’]})
add_news(f’年間MVP: {mvp[“name”]}’,‘club’); add_news(f’得点王: {gb[“name”]}({gb[“stats”][“goals”]}G)’,‘club’)

def update_hof():
club=get_sel()
if not club: return
for p in club[‘players’]:
score=p[‘stats’][‘goals’]*3+p[‘stats’][‘assists’]*2+p[‘stats’][‘mom’]*4
e={‘name’:p[‘name’],‘score’:score,‘reason’:‘シーズン表彰’}
if score>120 and e not in game_state[‘club_hall_of_fame’]:
game_state[‘club_hall_of_fame’].append(e); add_news(f’殿堂入り: {p[“name”]}’,‘club’)

def declare_goal(goal):
sel=get_sel()
if not sel: return
sel[‘player_season_goal’]=goal; game_state[‘season_goal_declared’]=True
bonus={‘優勝を狙う’:5,‘上位進出’:3,‘残留で十分’:2,‘昇格を目指す’:4}.get(goal,0)
game_state[‘board_rating’]=clamp(game_state[‘board_rating’]+bonus,0,100)
add_news(f’⚽今季目標:「{goal}」’,‘club’); refresh_ui()

def check_goal(dn,rank):
sel=get_sel()
if not sel or not sel.get(‘player_season_goal’): return
goal=sel[‘player_season_goal’]
ok=(goal==‘優勝を狙う’ and rank==1) or (goal==‘上位進出’ and rank<=4) or (goal==‘残留で十分’ and rank<=8) or (goal==‘昇格を目指す’ and rank<=2 and dn in [‘D2’,‘D3’])
if ok:
sel[‘budget’]+=100000; game_state[‘board_rating’]=clamp(game_state[‘board_rating’]+10,0,100)
game_state[‘club_brand’]=clamp(game_state[‘club_brand’]+5,0,100); add_news(f’🎯目標「{goal}」達成！{fmt_m(100000)}’,‘club’)
else:
game_state[‘board_rating’]=clamp(game_state[‘board_rating’]-5,0,100); add_news(f’❌目標「{goal}」未達成’,‘club’)
sel[‘player_season_goal’]=None; game_state[‘season_goal_declared’]=False

def reset_fin():
game_state[‘season_finance’]={k:0 for k in [‘sponsor’,‘matchday’,‘transfers_in’,‘transfers_out’,‘prize’,‘wages’,‘facility’,‘staff’,‘broadcast’,‘merch’,‘naming_rights’,‘preseason’,‘loan_interest’,‘insurance’]}

def start_domestic_cup():
teams=[t for d in game_state[‘divisions’] for t in game_state[‘divisions’][d]]
random.shuffle(teams)
game_state[‘domestic_cup’]={‘teams’:teams[:16],‘round’:1,‘winner’:None}
add_news(‘🏆国内カップ戦が開幕！16クラブ参加’,‘cup’)

def play_cup_round():
cup=game_state.get(‘domestic_cup’)
if not cup or cup.get(‘winner’): return
winners=[]
for i in range(0,len(cup[‘teams’]),2):
if i+1>=len(cup[‘teams’]): winners.append(cup[‘teams’][i]); continue
a,b=cup[‘teams’][i],cup[‘teams’][i+1]
ga,gb,*_=simulate_match_full(a,b,cup=True); w=a if ga>gb else b; winners.append(w)
sel=get_sel()
if sel and sel[‘name’] in (a[‘name’],b[‘name’]): add_news(f’カップ: {a[“name”]} {ga}-{gb} {b[“name”]}’,‘cup’)
cup[‘teams’]=winners; cup[‘round’]+=1
if len(cup[‘teams’])==1:
champ=cup[‘teams’][0]; cup[‘winner’]=champ[‘name’]; champ[‘budget’]+=500000
add_news(f’🏆国内カップ優勝: {champ[“name”]}’,‘cup’)
if champ[‘name’]==game_state[‘selected_club’]:
game_state[‘club_brand’]=clamp(game_state[‘club_brand’]+8,0,100); check_achievement(‘cup_winner’)
refresh_ui()

def start_intl_cup():
teams=[]
for d in game_state[‘divisions’]: tbl=sorted_table(d); teams+=tbl[:2]
random.shuffle(teams); game_state[‘international_cup’]={‘teams’:teams[:8],‘round’:1}

def play_intl_round():
cup=game_state.get(‘international_cup’)
if not cup or len(cup[‘teams’])<=1: return
winners=[]
for i in range(0,len(cup[‘teams’]),2):
if i+1>=len(cup[‘teams’]): winners.append(cup[‘teams’][i]); continue
a,b=cup[‘teams’][i],cup[‘teams’][i+1]; ga,gb,*_=simulate_match_full(a,b,cup=True)
winners.append(a if ga>=gb else b)
cup[‘teams’]=winners; cup[‘round’]+=1
if len(cup[‘teams’])==1:
champ=cup[‘teams’][0]; add_news(f’国際大会優勝: {champ[“name”]}’,‘cup’)
if champ[‘name’]==game_state[‘selected_club’]:
game_state[‘club_brand’]=clamp(game_state[‘club_brand’]+10,0,100); check_achievement(‘intl_winner’)
refresh_ui()

# =========================================================

# ユース大会

# =========================================================

def maybe_spawn_legacy_player(team):
“”“15シーズン以上経過したら引退済み殿堂選手の子供がユースに登場”””
if game_state[‘season’] < 15: return
hof=game_state.get(‘club_hall_of_fame’,[])
if not hof or random.random()>0.15: return
parent=random.choice(hof)
country=team.get(‘country’,‘England’)
p=gen_player(country,team[‘name’],random.randint(800000,899999),True)
# 親の名字を受け継ぐ
parent_lastname=parent[‘name’].split()[-1] if ’ ’ in parent[‘name’] else parent[‘name’]
firstname=random.choice(COUNTRY_NAME_POOLS[country][‘first’])
p[‘name’]=f’{firstname} {parent_lastname} Jr.’
p[‘is_wonderkid’]=True
p[‘potential’]=random.randint(82,94)
for k in p[‘attrs’]: p[‘attrs’][k]=clamp(p[‘attrs’][k]+random.randint(4,10),50,95)
_recompute(p); p[‘age’]=16; p[‘contract_years’]=3
team[‘youth’].append(p)
add_news(f’🌟伝説の2世: {p[“name”]}がアカデミーに加入（{parent[“name”]}の子）POT{p[“potential”]}’,‘player’)

def run_youth_cup(team):
“”“シーズン終了時にユース大会を開催。施設Lvに応じて成長ボーナス”””
if not team.get(‘youth’): return
fac_lv=game_state[‘facilities’][‘youth’]
# 参加チームはユースがいる全クラブ
participants=[t for d in game_state[‘divisions’] for t in game_state[‘divisions’][d] if t[‘youth’]]
if len(participants)<4: return
# 簡易トーナメント（チーム総合力で決定）
def youth_strength(t):
return avg([p[‘overall’] for p in t[‘youth’]]) if t[‘youth’] else 0
ranked=sorted(participants,key=youth_strength,reverse=True)
winner=ranked[0]
# 優勝チームのユース選手に成長ボーナス
bonus=fac_lv*random.randint(1,3)
for p in winner[‘youth’]:
attr=random.choice(list(p[‘attrs’].keys()))
p[‘attrs’][attr]=clamp(p[‘attrs’][attr]+bonus,30,99)
_recompute(p)
add_news(f’🏅ユース大会優勝: {winner[“name”]}（育成ボーナス+{bonus}）’,‘cup’)
if winner[‘name’]==game_state[‘selected_club’]:
game_state[‘locker_room_mood’]=clamp(game_state[‘locker_room_mood’]+5,0,100)
add_news(‘自クラブのユースが大会を制覇！ロッカールームが盛り上がっている’,‘club’)

# =========================================================

# メインゲームループ

# =========================================================

def get_week_pairs(dn,week):
teams=game_state[‘divisions’][dn]; names=[t[‘name’] for t in teams]
rot=names[:]; seed=game_state[‘season’]*1000+week+(1 if dn==‘D2’ else 2 if dn==‘D3’ else 0)
random.Random(seed).shuffle(rot)
pairs=[(rot[i],rot[i+1]) for i in range(0,len(rot)-1,2) if i+1<len(rot)]
if week%2==0: pairs=[(b,a) for a,b in pairs]
return pairs

def play_next_week():
sel=get_sel()
if not sel: ui.notify(‘クラブを選択してください’); return
if game_state.get(‘preseason_phase’) and not sel.get(‘preseason_done’): nav_state[‘tab’]=‘matches’; refresh_ui(); return
if game_state.get(‘manager_fired’): ui.notify(‘監督評価が危機的！’,‘warning’)
# 複数週一括進行
if game_state.get(‘bulk_advancing’) and game_state.get(‘bulk_weeks_left’,0)>0:
game_state[‘bulk_weeks_left’]-=1
if game_state[‘bulk_weeks_left’]<=0 or game_state.get(‘pending_event’):
game_state[‘bulk_advancing’]=False
weather=roll_weather()
if weather in [‘雨’,‘雪’,‘強風’]: add_news(f’🌦️今節の天候: {weather}’,‘match’)
game_state[‘halftime_data’]=None; nav_state[‘halftime_mode’]=False
game_state[‘pending_press’]=True
won=drew=lost=False; results=[]
for cd in [‘D1’,‘D2’,‘D3’]:
for hn,an in get_week_pairs(cd,game_state[‘week’]):
ht=find_team(hn); at=find_team(an)
ga1,gb1=simulate_half(ht,at,home_team=hn)
if sel[‘name’] in (hn,an) and not game_state.get(‘halftime_data’) and not game_state.get(‘bulk_advancing’):
game_state[‘halftime_data’]={‘home’:hn,‘away’:an,‘ha_team’:ht,‘away_team’:at,‘ga1’:ga1,‘gb1’:gb1}
nav_state[‘halftime_mode’]=True; continue
ga,gb,att,rev,stats,extra=simulate_match_full(ht,at)
results.append(f’{hn} {ga}-{gb} {an}’)
if sel[‘name’] in (hn,an):
my=ga if sel[‘name’]==hn else gb; op=gb if sel[‘name’]==hn else ga
game_state[‘last_match’]={‘result’:results[-1],‘attendance’:att,‘revenue’:rev,‘stats’:stats,‘mom’:extra[‘mom’],‘highlights’:extra[‘highlights’],‘derby’:extra[‘derby’],‘weather’:weather}
if my>op: won=True
elif my==op: drew=True
else: lost=True
htd=game_state.get(‘halftime_data’)
if htd and not nav_state.get(‘halftime_mode’):
ht=htd[‘ha_team’]; at=htd[‘away_team’]
ga2,gb2=simulate_half(ht,at,home_team=htd[‘home’])
ga=min(8,htd[‘ga1’]+ga2); gb=min(8,htd[‘gb1’]+gb2)
mom,sclog,cards=_match_stats_full(ht,at,ga,gb,WEATHER.get(weather,WEATHER[‘晴れ’]))
att=_attendance(ht,at,ht[‘name’] in at.get(‘rivals’,[]))
rev=_match_income(ht,att)
result_text=f’{htd[“home”]} {ga}-{gb} {htd[“away”]}’; results.append(result_text)
game_state[‘last_match’]={‘result’:result_text,‘attendance’:att,‘revenue’:rev,‘stats’:{},‘mom’:mom,‘highlights’:[f’前半: {htd[“ga1”]}-{htd[“gb1”]}’,f’後半: {ga2}-{gb2}’],‘derby’:ht[‘name’] in at.get(‘rivals’,[]),‘weather’:weather}
my=ga if sel[‘name’]==htd[‘home’] else gb; op=gb if sel[‘name’]==htd[‘home’] else ga
if my>op: won=True
elif my==op: drew=True
else: lost=True
_update_table(ht,ga,gb); _update_table(at,gb,ga)
_update_fanbase(ht,‘win’ if ga>gb else(‘draw’ if ga==gb else ‘loss’))
_update_fanbase(at,‘win’ if gb>ga else(‘draw’ if ga==gb else ‘loss’))
if ga>gb and ht[‘name’]==game_state[‘selected_club’]: _pay_win_bonus(ht)
elif gb>ga and at[‘name’]==game_state[‘selected_club’]: _pay_win_bonus(at)
game_state[‘halftime_data’]=None
weekly_sponsor(sel); weekly_expenses(sel); weekly_broadcast(sel); weekly_merch(sel); weekly_naming_rights(sel); weekly_portrait_income(sel); weekly_overseas_scout(sel)
process_loan_returns(); process_intl_calls(sel)
update_player_feelings(sel,won,drew,lost); update_player_states(sel); update_chemistry(sel)
update_fan_happiness(sel,won,drew,lost); update_manager_rating(sel,won,drew,lost); update_board_rating(sel)
if game_state[‘manager_rating’]>=45 and game_state[‘board_rating’]>=40 and game_state.get(‘manager_fired’):
game_state[‘manager_fired’]=False; add_news(‘監督評価回復、続投決定’,‘club’)
recover_players(); gen_domestic_offers(); gen_foreign_offer(); gen_loan_offers()
agent_intervention(sel); apply_individual_training(sel); check_retirements(sel)
gen_random_event(); gen_manager_offers()
if won:
game_state[‘win_streak’]=game_state.get(‘win_streak’,0)+1
if game_state[‘win_streak’]>=5: check_achievement(‘unbeaten_5’)
if sel.get(‘season_stats’,{}).get(‘w’,0)==1: check_achievement(‘first_win’)
else: game_state[‘win_streak’]=0
if sel[‘budget’]>=5000000: check_achievement(‘rich_club’)
dn=div_of(sel[‘name’]); tbl=sorted_table(dn)
rank=next((i+1 for i,t in enumerate(tbl) if t[‘name’]==sel[‘name’]),10)
game_state.setdefault(‘rank_history’,[]).append({‘week’:game_state[‘week’],‘rank’:rank,‘div’:dn})
sel.setdefault(‘rank_history’,[]).append(rank)
if game_state.get(‘last_match’):
lm=game_state[‘last_match’]
add_news(f’観客{lm[“attendance”]:,}人|収入{fmt_m(lm[“revenue”])}’,‘match’)
add_news(f’MOM: {lm[“mom”][“name”]}’,‘match’)
if lm.get(‘derby’): add_news(f’ダービー: {lm[“result”]}’,‘match’)
for r in reversed(results[-6:]): add_news(f’第{game_state[“week”]}節: {r}’,‘match’)
wk=game_state[‘week’]
if wk==CUP_START: start_domestic_cup()
elif wk>CUP_START and (wk-CUP_START)%2==0:
cup=game_state.get(‘domestic_cup’)
if cup and not cup.get(‘winner’): play_cup_round()
if wk==sel.get(‘board_meeting_week’,8): trigger_board_meeting()
if random.random()<0.03 and not sel.get(‘naming_rights’) and not game_state.get(‘naming_rights_offer’): offer_naming_rights()
if game_state.get(‘injury_insurance_active’):
cost=8000; sel[‘budget’]-=cost; add_sf(‘insurance’,cost)
game_state[‘week’]+=1
if game_state[‘week’]>SEASON_WEEKS: season_end()
elif nav_state.get(‘halftime_mode’): refresh_ui()
elif game_state.get(‘bulk_advancing’) and game_state.get(‘bulk_weeks_left’,0)>0 and not game_state.get(‘pending_event’):
play_next_week()
else: refresh_ui()

def do_halftime(tactic_choice):
htd=game_state.get(‘halftime_data’)
if not htd: return
htd[‘ht_tac_a’]=tactic_choice; nav_state[‘halftime_mode’]=False
add_news(f’ハーフタイム指示: 後半戦術→{tactic_choice}’,‘match’)
# 後半を自動実行（再度「次の週へ」を押す必要をなくす）
play_next_week()

def bulk_advance(n):
“”“複数週一括進行”””
game_state[‘bulk_advancing’]=True; game_state[‘bulk_weeks_left’]=n
add_news(f’⏩{n}週まとめて進行中…’,‘club’); play_next_week()

def season_end():
sel=get_sel()
if not sel: return
calc_awards(); update_hof()
dn=div_of(sel[‘name’]); tbl=sorted_table(dn)
rank=next((i+1 for i,t in enumerate(tbl) if t[‘name’]==sel[‘name’]),10)
check_goal(dn,rank)
pm=prize_money(dn,rank); sel[‘budget’]+=pm; add_fin(‘リーグ賞金’,pm,f’{dn} Rank {rank}’); add_sf(‘prize’,pm)
add_news(f’リーグ賞金{fmt_m(pm)}獲得’,‘club’)
if dn==‘D2’ and rank<=2: sel[‘budget’]+=350000; add_news(‘昇格ボーナス$350,000’,‘club’)
if dn==‘D3’ and rank<=2: sel[‘budget’]+=220000; add_news(‘昇格ボーナス$220,000’,‘club’)
if rank==1: check_achievement(‘first_title’)
# クラブ歴史書に記録
sel.setdefault(‘season_history’,[]).append({‘season’:game_state[‘season’],‘div’:dn,‘rank’:rank,‘goals’:sum(p[‘stats’][‘goals’] for p in sel[‘players’])})
game_state[‘club_history’].append({‘season’:game_state[‘season’],‘club’:sel[‘name’],‘div’:dn,‘rank’:rank})
do_promotion(); process_expiry(); run_cpu()
tr_b=game_state[‘facilities’][‘training’]*0.3; ass_b=sum(s[‘skill’]*0.003 for s in game_state[‘staff’] if s[‘type’]==‘アシスタント’); youth_b=1.15 if has_skill(‘育成型’) else 1.0
for d in game_state[‘divisions’]:
for t in game_state[‘divisions’][d]:
t[‘season_stats’]={‘p’:0,‘w’:0,‘d’:0,‘l’:0,‘gf’:0,‘ga’:0,‘gd’:0,‘pts’:0}
for p in t[‘players’]:
p[‘age’]+=1; gc=0.45+ass_b; dc=0.35
if p.get(‘growth_type’)==‘早熟’:
if p[‘age’]<=22: gc=0.60
elif p[‘age’]>=27: dc=0.50
if p.get(‘growth_type’)==‘晩成’:
if p[‘age’]<=21: gc=0.30
elif 24<=p[‘age’]<=29: gc=0.55
if p[‘age’]<=23 and p[‘overall’]<p[‘potential’] and random.random()<gc:
for k in p[‘attrs’]:
if random.random()<0.4: p[‘attrs’][k]=clamp(p[‘attrs’][k]+random.randint(0,2)+int(tr_b),30,99)
elif p[‘age’]>=30 and random.random()<dc:
for k in p[‘attrs’]:
if random.random()<0.35: p[‘attrs’][k]=clamp(p[‘attrs’][k]-random.randint(0,1),30,99)
if p.get(‘injury_severity’)==‘重傷’:
for k in p[‘attrs’]: p[‘attrs’][k]=clamp(p[‘attrs’][k]-random.randint(0,1),30,99)
_recompute(p); p[‘stamina’]=100
if p.get(‘injury_severity’)!=‘重傷’: p[‘injury_weeks’]=0; p[‘injury_severity’]=‘なし’
p[‘state’]=‘normal’; p[‘state_weeks’]=0
for p in t[‘youth’]:
p[‘age’]+=1
pol=YOUTH_POLICIES.get(game_state[‘youth_policy’],YOUTH_POLICIES[‘バランス’])
for attr in p[‘attrs’]:
g=int(random.randint(0,2)*youth_b)
if attr==‘SPD’: g=int(g*pol[‘SPD’])
if attr in [‘TEC’,‘PAS’]: g=int(g*pol[‘TEC’])
if attr==‘PHY’: g=int(g*pol[‘PHY’])
p[‘attrs’][attr]=clamp(p[‘attrs’][attr]+g,30,99)
_recompute(p)
refill_youth(t)
run_youth_cup(get_sel()) if get_sel() else None
if get_sel(): maybe_spawn_legacy_player(get_sel())
refresh_youth_queue(); gen_sponsor_nego(); start_intl_cup(); game_state[‘domestic_cup’]=None
game_state[‘season’]+=1; game_state[‘week’]=1; game_state[‘season_goal_declared’]=False
game_state[‘preseason_phase’]=True; sel[‘preseason_done’]=False
reset_fin(); add_news(‘シーズン終了。新シーズンへ’,‘club’)
if game_state[‘season’]>=3: check_achievement(‘season3’)
refresh_ui()

def save_game():
try:
data=json.dumps(game_state,ensure_ascii=False,default=str)
ui.download(data.encode(‘utf-8’),‘club_strive_v5_save.json’); add_news(‘💾セーブ完了’,‘club’)
except Exception as e: ui.notify(f’セーブ失敗: {e}’)

def load_game(content:bytes):
global game_state
try:
game_state=json.loads(content.decode(‘utf-8’)); init_stats(); add_news(‘📂ロード完了’,‘club’); refresh_ui(); ui.notify(‘ロード成功！’)
except Exception as e: ui.notify(f’ロード失敗: {e}’)

def new_world(country):
global game_state
game_state=build_world(country); init_stats()
for d in game_state[‘divisions’]:
for t in game_state[‘divisions’][d]:
t[‘sponsor’]=_gen_sponsor(t[‘country’],d)
nav_state[‘tab’]=‘dashboard’; refresh_ui()

def select_club(name):
game_state[‘selected_club’]=name; t=get_sel()
if t and not t.get(‘sponsor’): t[‘sponsor’]=_gen_sponsor(t[‘country’],div_of(t[‘name’]))
refresh_youth_queue(); add_news(f’クラブ選択: {name}’,‘club’); refresh_ui()

# =========================================================

# UI

# =========================================================

def render_status():
status_box.clear()
with status_box:
with ui.card().classes(‘w-full q-mb-sm’):
ui.label(APP_TITLE).classes(‘text-h5’)
ui.label(f’S{game_state[“season”]} W{game_state[“week”]}/{SEASON_WEEKS}’).classes(‘text-subtitle2’)
weather=get_weather(); wc_col=‘text-blue’ if weather in [‘雨’,‘雪’] else(‘text-orange’ if weather==‘強風’ else ‘’)
ui.label(f’天候: {weather}’).classes(f’text-body2 {wc_col}’)
if game_state.get(‘manager_fired’): ui.label(‘🚨監督評価危機！’).classes(‘text-red’)
if game_state.get(‘financial_crisis’): ui.label(‘💸財政危機！’).classes(‘text-red’)
ui.label(‘🔓移籍中’ if in_transfer_window() else ‘🔒移籍外’).classes(‘text-caption’)
ui.separator()
t=get_sel()
if t:
dn=div_of(t[‘name’]); tbl=sorted_table(dn) if dn else []
rank=next((i+1 for i,x in enumerate(tbl) if x[‘name’]==t[‘name’]),’-’)
ui.label(f’🏟 {t[“name”]}’).classes(‘text-body1 text-bold’)
ui.label(f’{dn} {rank}位 | 評判{t[“reputation”]}’).classes(‘text-body2’)
ui.label(f’予算: {fmt_m(t[“budget”])}’).classes(‘text-body2’+(’ text-red’ if t[‘budget’]<0 else ‘’))
ui.label(f’人気: {t[“fan_base”]:,} | ブランド: {game_state[“club_brand”]}’).classes(‘text-body2’)
ui.label(f’ケミストリー: {t.get(“chemistry”,50)}/100’).classes(‘text-body2’)
ui.label(f’監督exp: {game_state.get(“manager_exp”,0)} SP: {game_state.get(“manager_skill_points”,0)}’).classes(‘text-body2’)
loans=game_state.get(‘bank_loans’,[])
if loans: ui.label(f’🏦ローン残: {len(loans)}件’).classes(‘text-caption text-orange’)
else: ui.label(‘クラブ未選択’).classes(‘text-body2’)

def render_dashboard():
dashboard_box.clear()
with dashboard_box:
if not game_state[‘selected_club’]:
with ui.card().classes(‘w-full q-mb-sm’):
ui.label(‘クラブを選択’).classes(‘text-h6’)
for dn in [‘D1’,‘D2’,‘D3’]:
ui.label(dn).classes(‘text-subtitle1 text-bold’)
for t in game_state[‘divisions’][dn]:
ui.button(f’{t[“name”]} | 評判{t[“reputation”]} | {fmt_m(t[“budget”])}’,on_click=lambda e,n=t[‘name’]:select_club(n)).classes(‘w-full q-mb-xs’)
return
t=get_sel(); dn=div_of(t[‘name’]); tbl=sorted_table(dn)
rank=next((i+1 for i,x in enumerate(tbl) if x[‘name’]==t[‘name’]),10)

```
    # プレシーズン
    if game_state.get('preseason_phase') and not t.get('preseason_done'):
        with ui.card().classes('w-full q-mb-sm'):
            ui.label('⚽プレシーズン').classes('text-h6')
            ui.button('プレシーズンを実施する（親善試合3試合）',on_click=run_preseason).props('color=primary')

    # ハーフタイム
    if nav_state.get('halftime_mode') and game_state.get('halftime_data'):
        htd=game_state['halftime_data']
        with ui.card().classes('w-full q-mb-sm'):
            ui.label(f'⏱️ ハーフタイム｜前半終了: {htd["home"]} {htd["ga1"]}-{htd["gb1"]} {htd["away"]}').classes('text-h6')
            ui.label('後半の戦術指示を選んでください').classes('text-body2')
            with ui.row():
                for tac in TACTICS: ui.button(tac,on_click=lambda e,tc=tac:do_halftime(tc)).props('color=primary')
            ui.button('そのまま継続',on_click=lambda: do_halftime(t.get('tactic','バランス'))).props('color=secondary')
        # テキスト実況
        with ui.card().classes('w-full q-mb-sm'):
            ui.label('📺テキスト実況（前半）').classes('text-h6')
            evts=game_state.get('live_commentary',[])
            for e in [x for x in evts if x['t']<=45][:12]:
                apos="'"; ui.label(f'{e["t"]}{apos} {e["txt"]}').classes('text-body2')
        return

    # ランダムイベント
    if game_state.get('pending_event'):
        evt=game_state['pending_event']
        with ui.card().classes('w-full q-mb-sm'):
            ui.label(f'📌イベント: {evt["text"]}').classes('text-h6')
            with ui.row():
                for ch in evt['choices']: ui.button(ch,on_click=lambda e,c=ch:resolve_event(c)).props('color=primary')

    # プレスカンファレンス
    if game_state.get('pending_press'):
        with ui.card().classes('w-full q-mb-sm'):
            ui.label('📰試合前プレスカンファレンス').classes('text-h6')
            with ui.row():
                for ch in ['強気発言','慎重姿勢','選手を称える','批判を受け入れる']:
                    ui.button(ch,on_click=lambda e,c=ch:do_press(c)).props('color=primary')

    # 目標宣言
    if not game_state.get('season_goal_declared') and not t.get('player_season_goal'):
        with ui.card().classes('w-full q-mb-sm'):
            ui.label('📋今季目標を宣言').classes('text-h6')
            with ui.row():
                for g in ['優勝を狙う','上位進出','残留で十分','昇格を目指す']:
                    ui.button(g,on_click=lambda e,x=g:declare_goal(x)).props('color=primary')

    # 監督キャリアオファー
    offers=game_state.get('manager_career_offers',[])
    if offers:
        with ui.card().classes('w-full q-mb-sm'):
            ui.label('📨監督オファー').classes('text-h6')
            for club_name in offers:
                ot=find_team(club_name)
                ui.label(f'{club_name} | 評判{ot["reputation"] if ot else "?"}').classes('text-body2')
                ui.button(f'{club_name}に転身',on_click=lambda e,cn=club_name:accept_manager_offer(cn)).props('color=accent')
            ui.button('全て断る',on_click=lambda: game_state.update({'manager_career_offers':[]}) or refresh_ui()).props('flat')

    # ネーミングライツ
    if game_state.get('naming_rights_offer'):
        nr=game_state['naming_rights_offer']
        with ui.card().classes('w-full q-mb-sm'):
            ui.label('💼ネーミングライツ打診').classes('text-h6')
            ui.label(f'{nr["company"]} | 一時金{fmt_m(nr["upfront"])} | 週次{fmt_m(nr["weekly"])}').classes('text-body2')
            with ui.row():
                ui.button('契約する',on_click=accept_naming_rights).props('color=positive')
                ui.button('断る',on_click=reject_naming_rights).props('color=negative')

    # 買収オファー
    if game_state.get('buyout_offer'):
        bo=game_state['buyout_offer']
        with ui.card().classes('w-full q-mb-sm'):
            ui.label(f'💰{bo["type"]}買収オファー').classes('text-h6')
            ui.label(f'+{fmt_m(bo["budget_boost"])}').classes('text-body2 text-positive')
            with ui.row():
                ui.button('受け入れる',on_click=accept_buyout).props('color=positive')
                ui.button('断る',on_click=reject_buyout).props('color=negative')

    # スポンサー交渉
    if game_state.get('pending_sponsor_negotiation'):
        data=game_state['pending_sponsor_negotiation']; o=data['offer']
        with ui.card().classes('w-full q-mb-sm'):
            ui.label('スポンサー交渉').classes('text-h6')
            ui.label(f'{o["name"]} | 週次{fmt_m(o["weekly_income"])} | 要求:{data["demand"]}').classes('text-body2')
            with ui.row():
                ui.button('契約する',on_click=accept_sponsor).props('color=positive')
                ui.button('断る',on_click=reject_sponsor).props('color=negative')

    # メインダッシュボード
    with ui.card().classes('w-full q-mb-sm'):
        ui.label(f'{t["name"]}').classes('text-h6')
        ui.label(f'{dn} {rank}位 | 評判{t["reputation"]} | ケミストリー{t.get("chemistry",50)}').classes('text-body1')
        if t.get('player_season_goal'): ui.label(f'今季目標: {t["player_season_goal"]}').classes('text-body2 text-bold')
        if t.get('naming_rights'): ui.label(f'🏟 {t["naming_rights"]["company"]}').classes('text-body2 text-blue')
        if t.get('sponsor'): ui.label(f'スポンサー: {t["sponsor"]["name"]} 週{fmt_m(t["sponsor"]["weekly_income"])} 勝利+{fmt_m(t["sponsor"]["win_bonus"])}').classes('text-body2')
        with ui.row():
            for lbl,val in [('監督',game_state['manager_rating']),('理事会',game_state['board_rating']),('ファン',game_state['fan_happiness']),('ロッカー',game_state['locker_room_mood']),('ブランド',game_state['club_brand'])]:
                with ui.column().classes('items-center'):
                    ui.circular_progress(value=val,max=100,size='55px')
                    ui.label(lbl).classes('text-caption')

    # 直近試合
    if game_state.get('last_match'):
        lm=game_state['last_match']
        with ui.card().classes('w-full q-mb-sm'):
            ui.label('直近試合').classes('text-h6')
            ui.label(lm['result']).classes('text-body1 text-bold')
            ui.label(f'観客{lm["attendance"]:,}人 | {fmt_m(lm["revenue"])} | MOM:{lm["mom"]["name"]}').classes('text-body2')
            if lm.get('weather'): ui.label(f'天候: {lm["weather"]}').classes('text-caption')
            for h in lm.get('highlights',[]): ui.label(f'  {h}').classes('text-caption')
            # テキスト実況（後半分）
            evts=game_state.get('live_commentary',[])
            if evts:
                ui.label('試合ハイライト実況:').classes('text-subtitle2')
                for e in [x for x in evts if x.get('t',0)>45][:8]:
                    apos="'"; ui.label(f'{e["t"]}{apos} {e["txt"]}').classes('text-caption')

    # ダービー通算
    if t.get('derby_record'):
        with ui.card().classes('w-full q-mb-sm'):
            ui.label('⚔️ダービー').classes('text-h6')
            for rv,rec in t['derby_record'].items():
                ui.label(f'{rv}: {rec["w"]}勝{rec["d"]}分{rec["l"]}敗').classes('text-body2')

    # 実績
    done=game_state.get('achievements',[])
    if done:
        with ui.card().classes('w-full q-mb-sm'):
            ui.label('🏅実績').classes('text-h6')
            with ui.row():
                for key in done:
                    a=ACHIEVEMENTS.get(key,{})
                    ui.chip(f'{a.get("icon","")}{a.get("name",key)}').classes('text-body2')

    # 監督キャリア歴
    career=game_state.get('manager_career',[])
    if career:
        with ui.card().classes('w-full q-mb-sm'):
            ui.label('👔監督キャリア').classes('text-h6')
            for c in career: ui.label(f'S{c["season"]}: {c["club"]} {c["div"]} {c["rank"]}位').classes('text-body2')

    # クラブ歴史書
    history=get_sel().get('season_history',[]) if get_sel() else []
    if len(history)>=2:
        with ui.card().classes('w-full q-mb-sm'):
            ui.label('📖クラブ歴史書').classes('text-h6')
            for h in history[-5:]: ui.label(f'S{h["season"]}: {h["div"]} {h["rank"]}位 {h["goals"]}G').classes('text-body2')

    # 順位推移
    rh=game_state.get('rank_history',[])
    if rh:
        with ui.card().classes('w-full q-mb-sm'):
            ui.label('📈順位推移').classes('text-h6')
            ui.label('直近10週: '+' → '.join(str(x['rank']) for x in rh[-10:])).classes('text-body2')

    # 移籍要求
    req=[p for p in t['players'] if p.get('transfer_request')]
    if req:
        with ui.card().classes('w-full q-mb-sm'):
            ui.label('⚠️移籍要求').classes('text-h6 text-red')
            for p in req:
                ui.label(f'{p["name"]} OVR{p["overall"]} 不満{p["unhappiness"]}').classes('text-body2')
                ui.button('交渉',on_click=lambda e,pid=p['id']:settle_request(pid)).props('color=warning')

    # トレーニング結果
    tr=game_state.get('training_results',[])
    if tr:
        with ui.card().classes('w-full q-mb-sm'):
            ui.label('🏃トレーニング結果').classes('text-h6')
            for r in tr: ui.label(f'  {r}').classes('text-body2 text-positive')

    # ニュース
    with ui.card().classes('w-full q-mb-sm'):
        ui.label('📰ニュース').classes('text-h6')
        cats=['全て','match','transfer','player','club','cup','injury']
        def set_f(c): game_state['news_filter']=c; refresh_ui()
        with ui.row():
            for c in cats:
                active=game_state.get('news_filter','全て')==c
                ui.button(c,on_click=lambda e,x=c:set_f(x)).props(f'{"color=primary" if active else "flat"}')
        flt=game_state.get('news_filter','全て')
        for n in [x for x in game_state['news'] if flt=='全て' or x.get('cat')==flt][:20]:
            ui.label(f'・{n["text"]}').classes('text-body2')
```

def render_squad():
dashboard_box.clear()
with dashboard_box:
t=get_sel()
if not t: ui.label(‘クラブ未選択’); return

```
    # スターティングイレブン
    with ui.card().classes('w-full q-mb-sm'):
        ui.label('📋スターティングイレブン').classes('text-h6')
        xi_ids=set(t.get('starting_xi',[]))
        ui.label(f'選択中: {len(xi_ids)}/11人 {"✅確定" if len(xi_ids)==11 else ""}').classes('text-body2')
        avail=[p for p in t['players'] if p['injury_weeks']<=0 and p.get('intl_weeks',0)<=0]
        for p in sorted(avail,key=lambda x:(-x['overall'],x['pos'])):
            inxi=p['id'] in xi_ids
            def toggle(e,pid=p['id'],cur=inxi):
                xi=set(t.get('starting_xi',[]));
                if cur: xi.discard(pid)
                elif len(xi)<11: xi.add(pid)
                t['starting_xi']=list(xi); refresh_ui()
            inj='🏥' if p['injury_weeks']>0 else ''
            ui.button(f'{"✓" if inxi else "○"} {p["name"]} {p["pos"]} OVR{p["overall"]} {PLAYER_STATES.get(p.get("state","normal"),PLAYER_STATES["normal"])["label"]}{inj}',on_click=toggle).props(f'{"color=primary" if inxi else "flat"}').classes('w-full q-mb-xs')
        with ui.row():
            ui.button('確定',on_click=lambda: set_starting_xi(t.get('starting_xi',[]))).props('color=positive')
            ui.button('自動選出',on_click=auto_lineup).props('color=secondary')

    # PKシューター・セットプレー担当設定
    with ui.card().classes('w-full q-mb-sm'):
        ui.label('⚽PKシューター / セットプレー担当指定').classes('text-h6')
        pk_id=t.get('pk_taker_id')
        ck_id=t.get('ck_taker_id')
        fk_id=t.get('fk_taker_id')
        pk_p=next((p for p in t['players'] if p['id']==pk_id),None)
        ck_p=next((p for p in t['players'] if p['id']==ck_id),None)
        fk_p=next((p for p in t['players'] if p['id']==fk_id),None)
        if pk_p: ui.label(f'PKシューター: {pk_p["name"]} (SHT:{pk_p["attrs"].get("SHT",50)})').classes('text-body2')
        if ck_p: ui.label(f'CK担当: {ck_p["name"]} (TEC:{ck_p["attrs"].get("TEC",50)})').classes('text-body2')
        if fk_p: ui.label(f'FK担当: {fk_p["name"]} (SHT:{fk_p["attrs"].get("SHT",50)})').classes('text-body2')
        ui.label('PKシューター指定（SHT順）:').classes('text-subtitle2')
        top_shooters=sorted(t['players'],key=lambda p:p['attrs'].get('SHT',50),reverse=True)[:5]
        with ui.row():
            for p in top_shooters:
                ui.button(f'{p["name"]} SHT{p["attrs"].get("SHT",50)}',on_click=lambda e,pid=p['id']:set_pk_taker(pid)).props(f'{"color=accent" if p["id"]==pk_id else "flat"}')
        ui.label('CK担当指定（TEC順）:').classes('text-subtitle2')
        top_tec=sorted(t['players'],key=lambda p:p['attrs'].get('TEC',50),reverse=True)[:5]
        with ui.row():
            for p in top_tec:
                ui.button(f'{p["name"]} TEC{p["attrs"].get("TEC",50)}',on_click=lambda e,pid=p['id']:(t.update({"ck_taker_id":pid}) or add_news(f'CK担当: {next((x["name"] for x in t["players"] if x["id"]==pid),"?")}','club') or refresh_ui())).props(f'{"color=primary" if p["id"]==ck_id else "flat"}')
        ui.label('FK担当指定（SHT順）:').classes('text-subtitle2')
        with ui.row():
            for p in top_shooters:
                ui.button(f'{p["name"]} SHT{p["attrs"].get("SHT",50)}',on_click=lambda e,pid=p['id']:(t.update({"fk_taker_id":pid}) or add_news(f'FK担当: {next((x["name"] for x in t["players"] if x["id"]==pid),"?")}','club') or refresh_ui())).props(f'{"color=primary" if p["id"]==fk_id else "flat"}')

    # 戦術
    with ui.card().classes('w-full q-mb-sm'):
        ui.label('⚙️戦術').classes('text-h6')
        with ui.row():
            for tn in TACTICS: ui.button(tn,on_click=lambda e,x=tn:set_tactic(x)).props(f'{"color=primary" if t.get("tactic")==tn else "flat"}')
        ui.label('フォーメーション:').classes('text-subtitle2')
        with ui.row():
            for fn in FORMATIONS: ui.button(fn,on_click=lambda e,x=fn:set_formation(x)).props(f'{"color=primary" if t.get("formation")==fn else "flat"}')

    # 監督スキル
    with ui.card().classes('w-full q-mb-sm'):
        ui.label(f'🎓監督スキル (exp:{game_state.get("manager_exp",0)} SP:{game_state.get("manager_skill_points",0)})').classes('text-h6')
        with ui.row():
            for sk,data in MANAGER_SKILLS.items():
                learned=sk in game_state.get('manager_skills',[])
                req_ok=game_state.get('manager_exp',0)>=data['req_exp']
                col='positive' if learned else('primary' if req_ok else 'grey')
                ui.button(f'{"✅" if learned else ""}{sk} {data["desc"]}',on_click=lambda e,s=sk:learn_skill(s)).props(f'color={col}')

    # トップチーム
    with ui.card().classes('w-full q-mb-sm'):
        ui.label(f'トップチーム ({len(t["players"])}名)').classes('text-h6')
    for p in sorted(t['players'],key=lambda x:(x['pos'],-x['overall'])):
        inj=f'🏥{p["injury_severity"]}({p["injury_weeks"]}週)' if p['injury_weeks']>0 else ''
        intl=f'🌍({p.get("intl_weeks",0)}週)' if p.get('intl_weeks',0)>0 else ''
        req='⚠️' if p.get('transfer_request') else ''
        cap='©️' if p['id']==t.get('captain_id') else ''
        xi_mark='✓' if p['id'] in set(t.get('starting_xi',[])) else ''
        retire='💐' if p.get('retiring') else ''
        state=PLAYER_STATES.get(p.get('state','normal'),PLAYER_STATES['normal'])['label']
        agent='🤝' if p.get('has_agent') else ''
        local='🏠' if p.get('is_local') else ''
        convert=f'🔄→{p.get("target_pos","")}({p.get("convert_weeks",0)}週)' if p.get('convert_weeks',0)>0 else ''
        with ui.card().classes('w-full q-mb-xs'):
            ui.label(f'{xi_mark}{cap}{p["name"]} | {p["pos"]} OVR{p["overall"]} | {state} {inj}{intl}{req}{retire}{agent}{local}{convert}').classes('text-body1')
            ui.label(f'{p["age"]}歳 | 年俸{fmt_m(p["wage"])} | 契約{p["contract_years"]}年 | 不満{p.get("unhappiness",0)} | morale{int(p.get("morale",50))}').classes('text-body2')
            ui.label(f'出場{p["stats"]["apps"]} G{p["stats"]["goals"]} A{p["stats"]["assists"]} MOM{p["stats"]["mom"]} 🟨{p["stats"].get("yellow_cards",0)} 🟥{p["stats"].get("red_cards",0)}').classes('text-caption')
            attr_str=' '.join(f'{ATTR_ICONS.get(k,k)}{v}' for k,v in p['attrs'].items())
            ui.label(attr_str).classes('text-caption')
            with ui.row():
                ui.button('延長',on_click=lambda e,pid=p['id']:renew_contract(pid)).props('color=positive')
                ui.button('詳細',on_click=lambda e,pid=p['id']:show_player(pid))
                ui.button('©️C',on_click=lambda e,pid=p['id']:set_captain(pid)).props('flat')
                ui.button('🔄放出',on_click=lambda e,pid=p['id']:send_on_loan(pid)).props('flat color=warning')
            # トレーニング・役割設定
            focus=p.get('training_focus','')
            with ui.row():
                ui.label('集中:').classes('text-caption')
                for attr in list(p['attrs'].keys())[:4]:
                    ui.button(f'{ATTR_ICONS.get(attr,attr)}',on_click=lambda e,pid=p['id'],a=attr:set_training_focus(pid,a)).props(f'flat {"color=primary" if focus==attr else ""}')
                ui.button('役割:'+p.get('role_wish','どちらでも'),on_click=lambda e,pid=p['id'],rw=p.get('role_wish','どちらでも'):set_role_wish(pid,'主力のみ' if rw=='どちらでも' else 'どちらでも')).props('flat')
            # コンバート
            with ui.row():
                ui.label('コンバート→').classes('text-caption')
                for pos in [pp for pp in POSITIONS if pp!=p['pos']]:
                    ui.button(pos,on_click=lambda e,pid=p['id'],tp=pos:convert_position(pid,tp)).props('flat')

    # レンタル等
    lo=loaned_out()
    if lo:
        with ui.card().classes('w-full q-mb-sm'):
            ui.label('📤レンタル放出中').classes('text-h6')
            for p,dest in lo:
                ui.label(f'{p["name"]}→{dest} 残{p["loan_weeks"]}週').classes('text-body2')
                ui.button('召還',on_click=lambda e,pid=p['id']:recall_loan(pid)).props('color=warning')
    if t.get('loan_in'):
        with ui.card().classes('w-full q-mb-sm'):
            ui.label('📥レンタル借用中').classes('text-h6')
            for p in t['loan_in']:
                ui.label(f'{p["name"]}({p.get("loan_origin","?")}) {p["pos"]} OVR{p["overall"]} 残{p["loan_weeks"]}週').classes('text-body2')
    # ユース
    qps=[player_by_id(pid) for pid in game_state.get('youth_decision_queue',[]) if player_by_id(pid)]
    if qps:
        with ui.card().classes('w-full q-mb-sm'):
            ui.label('18歳到達ユース').classes('text-h6')
            for p in qps:
                ui.label(f'{p["name"]} {p["age"]}歳 {p["pos"]} OVR{p["overall"]} POT{p["potential"]} {youth_text(p)}').classes('text-body2')
                with ui.row():
                    ui.button('昇格',on_click=lambda e,pid=p['id']:promote_youth(pid)).props('color=positive')
                    ui.button('残留',on_click=lambda e,pid=p['id']:retain_youth(pid)).props('color=warning')
                    ui.button('放出',on_click=lambda e,pid=p['id']:release_youth(pid)).props('color=negative')
    with ui.card().classes('w-full q-mb-sm'):
        ui.label('ユースアカデミー').classes('text-h6')
        with ui.row():
            for pol in YOUTH_POLICIES: ui.button(pol,on_click=lambda e,p=pol:set_youth_policy(p)).props('flat')
        qset=set(game_state.get('youth_decision_queue',[]))
        for p in sorted([x for x in t['youth'] if x['id'] not in qset],key=lambda x:(-x['potential'],x['age'])):
            tag='🌟' if p.get('is_wonderkid') else ''
            ui.label(f'{tag}{p["name"]} {p["age"]}歳 {p["pos"]} OVR{p["overall"]} POT{p["potential"]} {p.get("growth_type","標準")} {youth_text(p)}').classes('text-body2')
```

def render_matches():
dashboard_box.clear()
with dashboard_box:
t=get_sel()
if not t: ui.label(‘クラブ未選択’); return
dn=div_of(t[‘name’])
with ui.card().classes(‘w-full q-mb-sm’):
ui.label(‘試合進行’).classes(‘text-h6’)
ui.label(f’{dn} | 第{game_state[“week”]}節/{SEASON_WEEKS}節 | 天候:{get_weather()}’).classes(‘text-body2’)
if game_state.get(‘preseason_phase’) and not t.get(‘preseason_done’):
ui.button(‘プレシーズン実施’,on_click=run_preseason).props(‘color=warning’)
else:
with ui.row():
ui.button(‘次の週へ進む’,on_click=play_next_week).props(‘color=primary’)
ui.button(‘5週一括進行’,on_click=lambda: bulk_advance(5)).props(‘color=secondary’)
ui.button(‘10週一括進行’,on_click=lambda: bulk_advance(10)).props(‘flat’)
cup=game_state.get(‘domestic_cup’)
if cup and not cup.get(‘winner’):
in_cup=any(x[‘name’]==t[‘name’] for x in cup[‘teams’])
ui.label(f’🏆国内カップ R{cup[“round”]} / {“出場中” if in_cup else “敗退済み”}’).classes(‘text-body2’)
with ui.card().classes(‘w-full q-mb-sm’):
ui.label(f’第{game_state[“week”]}節カード’).classes(‘text-h6’)
for hn,an in get_week_pairs(dn,game_state[‘week’]):
ht2=find_team(hn); at2=find_team(an)
derby=‘🔥’ if at2 and hn in at2.get(‘rivals’,[]) else ‘’
ui.label(f’{derby}{hn} vs {an}’).classes(‘text-red’ if derby else ‘text-body2’)
for dname in [‘D1’,‘D2’,‘D3’]:
with ui.card().classes(‘w-full q-mb-sm’):
ui.label(f’順位表 [{dname}]’).classes(‘text-h6’)
for i,tm in enumerate(sorted_table(dname),1):
s=tm[‘season_stats’]; mark=‘⭐ ’ if tm[‘name’]==t[‘name’] else ‘’
ui.label(f’{i}. {mark}{tm[“name”]} | 勝点{s[“pts”]} | {s[“w”]}-{s[“d”]}-{s[“l”]} | GD{s[“gd”]} | 評判{tm[“reputation”]}’).classes(‘text-body2’)

def render_transfers():
dashboard_box.clear()
with dashboard_box:
t=get_sel()
if not t: ui.label(‘クラブ未選択’); return
if not in_transfer_window():
with ui.card().classes(‘w-full q-mb-sm’):
ui.label(‘🔒移籍ウィンドウ外’).classes(‘text-h6’)
ui.label(‘完全移籍は夏(週1-6)と冬(週19-22)のみ可能。現在はレンタルのみ。’).classes(‘text-body2’)
with ui.card().classes(‘w-full q-mb-sm’):
ui.label(‘🔍国内スカウト市場’).classes(‘text-h6’)
with ui.row():
ui.button(‘候補更新’,on_click=create_scout_pool)
ui.button(‘ユース引き抜き’,on_click=poach_youth).props(‘color=warning’)
if ‘scout_pool’ not in game_state: create_scout_pool()
for p in game_state[‘scout_pool’]:
# スカウト不確実性: 推定値を表示
est=f’推定OVR {p.get(“scout_ovr_min”,p[“overall”])}〜{p.get(“scout_ovr_max”,p[“overall”])}’
grade=p.get(‘scout_grade’,‘C’)
ui.label(f’{p[“name”]} {p[“pos”]} {est} (評価:{grade}) {fmt_m(p[“value”])} {“🤝” if p.get(“has_agent”) else “”}’).classes(‘text-body2’)
ui.button(‘獲得’,on_click=lambda e,pid=p[‘id’]:sign_scout(pid)).props(‘color=positive’)
# 海外スカウト
with ui.card().classes(‘w-full q-mb-sm’):
ui.label(‘🌍海外スカウト派遣’).classes(‘text-h6’)
os_data=game_state.get(‘overseas_scout’)
if os_data: ui.label(f’{os_data[“country”]}に派遣中（残{os_data[“weeks_left”]}週）’).classes(‘text-body2’)
else:
with ui.row():
for country in COUNTRIES:
ui.button(country,on_click=lambda e,c=country:dispatch_overseas_scout(c)).props(‘flat’)
ui.label(‘費用: $50,000 / 4週後に帰還’).classes(‘text-caption’)
# 海外スカウット候補
op=game_state.get(‘overseas_pool’,[])
if op:
ui.label(‘海外スカウット候補:’).classes(‘text-subtitle2’)
for p in op:
est=f’推定OVR {p.get(“scout_ovr_min”,p[“overall”])}〜{p.get(“scout_ovr_max”,p[“overall”])}’
ui.label(f’{p[“name”]} {p[“nationality”]} {p[“pos”]} {est} {fmt_m(p[“value”])}’).classes(‘text-body2’)
ui.button(‘獲得’,on_click=lambda e,pid=p[‘id’]:sign_overseas_player(pid)).props(‘color=positive’)
# 国内オファー
with ui.card().classes(‘w-full q-mb-sm’):
ui.label(‘🏠国内移籍オファー’).classes(‘text-h6’)
if not game_state[‘transfer_offers’]: ui.label(‘なし’).classes(‘text-body2’)
else:
for o in game_state[‘transfer_offers’]:
p2=player_by_id(o[‘player_id’])
agent_note=f’🤝手数料{p2[“agent_fee_pct”]}%’ if p2 and p2.get(‘has_agent’) else ‘’
ui.label(f’{o[“player_name”]} ← {o[“buyer”]} / {fmt_m(o.get(“counter_fee”) or o[“fee”])} {agent_note}’).classes(‘text-body2’)
with ui.row():
ui.button(‘承諾’,on_click=lambda e,pid=o[‘player_id’]:accept_transfer(pid)).props(‘color=positive’)
ui.button(‘カウンター×1.3’,on_click=lambda e,pid=o[‘player_id’]:counter_offer(pid)).props(‘color=warning’)
ui.button(‘買戻条項付き’,on_click=lambda e,pid=o[‘player_id’]:accept_transfer(pid,True)).props(‘color=accent’)
ui.button(‘拒否’,on_click=lambda e,pid=o[‘player_id’]:reject_transfer(pid)).props(‘color=negative’)
# 海外オファー
with ui.card().classes(‘w-full q-mb-sm’):
ui.label(‘✈️海外オファー’).classes(‘text-h6’)
if not game_state[‘foreign_offers’]: ui.label(‘なし’).classes(‘text-body2’)
else:
for o in game_state[‘foreign_offers’]:
p2=player_by_id(o[‘player_id’])
if p2:
ui.label(f’{p2[“name”]} ← {o[“club”]} / {fmt_m(o[“fee”])}’).classes(‘text-body2’)
with ui.row():
ui.button(‘承諾’,on_click=lambda e,pid=o[‘player_id’]:accept_foreign(pid)).props(‘color=positive’)
ui.button(‘拒否’,on_click=lambda e,pid=o[‘player_id’]:reject_foreign(pid)).props(‘color=negative’)
# レンタル
with ui.card().classes(‘w-full q-mb-sm’):
ui.label(‘📥レンタル借用オファー’).classes(‘text-h6’)
if not game_state.get(‘loan_offers’): ui.label(‘なし’).classes(‘text-body2’)
else:
for o in game_state[‘loan_offers’]:
ui.label(f’{o[“player_name”]}({o[“from_club”]}) {o[“player_pos”]} OVR{o[“player_ovr”]} 評価:{o.get(“scout_grade”,“C”)} {o[“weeks”]}週 {fmt_m(o[“loan_fee”])}’).classes(‘text-body2’)
with ui.row():
ui.button(‘借りる’,on_click=lambda e,pid=o[‘player_id’]:accept_loan_in(pid)).props(‘color=positive’)
ui.button(‘断る’,on_click=lambda e,pid=o[‘player_id’]:reject_loan_in(pid)).props(‘color=negative’)
with ui.card().classes(‘w-full q-mb-sm’):
ui.label(‘📤レンタル放出’).classes(‘text-h6’)
for p in sorted([x for x in t[‘players’] if not x.get(‘loan_club’)],key=lambda x:x[‘overall’]):
ui.label(f’{p[“name”]} {p[“pos”]} OVR{p[“overall”]}’).classes(‘text-body2’)
ui.button(‘放出’,on_click=lambda e,pid=p[‘id’]:send_on_loan(pid)).props(‘flat color=warning’)
# 選手比較
if game_state.get(‘scout_pool’) and t[‘players’]:
with ui.card().classes(‘w-full q-mb-sm’):
ui.label(‘⚖️選手比較’).classes(‘text-h6’)
best=max(t[‘players’],key=lambda p:p[‘overall’]); cand=game_state[‘scout_pool’][0]
with ui.row():
with ui.column():
ui.label(f’自: {best[“name”]} OVR{best[“overall”]}’).classes(‘text-subtitle2’)
for k,v in best[‘attrs’].items(): ui.label(f’{ATTR_ICONS.get(k,k)}{k}: {v}’).classes(‘text-body2’)
with ui.column():
ui.label(f’候補: {cand[“name”]} OVR{cand[“overall”]}’).classes(‘text-subtitle2’)
for k,v in cand[‘attrs’].items():
diff=v-best[‘attrs’].get(k,0); col=‘text-positive’ if diff>0 else(‘text-negative’ if diff<0 else ‘’)
ui.label(f’{ATTR_ICONS.get(k,k)}{k}: {v} ({”+”+str(diff) if diff>=0 else str(diff)})’).classes(f’text-body2 {col}’)

def render_management():
dashboard_box.clear()
with dashboard_box:
t=get_sel()
if not t: ui.label(‘クラブ未選択’); return
with ui.card().classes(‘w-full q-mb-sm’):
ui.label(‘🏗️施設管理’).classes(‘text-h6’)
fac_names={‘youth’:‘ユース’,‘training’:‘トレーニング’,‘medical’:‘メディカル’,‘scouting’:‘スカウト’,‘stadium’:‘スタジアム’}
for ft in FACILITY_TYPES:
lv=game_state[‘facilities’][ft]; nm=fac_names[ft]
ui.label(f’{nm}: Lv{lv}/5 (強化費:{fmt_m(150000*lv)})’).classes(‘text-body2’)
if ft==‘stadium’: ui.button(‘スタジアム拡張’,on_click=expand_stadium).classes(‘q-mb-xs’)
elif ft==‘youth’: ui.button(‘ユース強化’,on_click=upgrade_youth_fac).classes(‘q-mb-xs’)
else: ui.button(f’{nm}強化’,on_click=lambda e,x=ft:upgrade_facility(x)).classes(‘q-mb-xs’)
vip=t.get(‘vip_level’,0)
ui.label(f’VIPエリア: Lv{vip}/3’).classes(‘text-body2’)
if vip<3: ui.button(f’VIP拡充({fmt_m(300000*(vip+1))})’,on_click=upgrade_vip).classes(‘q-mb-xs’)
with ui.card().classes(‘w-full q-mb-sm’):
ui.label(‘👥スタッフ’).classes(‘text-h6’)
ui.button(‘スタッフ雇用 ($60,000)’,on_click=hire_staff).props(‘color=primary’)
effs={‘ヘッドコーチ’:‘強度+’,‘スカウト’:‘スカウット質+’,‘フィジオ’:‘怪我率-’,‘アシスタント’:‘成長+’}
for s in game_state[‘staff’]:
ui.label(f’{s[“type”]} {effs.get(s[“type”],””)} skill{s[“skill”]} 給与{fmt_m(s[“salary”])}’).classes(‘text-body2’)
# 財務
with ui.card().classes(‘w-full q-mb-sm’):
ui.label(‘💰財務サマリー’).classes(‘text-h6’)
f=game_state[‘season_finance’]
items=[(‘スポンサー’,‘sponsor’),(‘観客’,‘matchday’),(‘放映権’,‘broadcast’),(‘グッズ/肖像権’,‘merch’),(‘ネーミング’,‘naming_rights’),(‘プレシーズン’,‘preseason’),(‘移籍収入’,‘transfers_out’),(‘賞金’,‘prize’),(‘移籍支出’,‘transfers_in’),(‘給与’,‘wages’),(‘施設’,‘facility’),(‘スタッフ’,‘staff’),(‘ローン利息’,‘loan_interest’),(‘保険料’,‘insurance’)]
for lbl,k in items:
v=f.get(k,0); col=‘text-positive’ if v>0 else(‘text-negative’ if v<0 else ‘’)
ui.label(f’{lbl}: {fmt_m(v)}’).classes(f’text-body2 {col}’)
dn=div_of(t[‘name’]); cap=SALARY_CAP.get(dn,999999)
total_wage=sum(p[‘wage’] for p in t[‘players’])
ui.label(f’総給与: {fmt_m(total_wage)} / 上限: {fmt_m(cap)}’).classes(‘text-body2’+(’ text-red’ if total_wage>cap else ’ text-positive’))
# 銀行ローン・保険
with ui.card().classes(‘w-full q-mb-sm’):
ui.label(‘🏦銀行ローン’).classes(‘text-h6’)
loans=game_state.get(‘bank_loans’,[])
if loans:
for l in loans: ui.label(f’残{l[“remaining_weeks”]}週 金利{int(l[“interest_rate”]*100)}%’).classes(‘text-body2’)
else: ui.label(‘ローンなし’).classes(‘text-body2’)
with ui.row():
for amt in [200000,500000,1000000]:
ui.button(f’{fmt_m(amt)}借りる’,on_click=lambda e,a=amt:take_bank_loan(a)).props(‘flat’)
with ui.card().classes(‘w-full q-mb-sm’):
ui.label(‘🏥選手保険’).classes(‘text-h6’)
ins=game_state.get(‘injury_insurance_active’,False)
ui.label(f’状態: {“契約中（週{fmt_m(8000)}）” if ins else “未契約”}’).classes(‘text-body2’)
if not ins: ui.button(‘保険契約（週$8,000）’,on_click=activate_insurance).props(‘color=positive’)
# 予算配分
with ui.card().classes(‘w-full q-mb-sm’):
ui.label(‘💹予算配分’).classes(‘text-h6’)
ui.label(f’移籍:{fmt_m(t.get(“budget_transfer”,0))} 施設:{fmt_m(t.get(“budget_facility”,0))} スタッフ:{fmt_m(t.get(“budget_staff”,0))}’).classes(‘text-body2’)
with ui.row():
ui.button(‘攻撃的(移籍60%)’,on_click=lambda: set_budget_allocation(60,25,15)).props(‘flat’)
ui.button(‘バランス(各33%)’,on_click=lambda: set_budget_allocation(33,34,33)).props(‘flat’)
ui.button(‘育成重視(施設50%)’,on_click=lambda: set_budget_allocation(25,50,25)).props(‘flat’)
# 国際大会
with ui.card().classes(‘w-full q-mb-sm’):
ui.label(‘🌍国際大会’).classes(‘text-h6’)
cup=game_state.get(‘international_cup’)
if not cup: ui.label(‘未開催’).classes(‘text-body2’)
else:
ui.label(f’R{cup[“round”]} 残{len(cup[“teams”])}クラブ’).classes(‘text-body2’)
ui.button(‘国際大会を進める’,on_click=play_intl_round)
for tm in cup[‘teams’]:
mark=‘⭐’ if tm[‘name’]==t[‘name’] else ‘’
ui.label(f’{mark}{tm[“name”]}’).classes(‘text-body2’)
# セーブ
with ui.card().classes(‘w-full q-mb-sm’):
ui.label(‘💾セーブ/ロード’).classes(‘text-h6’)
ui.button(‘セーブ’,on_click=save_game).props(‘color=primary’)
ui.upload(label=‘JSONロード’,on_upload=lambda e:load_game(e.content.read()),auto_upload=True).props(‘accept=”.json”’)

def show_player(pid):
p=player_by_id(pid)
if not p: return
with ui.dialog() as dlg, ui.card():
ui.label(f’{p[“name”]}’).classes(‘text-h6’)
ui.label(f’{p[“club”]} / {p[“nationality”]} {“🏠地元” if p.get(“is_local”) else “”}’).classes(‘text-body2’)
ui.label(f’{p[“age”]}歳 | {p[“pos”]} | OVR{p[“overall”]} | POT{p[“potential”]}’).classes(‘text-body2’)
ui.label(f’スタイル:{p[“playstyle”]} | 性格:{p[“personality”]} | 特性:{p.get(“trait”,“なし”)}’).classes(‘text-body2’)
ui.label(f’成長:{p.get(“growth_type”,“標準”)} | 状態:{PLAYER_STATES.get(p.get(“state”,“normal”),PLAYER_STATES[“normal”])[“label”]}’).classes(‘text-body2’)
ui.label(f’契約{p[“contract_years”]}年 | 年俸{fmt_m(p[“wage”])} | 不満{p[“unhappiness”]} | morale{int(p.get(“morale”,50))}’).classes(‘text-body2’)
sev=p.get(‘injury_severity’,‘なし’)
ui.label(f’負傷:{sev}({p[“injury_weeks”]}週)’).classes(‘text-body2’+(’ text-red’ if sev!=‘なし’ else ‘’))
if p.get(‘intl_weeks’,0)>0: ui.label(f’代表召集中 {p[“intl_weeks”]}週 {“→帰還後成長あり” if p.get(“intl_boost_pending”) else “”}’).classes(‘text-blue’)
if p.get(‘has_agent’): ui.label(f’エージェントあり（手数料{p[“agent_fee_pct”]}%）’).classes(‘text-body2’)
if p.get(‘retiring’): ui.label(‘💐今季引退予定’).classes(‘text-red’)
if p.get(‘convert_weeks’,0)>0: ui.label(f’🔄コンバート中→{p.get(“target_pos”,””)} ({p[“convert_weeks”]}週)’).classes(‘text-body2’)
ui.label(f’役割希望: {p.get(“role_wish”,“どちらでも”)}’).classes(‘text-body2’)
with ui.row():
for k,v in p[‘attrs’].items():
with ui.column().classes(‘items-center’):
ui.circular_progress(value=v,max=99,size=‘48px’)
ui.label(f’{ATTR_ICONS.get(k,k)}{k}’).classes(‘text-caption’)
st=p[‘stats’]
ui.label(f’出場{st[“apps”]} G{st[“goals”]} A{st[“assists”]} MOM{st[“mom”]} CS{st.get(“clean_sheets”,0)} 🟨{st.get(“yellow_cards”,0)} 🟥{st.get(“red_cards”,0)}’).classes(‘text-body2’)
if p.get(‘buyback_fee’): ui.label(f’買戻し:{fmt_m(p[“buyback_fee”])}’).classes(‘text-blue’)
ui.button(‘閉じる’,on_click=dlg.close)
dlg.open()

def render_current_tab():
{‘dashboard’:render_dashboard,‘squad’:render_squad,‘matches’:render_matches,‘transfers’:render_transfers,‘management’:render_management}.get(nav_state[‘tab’],render_dashboard)()

def refresh_ui(): render_status(); render_current_tab()
def switch_tab(tab): nav_state[‘tab’]=tab; refresh_ui()

# =========================================================

# 初期化・起動

# =========================================================

game_state=build_world(‘England’); init_stats()
for d in game_state[‘divisions’]:
for t in game_state[‘divisions’][d]:
t[‘sponsor’]=_gen_sponsor(t[‘country’],d)

ui.add_head_html(’’’
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Club Strive">
<meta name="theme-color" content="#1e293b">

<link rel="manifest" href="/static/manifest.json">
<style>
body{background:#0f172a;color:#e5e7eb;-webkit-tap-highlight-color:transparent;}
.q-card{background:#111827;color:#e5e7eb;border-radius:14px}
.q-header,.q-footer{background:#1e293b!important}
/* スマホ用タッチ操作改善 */
.q-btn{min-height:44px;min-width:44px;}
/* スクロール改善 */
.q-page-container{overflow-y:auto;-webkit-overflow-scrolling:touch;}
</style>
<script>
// Service Worker登録
if('serviceWorker' in navigator){
  window.addEventListener('load', function(){
    navigator.serviceWorker.register('/static/sw.js')
      .then(reg => console.log('SW registered'))
      .catch(err => console.log('SW error:', err));
  });
}
// PWAインストール促進
let deferredPrompt;
window.addEventListener('beforeinstallprompt', e => {
  e.preventDefault();
  deferredPrompt = e;
  // インストールバナーを表示する場合はここで処理
});
</script>
''')

with ui.header().classes(‘items-center justify-between’):
ui.label(APP_TITLE).classes(‘text-h5’)
with ui.row():
for c in COUNTRIES:
ui.button(c,on_click=lambda e,cc=c:new_world(cc)).props(‘flat color=white’)

with ui.row().classes(‘w-full’):
status_box=ui.column().classes(‘w-1/4’)
dashboard_box=ui.column().classes(‘w-3/4’)

with ui.footer().classes(‘justify-around’):
for lbl,tab in [(‘ダッシュボード’,‘dashboard’),(‘チーム’,‘squad’),(‘試合’,‘matches’),(‘移籍’,‘transfers’),(‘経営’,‘management’)]:
ui.button(lbl,on_click=lambda e,t=tab:switch_tab(t)).props(‘flat color=white’)

refresh_ui()
from nicegui import app as nicegui_app
import os

# staticフォルダを公開（manifest.json, sw.js用）

static_dir = os.path.join(os.path.dirname(**file**), ‘static’)
if os.path.exists(static_dir):
nicegui_app.add_static_files(’/static’, static_dir)

ui.run(
title=APP_TITLE,
host=‘0.0.0.0’,
port=int(os.environ.get(‘PORT’, 8080)),
favicon=‘⚽’,
dark=True,
)
