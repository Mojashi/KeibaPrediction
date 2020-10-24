from sklearn.tree import *
from sklearn.model_selection import train_test_split
import sklearn.preprocessing as sp
import pandas as pd
from sklearn.metrics import *
import pickle
import lightgbm as lgb
import numpy as np
import matplotlib.pyplot as plt
import features

def lgb_f1_score(y_hat, data):
    y_true = data.get_label()
    y_hat = np.where(y_hat < 0.5, 0, 1)
    return 'f1', f1_score(y_true, y_hat), True


past_num = features.past_num

query = features.make_query() + " where re1.race_id between 30000 and 40000"
print(query)

df = pd.read_sql(query, "mysql://keiba@localhost/keiba?charset=utf8")

pd.options.display.max_rows = 1000
encoded = features.joinOther(df)
encoded = features.cleaning(encoded)
# encoded = features.clean2(encoded)

print(str(next(encoded.iterrows())))

train_set, test_set = train_test_split(encoded,test_size=0.1, shuffle=False)
print(train_set)
X_train = train_set.drop(['re1.rank'], axis=1)
y_train = train_set['re1.rank']

#モデル評価用データを説明変数データ(X_test)と目的変数データ(y_test)に分割
X_test = test_set.drop(['re1.rank'], axis=1)
y_test = test_set['re1.rank']

# 学習に使用するデータを設定
lgb_train = lgb.Dataset(X_train, y_train)
lgb_eval = lgb.Dataset(X_test, y_test, reference=lgb_train)

# params = {
#         'task': 'train',
#         'boosting_type': 'gbdt',
#         'objective': 'multiclassova',
#         'num_class': 2,
#         'metric': {'multi_error'},
#          'learning_rate': 0.001,
# }
params = {
        'task': 'train',
        'boosting_type': 'gbdt',
        'objective': 'binary',
       # 'metric': {'auc'},
         'learning_rate': 0.05,
}
print(X_test.head())
model = lgb.train(params,
        train_set=lgb_train, # トレーニングデータの指定
        valid_sets=lgb_eval, # 検証データの指定
        verbose_eval=10,
        num_boost_round=10000,
        early_stopping_rounds=500,
        categorical_feature=features.cats(encoded),
)


pre = model.predict(X_test,num_iteration=model.best_iteration)
# print(pre)
# y_test = y_test.tolist()
# for i in range(len(X_test)):
#     if pre[i] < 0.5:
#         print("pre:%s"%(pre[i]), end=" ")
#         print("ans:%s" %(y_test[i]))


pickle.dump(model, open("models/test2.lgb","wb"))
pickle.dump(test_set, open("models/test_set2.df","wb"))

print(pre)

pre = np.round(pre)
print(confusion_matrix(y_test, pre, labels=[0, 1]))
print(accuracy_score(y_test, pre))
plt.scatter(pre, y_test.tolist())
plt.show()

importance = pd.DataFrame(model.feature_importance(), index=X_test.columns, columns=['importance'])
print(importance.sort_values("importance"))