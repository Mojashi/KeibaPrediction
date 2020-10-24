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
#include <iomanip>
#include <algorithm>
#include <sstream>
#include <vector>
#include <ctime>
#include <assert.h>
#define WITHOUT_NUMPY
#include "matplotlibcpp.h"

#include "graph.hpp"
#include "sql.hpp"

using namespace std;
namespace plt = matplotlibcpp;

bool execMain(Proc& proc)
{
    random_device seed_gen;
    mt19937 engine(seed_gen());
    
    try {
        MYSQL_ROW row;
        MYSQL_RES* res;
        Race races[50000];
        vector<Feature> features;
        features.reserve(700000);
        proc.query("TRUNCATE features");

        scanSitCoeff(proc);
        map<string,int> horses = scanHorses(proc);

        int race_st = 000, race_en = 50000;
        int n = horses.size();
        Graph g(n), revg(n);
        
        vector<string> columns_result = {"result.id", "name", "time","race_id","rank","single_return"};
        vector<string> columns_race   = {"date", "length", "field", "id", "single_odds"};//,"umatan_odds", "umaren_odds"};
        
        res = proc.query("SELECT " + join(columns_race, ",") + " from race where id between "+to_string(race_st)+" and "+to_string(race_en)+" order by id");
        while ((row = mysql_fetch_row(res)) != NULL){
            Race buf = parseRace(columns_race, row);
            races[buf.id] = buf;
        }

        res = proc.query("SELECT " + join(columns_result, ",") + " from result join race on result.race_id=race.id where field='ダ' and length>=0 and race_id between "+to_string(race_st)+" and "+to_string(race_en)+" order by race_id");
        vector<Result> race;
        race.reserve(20);
        int bef_race = -1;

        vector<float> ekilog;
        ekilog.reserve(50000);

        int cou = 0, basecou = 0, edsum = 0, rowi = 0;
        float oddssum = 0;
        float eki = 0;
        while ((row = mysql_fetch_row(res)) != NULL){
            Result buf = parseResult(columns_result, row);
            if(buf.race_id == bef_race || bef_race == -1)
                race.push_back(buf);
            else{
                if(bef_race % 1000 == 0) fprintf(stderr, "race %d\n", bef_race);
                if(rowi > 1000){
                    shuffle(race.begin(), race.end(),engine);
                    vector<int> ids(race.size());

                    for(int i = 0; race.size() > i; i++)
                        ids[i] = horses[race[i].name];
                    Graph sub = extractGraph(g, ids, races[bef_race].date/DAY_SEC);
                    if(connected(sub)){
                    
                    // vector<int> pre = rankByDeg(sub);
                    // vector<int> pre = rankByFeedbackArc(sub);
                    vector<int> pre = rankByGreed(sub);
                    // vector<int> pre = rankByNeg(sub);
                    if(race[pre[0]].single_return >= RETURN_BOUND){
                        edsum += edCou(sub);
                        eki-=100;
                        if(race[pre[0]].rank == 1){
                            cou++;
                            int odds = races[bef_race].single_odds;
                            eki += odds;
                            oddssum += odds;
                        }
                        ekilog.push_back(eki);
                        basecou++;
                        }
                    }
                }

                makeEdge(g, races[bef_race], race, horses);
                // sort(race.begin(), race.end(), [](const Result& a, const Result& b){return a.rank < b.rank;});
                // for(int i = 0; race.size() > i; i++){
                //     int i_id = horses[race[i].name];
                //     for(int j = 0; i > j; j++){// i->j
                //         int j_id = horses[race[j].name];
                //         Edge ed = makeEdge(races[bef_race], race[i], i_id, race[j], j_id);//{i_id,j_id, min(MAX_LATE, (race[i].time - race[j].time)*sitCoeff(races[bef_race])), 1, int(races[bef_race].date/DAY_SEC)};
                //         g[i_id].push_back(ed);
                //         swap(ed.src,ed.to);
                //         revg[j_id].push_back(ed);
                //     }
                // }

                race.clear();
                race.shrink_to_fit();
                race.reserve(20);
                race.push_back(buf);
                rowi++;
            }   
            bef_race = buf.race_id;
        }
        mysql_free_result(res);
        cout << int(eki) << endl;
        fprintf(stderr, "win:%d/%d(%f) profit:%d(%f) eds:%f odds:%f \n",cou,basecou,cou*1.0/basecou, int(eki), 1+eki/100.0/basecou, edsum*1.0/basecou, oddssum / cou);

        // plt::plot(ekilog);
        // plt::show();
        // Close a MySQL connection
    } catch (char *e) {
        cerr << "[EXCEPTION] " << e << endl;
        return false;
    }
    return true;
}

/*
 * Execution
 */
int main(){
    Proc proc;
    execMain(proc);
    return 0;
}