import pandas as pd
import os
import bs4
import math
import datetime
import re
import numpy as np
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import *
from sqlalchemy.orm.exc import NoResultFound
import multiprocessing as multi
from multiprocessing import Pool

engine = create_engine('mysql://keiba@localhost/keiba?charset=utf8', echo=False)


Base = declarative_base()
 
# 次にベースモデルを継承してモデルクラスを定義します
class Race(Base):
    __tablename__ = 'race'
 
    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    title = Column(CHAR(30))
    weather = Column(CHAR(10))
    field_state = Column(CHAR(10))
    field = Column(CHAR(8))
    direction = Column(CHAR(4))
    num_horse = Column(Integer)
    length = Column(Integer)
    place = Column(Integer)
    day = Column(Integer)
    cycle = Column(Integer)
    const_age = Column(Boolean)
    const_sex = Column(Boolean)
    const_impose = Column(Boolean)
    notice = Column(CHAR(40))
    round = Column(Integer)
    race_class = Column(CHAR(10))
    obstacle = Column(Boolean)
    handicap = Column(Boolean)
    baba_index = Column(Integer)

    single_odds = Column(Integer)
    multi_odds1 = Column(Integer)
    multi_odds2 = Column(Integer)
    multi_odds3 = Column(Integer)
    wakuren_odds = Column(Integer)
    umaren_odds = Column(Integer)
    wide_odds1 = Column(Integer)
    wide_odds2 = Column(Integer)
    wide_odds3 = Column(Integer)
    umatan_odds = Column(Integer)
    renpuku_odds = Column(Integer)
    rentan_odds = Column(Integer)

    def __repr__(self):
        return "<Race(id='%s', title='%s', date='%s', weather='%s', field_state='%s', field='%s', direction='%s', num_horse='%s', length='%s', place='%s', day='%s', cycle='%s', const_age='%s', const_sex='%s', const_impose='%s', notice='%s', round='%s', race_class='%s', obstacle='%s')>" % (self.id, self.title, self.date,self.weather,self.field_state,self.field,self.direction,self.num_horse,self.length, self.place,self.day, self.cycle, self.const_age,self.const_sex,self.const_impose,self.notice,self.round,self.race_class,self.obstacle)
class Result(Base):
    __tablename__ = 'result'

    id = Column(Integer, primary_key=True)
    name = Column(CHAR(25))
    age = Column(Integer)
    sex = Column(CHAR(4))
    impost = Column(Integer)
    jockey = Column(CHAR(25))
    time = Column(Integer)
    diff = Column(CHAR(15))
    passrank = Column(CHAR(20))
    agari = Column(Float)
    single_return = Column(Float)
    popularity = Column(Integer)
    weight = Column(Integer)
    weight_diff = Column(Integer)
    trainer = Column(CHAR(25))
    owner = Column(CHAR(50))
    rank = Column(Integer)
    race_id = Column(Integer)
    position = Column(Integer)
    time_index = Column(Integer)
    bef = Column(Integer)

    def __repr__(self):
        return "<Result(id='%s', name='%s', age='%s', sex='%s', impost='%s', jockey='%s', time='%s', diff='%s', passrank='%s', agari='%s', single_return='%s', popularity='%s', weight='%s', trainer='%s', owner='%s', rank='%s', race_id='%s', position='%s')>" % (self.id, self.name,self.age, self.sex,self.impost,self.jockey,self.time, self.diff,self.passrank,self.agari,self.single_return,self.popularity,self.weight,self.trainer,self.owner,self.rank,self.race_id,self.position)

session = scoped_session(
        sessionmaker(
            autocommit = False,
            autoflush = False,
            bind = engine
        )
)

st = "0"
results = []
races = []

def isnan(x):
    if type(x) == float and math.isnan(x):
        return True
    else:
        return False

