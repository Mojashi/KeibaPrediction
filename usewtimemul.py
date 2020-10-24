from sklearn.tree import *
from sklearn.model_selection import train_test_split
import sklearn.preprocessing as sp
import pandas as pd
import pickle
from sklearn.metrics import *
import lightgbm as lgb
import math
import features
import matplotlib.pyplot as plt
import numpy as np
import optuna
import cProfile

timemodel = pickle.load(open("models/reg.lgb","rb"))
model = pickle.load(open("models/wtimemultitop.lgb","rb"))

st = 45000
en = 47000

query = features.make_query() + " WHERE re1.race_id between %s and %s order by re1.race_id"%(st,en)
print(query)

dff = pd.read_sql(query, "mysql://keiba@localhost/keiba?charset=utf8")

odds = pd.read_sql("SELECT id,single_odds,multi_odds1,multi_odds2,multi_odds3 from race where id between %s and %s" % (st, en), "mysql://keiba@localhost/keiba?charset=utf8")
odds.set_index("id", inplace=True)


pd.options.display.max_rows = 1000

encoded = features.joinOther(dff.copy())
races = features.cleaning(encoded,rid=False)
races = features.predPretime(races)
# races.insert(0,"pretime", timemodel.predict(races.drop(features.drops, axis=1)))
# races.drop("re1.race_id",axis=1,inplace=True)
# races.reset_index(inplace=True,drop=True)

# races.insert(0,"pretime", timemodel.predict(races.drop(["re1.rank", "re1.time_index", "re1.time"], axis=1)))
prebuf = model.predict(features.delCol(races.drop(features.drops, axis=1), "re1.race_id"))
# races['re1.rank'] = 
dff.dropna(how='any', inplace=True)
# print(dff.columns)
dff.reset_index(inplace=True, drop=True)
dff.insert(0,"pre0", prebuf[:,0])
dff.insert(0,"pre1", prebuf[:,1])
dff.insert(0,"pre2", prebuf[:,2])
# print(dff)

def testRace(st,en, diff,sig,modds, multi=False, verbose=0):
    sumc = 0
    kake = 0
    tekic = 0
    befid = -1

    def judge(df):
        nonlocal sumc
        nonlocal kake
        nonlocal tekic

        if len(df) <= 4:
            return
        if len(df) <= df["ra1.num_horse"][0]/2:
            return
        if df["ra1.num_horse"][0] != len(df):
            return
        # encoded = features.cleaning(df,rank=False)
        pre = df["pre0"].tolist()
        aso = np.argsort(pre)[::-1]
        pf = aso[0]
        # print(np.argsort(pre)[::1])
        # print(aso)
        # print("%d:%d"%(encoded["re1.rank"][pf],ret))
        if pre[aso[0]] - pre[aso[1 if multi else 1]] >= diff and pre[aso[0]] > sig and df["re1.single_return"][aso[0]] > modds:
            # for i in range(len(df)):
            #     print("pre:%s rank:%s %s" % (pre[i], df["re1.rank"][i], df["re1.single_return"][i]))
            sumc -= 100
            kake += 1
            if df["re1.rank"][pf] <= (3 if multi else 1):
                ret = odds["multi_odds%d"%(df["re1.rank"][pf])][race_id] if multi else odds["single_odds"][race_id]
                # ret = odds["single_odds"][race_id]
                if math.isnan(ret):
                    return
                if verbose >= 1:
                    print("的中！ ret:%s"%(ret))
                sumc += ret
                tekic+=1
                if verbose >= 2:
                    print("---------\n%d"%(race_id))
                    for i in range(len(X_test)):
                            print("pre:%s rank:%s %s" % (pre[i], df["re1.rank"][i], df["re1.single_return"][i]))


    dfl = []
    print("start")
    
    for row in dff.iterrows():
        # print(row[1])
        if befid == -1:
            dfl.append(row[1])
            befid=row[1]["re1.race_id"]
            continue

        if row[1]["re1.race_id"] == befid:
            dfl.append(row[1])
            continue


        race_id = befid
        # print(race_id)
        # print(dfl)
        # df = 
        judge(pd.DataFrame(data=dfl, columns=dff.columns, index=[i for i in range(len(dfl))]))

        dfl = []
        dfl.append(row[1])
        befid=row[1]["re1.race_id"]

    print(sumc)
    print("%d/%d"%(tekic,kake))
    if kake > 0:
        print(tekic/kake)
    else:
        return np.nan
    return sumc

def testGreedy(st,en,verbose=0):
    sum = 0
    kake = 0
    tekic = 0
    global model

    for race_id in range(st,en):
        df = races[races["re1.race_id"]==race_id].copy()
        df.reset_index(inplace=True,drop=True)
        df.drop("re1.race_id", axis=1, inplace=True)
        if len(df) <= 3:
            continue
        if len(df) <= df["ra1.num_horse"][0]/2:
            continue
        # if df["ra1.num_horse"][0] != len(df):
        #     return

        pf = np.argmin(df["re1.popularity"])
        sum -= 100
        kake += 1
        if df["re1.rank"][pf] <= 3:
            ret = odds["multi_odds%d"%(df["re1.rank"][pf])][race_id]
            if math.isnan(ret):
                continue
            if verbose >= 1:
                print("的中！ ret:%s"%(ret))
            sum += ret
            tekic+=1
            if verbose >= 2:
                print("---------\n%d"%(race_id))
                for i in range(len(df)):
                    print("pop:%s rank:%s %s" % (df["re1.popularity"][i], df["re1.rank"][i], df["re1.single_return"][i]))

    print(sum)
    print("%d/%d"%(tekic,kake))
    print(tekic/kake)
# test_set = pickle.load(open("models/test_set2.df","rb"))

# X_test = test_set.drop(['re1.rank','re1.single_return'], axis=1)
# y_test = test_set['re1.rank']

# pre = model.predict(X_test)
# y_list = y_test.tolist()

# sum = 0

# test_set.reset_index(inplace=True, drop=True)
# for i in range(len(X_test)):
#     if pre[i] < 1.0:
#         print("pre:%s"%(pre[i]), end=" ")
#         print("ans:%s" %(y_list[i]), end="\n")
#         print(test_set["re1.single_return"][i])
#         sum -= 100
#         if y_list[i] == 0:
#             sum += test_set["re1.single_return"][i]*100

# print(sum)
# pre = np.round(pre)
# print(confusion_matrix(y_test, pre, labels=[0, 1]))
# print(accuracy_score(y_test, pre))
# print(f1_score(y_test,pre))

def objective(trial):
    ret = testRace(st,en, trial.suggest_uniform("diff",0,0.4), trial.suggest_uniform("sig",0,1), trial.suggest_uniform("modds",0,5),multi=False)
    return ret
def opt():
    study = optuna.create_study(direction='maximize')
    study.optimize(objective, n_trials=1000)

def expe():
    testRace(st,en,0.0,0,2.0,multi=False)
    plt.scatter(dff["re1.rank"].tolist(), dff["pre0"].tolist(),s=60, c="pink", alpha=0.2, linewidths=2, edgecolors="red")
    plt.show()
# cProfile.run('expe()', "restats")
opt()