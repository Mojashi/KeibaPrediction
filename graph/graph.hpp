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
#include "sql.hpp"
using namespace std;

struct Edge{
    int src,to;
    float diff;
    float rcsum = 0;
    int date;
};
typedef vector<vector<Edge>> Graph;
extern float INDIRECT_COEFF, MIRROR_COEFF , CENTER_COEFF, WEIGHT_BOUND;
extern float hangen, pace;
extern float MAX_LATE;
extern float RETURN_BOUND;
extern float sitCoeffAr[3][5000];

extern const int MAX_NUMHORSE;
extern const int DAY_SEC;
Graph extractGraph(const Graph& g, const vector<int>& vs, int baseday);
bool connected(const Graph& g);

vector<int> rankByFeedbackArc(const Graph&);
vector<int> rankByGreed(const Graph&);
vector<int> rankByDeg(const Graph&);

float sitCoeff(const Race& ra);
int edCou(const Graph& g);
Edge makeEdge(const Race& race, const Result& a, int aid, const Result& b, int bid);
void makeEdge(Graph& g, const Race& race, vector<Result>& ress,const map<string,int>& horses);
// void predict(const Graph& g, const vector<int> attends);
void showGraph(const Graph& g, string fname, const map<int, string>& names);