def parse(arg):
    [fname, cou] = arg
    print(fname)
    with open("pages/"+fname) as f:
        race = Race()
        race.id = cou

        html = pd.read_html(f)

        tb = html[0]
        if "着順" not in tb.columns:
            return
        # print(tb.columns)
        for index,row in tb.iterrows():
            if row["着順"] in ["中", "取", "除"]:
                continue
            result = Result()
            result.name = row["馬名"]
            result.age = int(re.findall(r'\d+',row["性齢"])[0])
            result.rank = index + 1
            result.sex = re.sub(r'\d+','',row["性齢"])
            result.impost = int(row["斤量"])
            result.jockey = row["騎手"]
            result.time = int(row["タイム"].split(":")[0])*600+int(row["タイム"].split(":")[1].split(".")[0])*10+int(row["タイム"].split(":")[1].split(".")[1])
            result.diff = row["着差"]
            if type(result.diff)==float and math.isnan(result.diff):
                result.diff = "0"
                
            result.passrank = row["通過"]
            if not isnan(float(row["上り"])):
                result.agari = float(row["上り"])
            if not isnan(float(row["単勝"])):
                result.single_return = float(row["単勝"])
            result.popularity = int(row["人気"])
            if row["馬体重"] != "計不":
                result.weight = int(re.findall(r'\d+',row["馬体重"])[0])
                result.weight_diff = int(re.findall(r'([+-]\d+|0)',row["馬体重"])[0])
            result.trainer = row["調教師"]
            result.owner = row["馬主"]
            result.race_id = race.id
            result.position = int(row["枠番"])
            
            if "ﾀｲﾑ指数" in row.index:
                if not isnan(row["ﾀｲﾑ指数"]):
                    result.time_index = int(row["ﾀｲﾑ指数"])
            if "タイム指数" in row.index:
                if not isnan(row["タイム指数"]):
                    result.time_index = int(row["タイム指数"])
            results.append(result)
            # print(result)
            
        f.seek(0)

        soup = bs4.BeautifulSoup(f, "html.parser")
        data_intro = soup.select_one(".data_intro")
        cond = data_intro.find("dl").find("dd").find("p").find("diary_snap_cut").find("span").text.split("\xa0/\xa0")
        misc = data_intro.select_one(".smalltxt").text.split()
        
        race.date = datetime.datetime.strptime(misc[0], "%Y年%m月%d日")
        tm = re.findall(r'発走 : \d+:\d+', cond[3])[0][5:]
        race.date = race.date.replace(hour = int(tm[:tm.find(":")]), minute = int(tm[tm.find(":")+1:]))

        race.weather = re.findall(r'天候 : .*',cond[1])[0][5:]
        race.field_state = re.findall(r' : .*', cond[2])[0][3:].split()[0]
        # print(cond[0])
        race.field = str(cond[0][0])
        if "左" in cond[0]:
            race.direction = "左"
        if "右" in cond[0]:
            race.direction = "右"
            
        race.num_horse = len(tb)
        race.length = int(re.findall(r'\d+m', cond[0])[0][:-1])
        race.place = int(fname[4:6])
        race.cycle = int(fname[6:8])
        race.day = int(fname[8:10])
        race.round = int(fname[10:12])
        race.const_age = "馬齢" in misc[3]
        race.const_sex = "牝" in misc[3] or "牡" in misc[3] or "セ" in misc[3]
        race.const_impose = "定量" in misc[3]
        race.notice = misc[3]
        
        race.race_class = re.findall(r'(新馬|未勝利|\d+万下|\d+勝クラス|オープン)', misc[2])[0]
        race.title = data_intro.find("h1").text
        race.obstacle = "障害" in misc[2]
        race.handicap = "ハンデ" in misc[2]

        f.seek(0)
        html = pd.read_html(f.read().replace("<br />", ";").replace(",", ""))
        baba = html[3]
        if len(baba.iloc[:,1][baba.iloc[:,0]=="馬場指数"]) > 0:
            race.baba_index = int(re.findall(r'(-\d+|0|\d+)',baba[1][baba[0]=="馬場指数"].tolist()[0])[0])

        odds1 = html[1]
        if len(odds1[2][odds1[0]=="単勝"]) > 0:
            race.single_odds = int(str(odds1[2][odds1[0]=="単勝"].iat[0]).split(';')[0])
        if len(odds1[2][odds1[0]=="複勝"]) > 0:
            race.multi_odds1 = int(str(odds1[2][odds1[0]=="複勝"].iat[0]).split(';')[0])
            race.multi_odds2 = int(str(odds1[2][odds1[0]=="複勝"].iat[0]).split(';')[1])
            if len(str(odds1[2][odds1[0]=="複勝"].iat[0]).split(';')) > 2:
                race.multi_odds3 = int(str(odds1[2][odds1[0]=="複勝"].iat[0]).split(';')[2])
        if len(odds1[2][odds1[0]=="枠連"]) > 0:
            race.wakuren_odds = int(str(odds1[2][odds1[0]=="枠連"].iat[0]).split(';')[0])
        if len(odds1[2][odds1[0]=="馬連"]) > 0:
            race.umaren_odds = int(str(odds1[2][odds1[0]=="馬連"].iat[0]).split(';')[0])

        odds2 = html[2]
        if len(odds2[2][odds2[0]=="ワイド"]) > 0:
            race.wide_odds1 = int(str(odds2[2][odds2[0]=="ワイド"].iat[0]).split(';')[0])
            race.wide_odds2 = int(str(odds2[2][odds2[0]=="ワイド"].iat[0]).split(';')[1])
            race.wide_odds3 = int(str(odds2[2][odds2[0]=="ワイド"].iat[0]).split(';')[2])
        if len(odds2[2][odds2[0]=="馬単"]) > 0:
            race.umatan_odds = int(str(odds2[2][odds2[0]=="馬単"].iat[0]).split(';')[0])
        if len(odds2[2][odds2[0]=="三連複"]) > 0:
            race.renpuku_odds = int(str(odds2[2][odds2[0]=="三連複"].iat[0]).split(';')[0])
        if len(odds2[2][odds2[0]=="三連単"]) > 0:
            race.rentan_odds = int(str(odds2[2][odds2[0]=="三連単"].iat[0]).split(';')[0])

        r = data_intro.find("dl").find("dt").text.replace("\n","")
        
        # print(race)
        races.append(race)
    #     session.add(race)
    # session.add_all(results)
    # session.commit()

Base.metadata.create_all(bind=engine)
# if st == '0':
#     session.execute("truncate race")
#     session.execute("truncate result")
#     session.commit()


year = input()
cou = 1
flist = sorted(os.listdir("pages"))
for fname in flist:
    if year != fname[:4]:
        cou+=1
        continue
    if st > fname:
        continue
    parse((fname,cou))
    cou=cou+1
    print(cou)

# for 
# p = Pool(8)
# p.map(parse, [(flist[i], i) for i in range(len(flist))])
# p.close()

# result = Parallel(n_jobs=-1)([delayed(parse)(flist[i], i) for i in range(len(flist))])
session.add_all(results)
session.add_all(races)
session.commit()