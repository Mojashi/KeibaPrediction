#pragma once
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
using namespace std;

struct Race{
    int id,length, rentan_odds,renpuku_odds,single_odds,umatan_odds,umaren_odds;
    time_t date;
    string field;
};
struct Result{
    //| id | name | age  | sex  | impost | jockey       | time | diff | passrank | agari | single_return | popularity | weight | weight_diff | trainer            | owner        | rank | race_id | position | time_index | bef  | iday |
    int id,age,popularity,weight,weight_diff,rank,race_id,position,time_index,bef,iday;
    float impost,time,agari,single_return;
    string name,sex,jockey,diff,passrank,trainer,owner;
};
struct Feature{
    int in_deg, out_deg, diff_deg;
    float in_sum, out_sum;
};

class Proc
{
    const char* MY_HOSTNAME;
    const char* MY_DATABASE;
    const char* MY_USERNAME;
    const char* MY_PASSWORD;
    const char* MY_SOCKET;
    enum {
        MY_PORT_NO = 3306,
        MY_OPT     = 0
    };
    MYSQL     *conn;

public:
    Proc();
    // bool execMain();  // Main Process
    MYSQL_RES* query(string);
    ~Proc();
};


void scanSitCoeff(Proc& proc);
map<string,int> scanHorses(Proc& proc);
std::string join(const std::vector<std::string>& v, const char* delim);

Race parseRace(vector<string>& columns, MYSQL_ROW& row);
Result parseResult(vector<string>& columns, MYSQL_ROW& row);