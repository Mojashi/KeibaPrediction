from sklearn.tree import *
from sklearn.model_selection import train_test_split
import sklearn.preprocessing as sp
import pandas as pd
from sklearn.metrics import *
import pickle
import lightgbm as lgb
import numpy as np
import features
import matplotlib.pyplot as plt

def lgb_f1_score(y_hat, data):
    y_true = data.get_label()
    y_hat = np.where(y_hat < 0.5, 0, 1)
    return 'f1', f1_score(y_true, y_hat), True


past_num = features.past_num

query = features.make_query() + " where re1.race_id between 20000 and 40000 order by re1.race_id"
print(query)

df = pd.read_sql(query, "mysql://keiba@localhost/keiba?charset=utf8")

pd.options.display.max_rows = 1000
encoded = features.joinOther(df)
# encoded = features.clean2(encoded)

print(str(next(encoded.iterrows())))

group = []
befid = -1
succou = 0
for row in encoded.iterrows():
    if befid == row[1]["re1.race_id"]:
        succou += 1
    else:
        if succou != 0:
            group.append(succou)
        succou=1
    befid = row[1]["re1.race_id"]
group.append(succou)

# plt.bar([i for i in range(0, 19)], [sum(encoded["re1.rank"] == i) for i in range(0,19)])
# plt.show()

encoded = features.cleaning(encoded, lambdarank=True)

# plt.bar([i for i in range(0, 4)], [sum(encoded["re1.rank"] == i) for i in range(0,4)])
# plt.show()

train_set, test_set = train_test_split(encoded,train_size=sum(group[:int(len(group)*0.8)]), shuffle=False)
gtrain_set, gtest_set = train_test_split(group,train_size=int(len(group)*0.8), shuffle=False)
print(train_set)
# print(sum(group[:int(len(group)*0.8)]))
# print(sum(gtrain_set))
# print(group)
# print(gtrain_set)
# print(gtest_set)
X_train = train_set.drop(['re1.rank','re1.time_index'], axis=1)
y_train = train_set['re1.rank']

#モデル評価用データを説明変数データ(X_test)と目的変数データ(y_test)に分割
X_test = test_set.drop(['re1.rank', "re1.time_index"], axis=1)
y_test = test_set['re1.rank']
y_rank = test_set['re1.rank']


# 学習に使用するデータを設定
lgb_train = lgb.Dataset(X_train, y_train, group=gtrain_set)
lgb_eval = lgb.Dataset(X_test, y_test, reference=lgb_train, group=gtest_set)


# params = {
#     'task': 'train',
#     'boosting_type': 'gbdt',
#     'objective': 'lambdarank',
#     'metric': 'ndcg',   # for lambdarank
#     'ndcg_eval_at': [1,2,3],  # for lambdarank
#     # 'max_position': max_position,  # for lambdarank
#     'learning_rate': 0.001,
#     'label_gain':[i*i for i in range(0,np.max(df['re1.rank']) + 1)]
#     # 'min_data': 1,
#     # 'min_data_in_bin': 1,
    
# }
# print(X_test.head())
# model = lgb.train(params,
#         train_set=lgb_train, # トレーニングデータの指定
#         valid_sets=lgb_eval, # 検証データの指定
#         verbose_eval=10,
#         num_boost_round=10000,
#         early_stopping_rounds=2000,
#         categorical_feature=features.cats(encoded),
# )

model = lgb.LGBMRanker(n_estimators=10000)
model.fit(X_train, y_train, group=gtrain_set, eval_set=[(X_test, y_test)],
    eval_group=[gtest_set], eval_at=[3], early_stopping_rounds=2000, verbose=True,
    callbacks=[lgb.reset_parameter(learning_rate=lambda x: max(0.01, 0.1 - 0.01 * x))])

# print(pre)
# y_test = y_test.tolist()
# for i in range(len(X_test)):
#     if pre[i] < 0.5:
#         print("pre:%s"%(pre[i]), end=" ")
#         print("ans:%s" %(y_test[i]))


pickle.dump(model, open("models/rankw.lgb","wb"))

pre = model.predict(X_test)

# print(pre)
# print(y_test)
plt.scatter(pre, y_rank.tolist(),s=60, c="pink", alpha=0.1, linewidths=1, edgecolors="pink")
plt.show()
# plt.scatter(pre, y_test.tolist(),s=60, c="blue", alpha=0.1, linewidths=1, edgecolors="blue")
# plt.show()
# pre = np.round(pre)
# print(confusion_matrix(y_test, pre, labels=[0, 1]))
# print(accuracy_score(y_test, pre))

importance = pd.DataFrame(model.feature_importances_, index=X_test.columns, columns=['importance'])
print(importance.sort_values("importance"))