
import sklearn.preprocessing as sp
import pandas as pd
import numpy as np
import pickle

class MultiColumnLabelEncoder:
    def __init__(self,columns = None):
        self.columns = columns # array of column names to encode

    def fit(self,X,y=None):
        return self # not relevant here

    def transform(self,X):
        '''
        Transforms columns of X specified in self.columns using
        LabelEncoder(). If no columns specified, transforms all
        columns in X.
        '''
        output = X.copy()
        if self.columns is not None:
            for col in self.columns:
                tbl = "race"
                if "re" in col:
                    tbl = "result"
                print(col)
                output[col] = getEncoder(tbl, col.split(".")[1].split("-")[0]).transform(output[col])
        else:
            for colname,col in output.iteritems():
                output[colname] = sp.LabelEncoder().fit_transform(col)
        return output

    def fit_transform(self,X,y=None):
        return self.fit(X,y).transform(X)

dists = {}

def getEncoder(tbl, col):
    if (tbl,col) in dists:
        return dists[tbl,col]
    df = pd.read_sql("SELECT distinct(%s) from %s"%(col,tbl), "mysql://keiba@localhost/keiba?charset=utf8")
    le = sp.LabelEncoder()
    le.fit(df)
    dists[(tbl,col)] = le
    return le


othercou = 0
past_num = 3
res_past_need = ["race_id", "age", "impost", "time","agari","iday", "weight",  "time_index","weight_diff", "rank", "position","popularity"]
rac_past_need = ["place","date", "weather", "field_state", "field", "num_horse", "length", "race_class", "obstacle", "const_age", "const_sex", "const_impose"]
res_cur_need =  ["single_return", "race_id", "age", "sex","iday", "time", "impost", "position", "weight","weight_diff","rank", "time_index"]
rac_cur_need =  ["single_odds", "place", "date", "weather", "field_state", "field", "num_horse", "length", "race_class", "obstacle", "const_age", "const_sex", "const_impose"]

drops = ['re1.rank','re1.time_index','re1.time', 'ra1.single_odds', 're1.single_return']
# res_past_need = ["race_id", "agari","iday", "weight", "time_index","weight_diff", "position"]
# rac_past_need = ["place", "date", "weather", "field_state", "field", "num_horse", "length", "race_class", "obstacle", "const_age", "const_sex", "const_impose"]
# res_cur_need =  ["race_id", "age", "sex", "iday", "impost", "position", "weight","weight_diff","rank","time_index"]
# rac_cur_need =  ["place", "date", "weather", "field_state", "field", "num_horse", "length", "race_class", "obstacle", "const_age", "const_sex", "const_impose"]


def make_query(ae_past=[],aa_past=[],ae_cur=[],aa_cur=[]):

    items = []

    for item in res_cur_need+ae_cur:
        items.append("re1.%s 're1.%s'" % (item,item))
    for item in rac_cur_need+aa_cur:
        items.append("ra1.%s 'ra1.%s'" % (item,item))

    for i in range(2,2+past_num):
        for item in res_past_need+ae_past:
            items.append("re%d.%s 're%d.%s'" % (i,item,i,item))
        for item in rac_past_need+aa_past:
            items.append("ra%d.%s 'ra%d.%s'" % (i,item,i,item))

    query = "SELECT " + ",".join(items) + " FROM result re1 JOIN race ra1 ON re1.race_id=ra1.id"
    for i in range(2, past_num + 2):
        query += " JOIN result re%d ON re%d.bef=re%d.id JOIN race ra%d ON re%d.race_id=ra%d.id" % (i, i-1, i, i, i, i)
    return query

cat = ["race_class","weather","jockey","name","sex","field_state","field",]
def cats(df):
    #cat = [("ra","race_class"),("ra","weather"),("re","jockey"),("re", "name"),("re","sex"),("ra","field"),("ra","field_state")]
    lbs = []

    for col in df.columns:
        for c in cat:
            if c in col:
                lbs.append(col)
                break
    return lbs

def delCol(df, col):
    for x in df.columns:
        if col in x:
            df.drop(x,axis=1, inplace=True)
    return df
def erase(df):

    saverows = []
    befid = -1
    befnhoese = -1
    succou = 0
    for row in df.iterrows():
        if befid == row[1]["re1.race_id"]:
            succou += 1
        else:
            if succou != 0:
                if succou == befnhorse:
                    saverows.append(befid)
            succou=1
        befid = row[1]["re1.race_id"]
        befnhorse = row[1]["ra1.num_horse"]
    # print(saverows)
    df = df[df["re1.race_id"].isin(saverows)].reset_index(drop=True)

    return df

