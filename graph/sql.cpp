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
#include "sql.hpp"
#include "graph.hpp"
using namespace std;

// float sitCoeffAr[3][5000] = {};

Proc::Proc()
{
    // Initialize constants
    MY_HOSTNAME = "localhost";
    MY_DATABASE = "keiba";
    MY_USERNAME = "keiba";
    MY_PASSWORD = "";
    MY_SOCKET   = NULL;

    // Format a MySQL object
    conn = mysql_init(NULL);
    mysql_options(conn, MYSQL_SET_CHARSET_NAME, "utf8mb4");
    // Establish a MySQL connection
    if (!mysql_real_connect(
            conn,
            MY_HOSTNAME, MY_USERNAME,
            MY_PASSWORD, MY_DATABASE,
            MY_PORT_NO, MY_SOCKET, MY_OPT)) {
        cerr << mysql_error(conn) << endl;
        return;
    }
}

Proc::~Proc(){
    mysql_close(conn);
}

MYSQL_RES* Proc::query(string str){
   if (mysql_query(conn, str.c_str())) {
        cerr << mysql_error(conn) << endl;
        exit(1);
    }
    // Get a result set
    return mysql_use_result(conn);
}

std::string join(const std::vector<std::string>& v, const char* delim = 0) {
  std::string s;
  if (!v.empty()) {
    s += v[0];
    for (decltype(v.size()) i = 1, c = v.size(); i < c; ++i) {
      if (delim) s += delim;
      s += v[i];
    }
  }
  return s;
}

void scanSitCoeff(Proc& proc){
    MYSQL_ROW row;
    MYSQL_RES *res;
    res = proc.query("select field,length,8.2512/avg(r2.time-r1.time) from result r1 join result r2 on r1.race_id=r2.race_id join race rc on rc.id=r1.race_id where r1.rank=1 and r2.rank=4 group by rc.length,rc.field");
    while ((row = mysql_fetch_row(res)) != NULL){
        int fi = -1;
        if(string(row[0]) == "ダ") fi = 0;
        else if(string(row[0]) == "芝") fi = 1;
        else if(string(row[0]) == "障") fi = 2;
        sitCoeffAr[fi][atoi(row[1])] = atof(row[2]);
    }
    mysql_free_result(res);
}

map<string,int> scanHorses(Proc& proc){
    map<string,int> horses;
    MYSQL_ROW row;
    MYSQL_RES *res;
    res = proc.query("SELECT distinct(name) from result order by name");
    while ((row = mysql_fetch_row(res)) != NULL){
        int cou = horses.size();
        if(horses.count(row[0]) == 0)
            horses[row[0]] = cou;
    }
    mysql_free_result(res);
    cerr << horses.size() << " horses" << endl;
    return horses;
}
Result parseResult(vector<string>& columns, MYSQL_ROW& row){
    Result res;
    for(int i = 0; columns.size() > i; i++){
        if(columns[i] == "name") res.name = row[i];
        else if(columns[i] == "race_id") res.race_id = atoi(row[i]);
        else if(columns[i] == "time") res.time = atof(row[i]);
        else if(columns[i] == "rank") res.rank = atoi(row[i]);
        else if(columns[i] == "id") res.id = atoi(row[i]);
        else if(columns[i] == "single_return") res.single_return = atof(row[i]);
    }
    return res;
}

Race parseRace(vector<string>& columns, MYSQL_ROW& row){
    Race res;
    for(int i = 0; columns.size() > i; i++){
        if(columns[i] == "id") res.id = atoi(row[i]);
        else if(columns[i] == "single_odds") res.single_odds = atoi(row[i]);
        else if(columns[i] == "rentan_odds") res.rentan_odds = atoi(row[i]);
        else if(columns[i] == "renpuku_odds")res.renpuku_odds = atoi(row[i]);
        else if(columns[i] == "umatan_odds") res.umatan_odds = atoi(row[i]);
        else if(columns[i] == "umaren_odds") res.umaren_odds = atoi(row[i]);
        else if(columns[i] == "length") res.length = atoi(row[i]);
        else if(columns[i] == "field") res.field = row[i];
        else if(columns[i] == "date") {
            stringstream ss(row[i]);
            tm buf;
            ss >> get_time(&buf, "%Y-%m-%d %H:%M:%S");
            res.date = mktime(&buf);
        }
    }
    return res;
}