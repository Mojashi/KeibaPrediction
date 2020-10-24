from sklearn.tree import *
from sklearn.model_selection import train_test_split
import sklearn.preprocessing as sp
import pandas as pd
from sklearn.metrics import *
import pickle
import optuna.integration.lightgbm as lgb
import numpy as np
import matplotlib.pyplot as plt
import features

def lgb_f1_score(y_hat, data):
    y_true = data.get_label()
    y_hat = np.where(y_hat < 0.5, 0, 1)
    return 'f1', f1_score(y_true, y_hat), True


past_num = features.past_num

query = features.make_query() + " where re1.race_id between 20000 and 40000 order by re1.race_id"
print(query)

df = pd.read_sql(query, "mysql://keiba@localhost/keiba?charset=utf8")

# pd.options.display.max_columns = 1000
encoded = features.joinOther(df)
encoded = features.erase(encoded)

encoded = features.cleaning(encoded, multi=False, rid=False)

features.predPretime(encoded)
# np.set_printoptions(threshold=np.inf)
# print(encoded[["pretime","pretimerank","re1.race_id"]].type(
# pd.options.display.max_rows = 10000
print(encoded[["pretime","pretimerank","re1.race_id"]])

pd.options.display.max_rows = 100

print(str(next(encoded.iterrows())))
models = ['wtimemultitop.lgb']

encodedb = encoded.copy()
encodedb.drop(features.drops+["re1.race_id"],axis=1,inplace=True)
for m in models:
    mo = pickle.load(open("models/"+m,"rb"))
    encoded.insert(0, m, mo.predict(encodedb)[:,0])

mname = models[0]

frs = pd.DataFrame(columns=[i for i in range(5)]+["diff"+str(i) for i in range(1,5)]+["hit"], index=encoded["re1.race_id"].unique())

dfl = []
befid=-1
for row in encoded.iterrows():
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
    df = pd.DataFrame(data=dfl, columns=encoded.columns)
    df.sort_values(mname, inplace=True,ascending=False)
    df.reset_index(inplace=True,drop=True)
    df = df[:5]
    # frs.loc[rid,:]=
    
    # for r in df.iterrows():
    #     frs.loc[befid,r[0]]=r[1][mname]
    frs.loc[befid,[i for i in range(5)]]=df[mname]
    frs.loc[befid,["diff"+str(i) for i in range(1,5)]]=(df[mname] - df[mname][0])[1:]
    frs.loc[befid,"hit"]=int(df["re1.rank"][0] == 1)
    print(frs.loc[befid,:])
    # print(df)
    dfl = []
    dfl.append(row[1])
    befid=row[1]["re1.race_id"]

frs.dropna(inplace=True)
frs.reset_index(inplace=True,drop=True)
frs = frs.astype('float')

train_set, test_set = train_test_split(frs,test_size=0.1, shuffle=False)
print(train_set)
X_train = train_set.drop(['hit'], axis=1)
y_train = train_set['hit']
# w_train = np.minimum(10,train_set['ra1.single_odds']/100)
pd.options.display.max_rows = 100
# print(w_train)
#モデル評価用データを説明変数データ(X_test)と目的変数データ(y_test)に分割
X_test = test_set.drop(['hit'], axis=1)
y_test = test_set['hit']
# w_test = np.minimum(10,test_set['ra1.single_odds']/100)

# 学習に使用するデータを設定
lgb_train = lgb.Dataset(X_train, y_train, weight=train_set['hit']*3+1)
lgb_eval = lgb.Dataset(X_test, y_test, reference=lgb_train,weight=test_set['hit']*3+1)

params = {
        'task': 'train',
        'boosting_type': 'gbdt',
        'objective': 'binary',
        
        'learning_rate': 0.001,
}
print(X_test.head())
model = lgb.train(params,
        train_set=lgb_train, # トレーニングデータの指定
        valid_sets=lgb_eval, # 検証データの指定
        verbose_eval=10,
        num_boost_round=10000,
        early_stopping_rounds=500,
        # categorical_feature=features.cats(encoded),
)


pre = model.predict(X_test,num_iteration=model.best_iteration)

pickle.dump(model, open("models/buy.lgb","wb"))
print(pre)

pre = np.round(pre)
print(confusion_matrix(y_test, pre, labels=[0, 1]))
print(accuracy_score(y_test, pre))
plt.scatter(pre, y_test.tolist())
plt.show()

importance = pd.DataFrame(model.feature_importance(), index=X_test.columns, columns=['importance'])
print(importance.sort_values("importance"))