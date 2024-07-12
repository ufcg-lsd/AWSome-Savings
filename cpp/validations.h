#include <string>
#include <vector>

using namespace std;

void validate_on_demand_config(vector<vector<string>> on_demand_config);
void validate_columns(vector<vector<string>> dataframe, vector<string> names,
                      string file_name);
void validate_on_demand_instances(vector<vector<string>> on_demand_config);
void validate_instances_names(vector<vector<string>> dataframe,
                              vector<string> names, string file_name);
void validate_savings_plan_config(vector<vector<string>> savings_plan_config,
                                  vector<string> instances);
void validate_savings_plan_durations(
    vector<vector<string>> savings_plan_config);
void validate_demand(vector<vector<string>> raw_demand,
                     vector<string> instances);
void validate_demand_instances(vector<vector<string>> raw_demand,
                               vector<string> instances);