def cleaning(df,multi=False, lambdarank=False,binary=False,rank=True,buy=False,rid=True):
    df.dropna(how='any', inplace=True)
    df.reset_index(inplace=True, drop=True)
    lbs = cats(df)
    # print(next(df.iterrows()))
    # print(next(df.iterrows()))
    
    
    for i in range(1, 2):
        col = "ra%d.date"%(i)
        bcol = "ra%d.date"%(i+1)
        # ncol = "ra%d.delta_day" % (i)
        mcol = "ra%d.daytime" % (i)
        buf=[]
        buf2=[]
        for j in range(len(df[col])):
            # buf.append((df[col][j] - df[bcol][j]).days)
            buf2.append(df[col][j].hour)
        # df.insert(0,ncol,buf)
        df.insert(0,mcol,buf2)
        # df.loc[::,ncol] = buf
        # df.loc[::,mcol] = buf2
    
    # for i in range(1, past_num+2):
    #     col = "ra%d.date"%(i)
    #     df.drop(columns=[col],inplace=True)
    
    for x in df.columns:
        if (rid and "race_id" in x) or "date" in x:
            # print(x)
            df.drop(x,axis=1, inplace=True)

    if lambdarank:
        buf3 = []
        for j in range(len(df["re1.rank"])):
            # buf3.append(int(10.0 / df["re1.rank"][j]))
            # buf3.append(df["ra1.num_horse"][j] - df["re1.rank"][j] + 1)
            buf3.append(int(18-20*(df["re1.rank"][j]-1)/df["ra1.num_horse"][j]))
            # buf3.append(5-int(df["re1.rank"][j] / (df["ra1.num_horse"][j]/5)))
            # if df["re1.rank"][j] <= 1:
            #     buf3.append(4)
            # elif df["re1.rank"][j] <= 2:
            #     buf3.append(3)
            # elif df["re1.rank"][j] <= 3:
            #     buf3.append(2)
            # elif df["re1.rank"][j] <= 4:
            #     buf3.append(1)
            # else:
            #     buf3.append(0)
            # buf3.append(20-int((df["re1.rank"][j]) / 2))
            # buf3.append(df["re1.time_index"][j])
        df.loc[::,"re1.rank"] = buf3
    elif binary:
        buf3 = []
        for j in range(len(df["re1.rank"])):
            if df["re1.rank"][j] <= 1:
                buf3.append(0)
            else:
                buf3.append(1)
        df.loc[::,"re1.rank"] = buf3
    elif multi:
        buf3 = []
        for j in range(len(df["re1.rank"])):
            if df["re1.rank"][j] <= 3:
                buf3.append(0)
            elif df["re1.rank"][j] <= 3 + int((df["ra1.num_horse"][j]-2)/2):
                buf3.append(1)
            else:
                buf3.append(2)
        df.loc[::,"re1.rank"] = buf3
    
    
    for i in range(2, past_num+2):
        ce = "re%d.rank" % (i)
        ca = "ra%d.num_horse" % (i)
        buf4 = []
        if ce not in df.columns or ca not in df.columns:
            continue 
        for j in range(len(df[ce])):
            buf4.append(df[ce][j]*1.0 / df[ca][j])
        df[ce].update(buf4)
    #print(df["re2.rank"])
    # print(lbs)

    encoded = MultiColumnLabelEncoder(columns = lbs).fit_transform(df)

    return encoded

def joinOther(df,ae_past=[],aa_past=[],ae_cur=[],aa_cur=[]):
    items = []
    remed = res_cur_need.copy()
    remed.remove("rank")
    for item in remed+ae_cur:
        items.append("re1.%s 're1.%s'" % (item,item))
    for item in rac_cur_need+aa_cur:
        items.append("ra1.%s 'ra1.%s'" % (item,item))

    for i in range(2,2+past_num):
        for item in res_past_need+ae_past:
            items.append("re%d.%s 're%d.%s'" % (i,item,i,item))
        for item in rac_past_need+aa_past:
            items.append("ra%d.%s 'ra%d.%s'" % (i,item,i,item))

    query = "SELECT " + ",".join(items) + " FROM result re1 JOIN race ra1 ON re1.race_id=ra1.id"
    for i in range(2, past_num + 2):
        query += " JOIN result re%d ON re%d.bef=re%d.id JOIN race ra%d ON re%d.race_id=ra%d.id" % (i, i-1, i, i, i, i)
    query += " WHERE re1.popularity<=%d" % (othercou)
    jd = pd.read_sql(query, "mysql://keiba@localhost/keiba?charset=utf8")
    
    for i in range(1,othercou + 1):
        df = pd.merge(df, jd[jd["re1.popularity"]==i].add_suffix("-%d"%(i)), left_on="re1.race_id", right_on="re1.race_id-%d"%(i), how="inner")
    
    # print(df.columns.tolist())
    return df
def predPretime(encoded):
    timemodel = pickle.load(open("models/reg.lgb","rb"))
    encoded.insert(0, 'pretime', timemodel.predict(delCol(encoded.drop(drops,axis=1),"race_id")))

    befid = -1
    succou = 0
    pretimes = []
    ids = []
    pretimerank = np.zeros(len(encoded))
    for row in encoded.iterrows():
        if befid == row[1]["re1.race_id"]:
            succou += 1
        else:
            if succou != 0:
                r = 1
                # print(pretimes)
                bufids = np.array(ids)
                for i in bufids[np.argsort(pretimes)]:
                    pretimerank[i] = r
                    r+=1
                ids = []
                pretimes = []
            succou=1
        befid = row[1]["re1.race_id"]
        pretimes.append(row[1]["pretime"])
        ids.append(row[0])
    encoded.insert(0,"pretimerank", pretimerank)
    return encoded