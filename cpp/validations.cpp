#include "csv_parser.h"
#include <algorithm>
#include <iostream>
#include <set>
#include <string>
#include <vector>

using namespace std;

void validate_columns(vector<vector<string>> dataframe, vector<string> names,
                      string file_name) {
  if (dataframe[0] != names) {
    cerr << "The column names in " << file_name << " are incorrect.";
  }
}

void validate_on_demand_instances(vector<vector<string>> on_demand_config) {
  vector<string> instances = get_column(on_demand_config, "instance");
  set<string> unique_strings;

  for (string inst : instances) {
    if (!unique_strings.insert(inst).second) {
      cerr << "The instances names in on_demand_config should be unique";
    }
  }
}

void validate_on_demand_config(vector<vector<string>> on_demand_config) {
  validate_columns(on_demand_config, {"instance", "hourly_price"},
                   "on_demand_config");
  validate_on_demand_instances(on_demand_config);
}

void validate_instances_names(vector<vector<string>> dataframe,
                              vector<string> instances, string file_name) {
  vector<string> file_instances = get_column(dataframe, "instance");

  sort(file_instances.begin(), file_instances.end());
  sort(instances.begin(), instances.end());

  if (file_instances != instances) {
    cerr << "The instance names in on_demand_config and " << file_name
         << " are not the same.";
  }
}

void validate_savings_plan_durations(
    vector<vector<string>> savings_plan_config) {
  vector<string> savings_plan_durations =
      get_column(savings_plan_config, "duration");
  set<string> unique_elements;

  for (string duration : savings_plan_durations) {
    unique_elements.insert(duration);

    if (unique_elements.size() > 1) {
      cerr << "All instances must have the same savings plan duration";
    }
  }
}

void validate_savings_plan_config(vector<vector<string>> savings_plan_config,
                                  vector<string> instances) {
  validate_columns(savings_plan_config,
                   {"instance", "hourly_price", "duration"},
                   "savings_plan_config");
  validate_instances_names(savings_plan_config, instances,
                           "savings_plan_config");
  validate_savings_plan_durations(savings_plan_config);
}

void validate_demand_instances(vector<vector<string>> raw_demand,
                               vector<string> instances) {
  vector<string> demand_col = raw_demand[0];

  for (string instance : instances) {
    if (find(demand_col.begin(), demand_col.end(), instance) ==
        demand_col.end()) {
      cerr << "The instance " << instance << " is not on the demand file.";
    }
  }
}

void validate_demand(vector<vector<string>> raw_demand,
                     vector<string> instances) {
  if (raw_demand[0][0] != "hour") {
    cerr << "The first column name in the demand file is incorrect.";
  }

  validate_demand_instances(raw_demand, instances);
}
