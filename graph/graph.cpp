#include <iostream>
#include <mysql/mysql.h>
#include <string>
#include <map>
#include <random>
#include <unordered_map>
#include <utility>
#include <string>
#include <set>
#include <locale>
#include <cstdlib>
#include <iomanip>
#include <algorithm>
#include <fstream>
#include <sstream>
#include <vector>
#include <ctime>
#include <assert.h>
#include "sql.hpp"
#include "graph.hpp"

using namespace std;

float INDIRECT_COEFF = 0.3, MIRROR_COEFF = 0.1, CENTER_COEFF = 0.1, WEIGHT_BOUND = 0.5;
float hangen = 365, pace = 300;
float MAX_LATE = 10;
float RETURN_BOUND = 0;
float sitCoeffAr[3][5000] = {};
const int MAX_NUMHORSE = 18;
const int DAY_SEC = 86400;

Edge makeEdge(const Race& race, const Result& a, int aid, const Result& b, int bid){
    return {aid,bid, min(MAX_LATE, (a.time - b.time)*sitCoeff(race)), 1, int(race.date/DAY_SEC)};
}

void makeEdge(Graph& g, const Race& race, vector<Result>& ress,const map<string,int>& horses){
    sort(ress.begin(), ress.end(), [](const Result& a, const Result& b){return a.rank < b.rank;});
    for(int i = 0; ress.size() > i; i++){
        int i_id = horses.at(ress[i].name);
        for(int j = 0; i > j; j++){// i->j
            int j_id = horses.at(ress[j].name);
            Edge ed = makeEdge(race, ress[i], i_id, ress[j], j_id);//{i_id,j_id, min(MAX_LATE, (race[i].time - race[j].time)*sitCoeff(races[bef_race])), 1, int(races[bef_race].date/DAY_SEC)};
            g[i_id].push_back(ed);
            swap(ed.src,ed.to);
            // revg[j_id].push_back(ed);
        }
    }
}

inline float timeCoeff(int iday){
    const float a = 1 - (- 1/(1 + exp(-hangen / pace)));
    return a - 1/(1 + exp((iday - hangen) / pace));
}

float sitCoeff(const Race& ra){
    int fi = -1;
    if(ra.field == "ダ") fi = 0;
    else if(ra.field == "芝") fi = 1;
    else if(ra.field == "障") fi = 2;
    // if(fi == 2) printf("aa");
    // printf("%d\n",fi);
    return sitCoeffAr[fi][ra.length];
}
Graph extractGraph(const Graph& g, const vector<int>& vs, int baseday = 0){
    float mat[MAX_NUMHORSE][MAX_NUMHORSE] = {};
    float cou[MAX_NUMHORSE][MAX_NUMHORSE] = {};

    unordered_map<int,int> um;
    unordered_map<int,vector<Edge>> oins;
    for(int i = 0; vs.size() > i; i++)
        um[vs[i]] = i;
    for(auto& v : vs){
        for(auto& r : g[v]){
            if(um.count(r.to)){
                float c = baseday == 0 ? 1 : timeCoeff(baseday - r.date);
                mat[um[v]][um[r.to]] += r.diff*c;
                cou[um[v]][um[r.to]] += c;
            }
            else
                oins[r.to].push_back(r);
        }
    }

    for(auto o : oins){
        for(auto v : g[o.first]){
            if(um.count(v.to)){
                for(auto sv : o.second){
                    float c = baseday == 0 ? 1 : timeCoeff(baseday - (sv.date + v.date) / 2)*INDIRECT_COEFF;
                    mat[um[sv.src]][um[v.to]] += (sv.diff + v.diff)*c;
                    cou[um[sv.src]][um[v.to]] += c;
                }
            }
        }
        for(int i = 0; o.second.size() > i; i++){
            for(int j = i + 1; o.second.size() > j; j++){
                int f = i,s = j;
                if(o.second[f].diff < o.second[s].diff){
                    swap(f,s);
                }
                float c = baseday == 0 ? 1 : timeCoeff(baseday - (o.second[f].date + o.second[s].date) / 2)*MIRROR_COEFF;
                mat[um[o.second[f].src]][um[o.second[s].src]] += (o.second[f].diff - o.second[s].diff) * c;
                cou[um[o.second[f].src]][um[o.second[s].src]] += c;
            }
        }
    }

    Graph ret(vs.size());
    for(int i = 0; vs.size() > i; i++){
        for(int j = 0; vs.size() > j; j++){
            if(i != j)
                if(cou[i][j] > 0) ret[i].push_back({i,j,mat[i][j], cou[i][j]});
        }
    }
    return ret;
}

Graph subGraph(const Graph& g, const vector<int>& vs){
    Graph ret(vs.size());
    unordered_map<int,int> um;
    for(int i = 0; vs.size() > i; i++)
        um[vs[i]] = i;
    for(auto& v : vs){
        for(auto& r : g[v]){
            if(um.count(r.to))
                ret[um[v]].push_back({um[v], um[r.to], r.diff});
        }
    }
    return ret;
}

inline float divz(float a, float b){
    return a > 0 ? a/b : 0;
}

std::random_device seed_gen;
std::mt19937 engine(seed_gen());

