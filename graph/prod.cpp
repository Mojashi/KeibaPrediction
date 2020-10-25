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
        scanSitCoeff(proc);
        map<string,int> horses = scanHorses(proc);

        int race_st = 000, race_en = 50000;
        int n = horses.size();
        Graph g(n), revg(n);
        
        vector<string> columns_result = {"result.id", "name", "time","race_id","rank","single_return"};
        vector<string> columns_race   = {"date", "length", "field", "id", "single_odds"};//,"umatan_odds", "umaren_odds"};
        
        Race races[50000];
        res = proc.query("SELECT " + join(columns_race, ",") + " from race where id between "+to_string(race_st)+" and "+to_string(race_en)+" order by id");
        while ((row = mysql_fetch_row(res)) != NULL){
            Race buf = parseRace(columns_race, row);
            races[buf.id] = buf;
        }

        res = proc.query("SELECT " + join(columns_result, ",") + " from result join race on result.race_id=race.id where field='ダ' and length>=0 and race_id between "+to_string(race_st)+" and "+to_string(race_en)+" order by race_id");
        vector<Result> race;
        race.reserve(20);
        int bef_race = -1;

        while ((row = mysql_fetch_row(res)) != NULL){
            Result buf = parseResult(columns_result, row);
            if(buf.race_id == bef_race || bef_race == -1)
                race.push_back(buf);
            else{
                if(bef_race % 1000 == 0) fprintf(stderr, "race %d\n", bef_race);
                makeEdge(g, races[bef_race], race, horses);
                race.clear();
                race.shrink_to_fit();
                race.reserve(20);
                race.push_back(buf);
            }   
            bef_race = buf.race_id;
        }
        mysql_free_result(res);
        int t;
        cin >> t;
        for(int cc = 0 ;t > cc;cc++){
        string title;
        cin >> title;
        int m;
        cin >> m;
        vector<int> ids;
        vector<pair<string, float>> attends;
        map<int,string> names;
        for(int i = 0; m > i; i++){
            string name;
            float odds;
            cin >> name >> odds;
            
            attends.push_back({name, odds});
            names[i] = name;
            ids.push_back(horses[name]);
        }
        cerr << time(NULL)/DAY_SEC << endl;
        Graph sub = extractGraph(g, ids, time(NULL)/DAY_SEC);
        
        vector<int> pre = rankByGreed(sub);
        cout << title << ":";
        if(connected(sub) && attends[pre[0]].second >= RETURN_BOUND){
            cout << attends[pre[0]].first << endl;
        }else {
            cout <<"NONE " <<  attends[pre[0]].first << endl;
        }
        showGraph(sub,string()+"out/"+to_string(cc)+".dot", names);
    }
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
    readParams();
    Proc proc;
    execMain(proc);
    return 0;
}