float calcScore(const Graph& g, vector<int>& ds){
    float score = 0;
    vector<int> rev(ds.size());

    for(int i = 0; ds.size() > i; i++)
        rev[ds[i]] = i;
    
    for(auto eds : g){
        for(auto ed : eds){
            if(rev[ed.src] > rev[ed.to])
                score += ed.diff/ed.rcsum;
        }
    }

    return score;
}
vector<int> rankByFeedbackArc(const Graph& g){
    vector<int> ds(g.size());
    // for(int i = 0; ds.size() > i; i++) ds[i] = i;
    ds = rankByGreed(g);
    float mat[MAX_NUMHORSE][MAX_NUMHORSE] = {}, cou[MAX_NUMHORSE][MAX_NUMHORSE] = {}, score = calcScore(g,ds);
    for(auto eds : g){
        for(auto ed : eds){
            mat[ed.src][ed.to] = ed.diff;
            cou[ed.src][ed.to] = ed.rcsum;
        }
    }

    float best_score = score;
    vector<int> best = ds;

    for(int cc = 0; 100 > cc; cc++){
        while(1){
            bool f = false;
            for(int i = 0; ds.size()-1 > i; i++){
                if(divz(mat[ds[i]][ds[i + 1]],cou[ds[i]][ds[i + 1]]) - divz(mat[ds[i + 1]][ds[i]],cou[ds[i+1]][ds[i]]) > 0){
                    score -= divz(mat[ds[i + 1]][ds[i]],cou[ds[i+1]][ds[i]]);
                    swap(ds[i], ds[i + 1]);
                    score += divz(mat[ds[i + 1]][ds[i]],cou[ds[i+1]][ds[i]]);
                    f = true;
                }
            }
            for(int i = 0; ds.size() > i; i++){
                for(int j = i + 2; ds.size() > j; j++){
                    swap(ds[i], ds[j]);
                    float ns = calcScore(g, ds);
                    if(ns > score) {
                        score = ns;
                        f = true;
                    }else{
                        swap(ds[i], ds[j]);
                    }
                }
            }
            if(!f) break; 
        }
    }
    return ds;
}

vector<int> rankByGreed(const Graph& g){
    vector<pair<float,int>> ds(g.size());
    vector<float> cou(g.size());
    for(int i = 0; g.size() > i; i++){
        ds[i].second = i;
        for(auto ed : g[i]){
            ds[i].first -= ed.diff;
            ds[ed.to].first+=ed.diff;
            cou[ed.to]+=ed.rcsum;
            cou[ed.src]+=ed.rcsum;
        }       
    }
    for(int i = 0; g.size() > i; i++)
        ds[i].first /= cou[i];

    sort(ds.begin(),ds.end(), greater<pair<float,int>>());
    vector<int> ret(ds.size());
    for(int i = 0; ds.size() > i; i++)
        ret[i] = ds[i].second;
    return ret;
}

vector<int> rankByNeg(const Graph& g){
    vector<int> ds(g.size());
    float mat[MAX_NUMHORSE] = {}, cou[MAX_NUMHORSE] = {};
    vector<int> ret(g.size());
    for(int i = 0; g.size() > i; i++){
        ds[i] = i;
        for(auto ed : g[i]){
            mat[i] -= ed.diff;
            mat[ed.to]+=ed.diff;
            cou[ed.to]+=ed.rcsum;
            cou[ed.src]+=ed.rcsum;
        }       
    }

    sort(ds.begin(),ds.end(), [mat,cou](const int a,const int b){return mat[a]/cou[a] > mat[b]/cou[b];});
    for(int i = g.size()-1; 0 <= i; i--){
        for(auto ed : g[i]){
            mat[ed.to]-=ed.diff;
            cou[ed.to]-=ed.rcsum;
        }
        sort(ds.begin(),ds.begin() + i, [mat,cou](const int a,const int b){return mat[a]/cou[a] > mat[b]/cou[b];});
    }
    return ds;
}

vector<int> rankByDeg(const Graph& g){
    if(g.size() == 1) return {0};
    if(g.size() == 0) return {};
    vector<pair<float,int>> ds(g.size());
    vector<float> cou(g.size());
    for(int i = 0; g.size() > i; i++){
        ds[i].second = i;
        for(auto ed : g[i]){
            ds[i].first -= ed.diff;
            ds[ed.to].first+=ed.diff;
            cou[ed.to]+=ed.rcsum;
            cou[ed.src]+=ed.rcsum;
        }       
    }
    for(int i = 0; g.size() > i; i++)
        ds[i].first /= cou[i];

    sort(ds.begin(),ds.end(), greater<pair<float,int>>());
    vector<int> ids[2];// = {vector<int>(ds.size()/2, ds.size()-ds.size()/2)};
    for(int i = 0; ds.size() > i; i++)
        ids[i>=ds.size()/2].push_back(ds[i].second);
    vector<int> ret;
    ret.reserve(ds.size());
    for(auto v : rankByDeg(extractGraph(g, ids[0]))){
        ret.push_back(ids[0][v]);
    }
    for(auto v : rankByDeg(extractGraph(g, ids[1]))){
        ret.push_back(ids[1][v]);
    }
    return ret;
}

int edCou(const Graph& g){
    int ret = 0;
    for(auto itr : g){
        ret += itr.size();
    }
    return ret;
}

bool connected(const Graph& g){
    float cou[MAX_NUMHORSE] = {};
    for(auto& eds : g){
        for(auto& ed : eds){
            cou[ed.src] += ed.rcsum;
            cou[ed.to]+=ed.rcsum;
        }
    }
    for(int i = 0; g.size() > i; i++){
        if(cou[i] <= WEIGHT_BOUND) return false;
    }
    return true;
}

void showGraph(const Graph& g, string fname, const map<int, string>& names){
    ofstream ofs(fname);
    ofs << "digraph G {" << endl;
    for(auto name : names) {
        ofs << name.first << "[label=" <<name.second << "];" << endl; 
    }
    for(auto eds : g){
        for(auto ed : eds){
            ofs << ed.src << "->" << ed.to << "[label=\"" << ed.diff << "/" << ed.rcsum << "\"];" <<endl;
        }
    }
    ofs << "}" << endl;
    ofs.close();
    int ret = system((string("dot -T png ") + fname + " -o " + fname + ".png").c_str());
}