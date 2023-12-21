#include "aws_model.h"
#include "csv_parser.h"
#include <algorithm>
#include <string>
#include <utility>
#include <vector>

using namespace std;

vector<vector<vector<double>>>
generate_list(vector<double> values, int t, int num_instances, int num_markets);

void generate_result_cost(double total_cost,
                          vector<vector<vector<double>>> values, int t,
                          vector<string> instance_names,
                          vector<string> market_names,
                          vector<double> on_demand_data,
                          int savings_plan_duration);
void generate_total_purchases_savings_plan(
    vector<vector<vector<double>>> values, vector<int> hour_index);

void generate_total_purchases(vector<vector<vector<double>>> values,
                              vector<int> hour_index,
                              vector<string> instance_names,
                              vector<string> market_names);
int main() {
  // read CSVs
  auto on_demand_config = read_csv("./data/on_demand_config.csv");
  auto savings_plan_config = read_csv("./data/savings_plan_config.csv");
  auto raw_demand = read_csv("./data/total_demand.csv");

  // TODO: validate data

  vector<string> instances = get_column(on_demand_config, "instance");
  sort(instances.begin(), instances.end());

  // transforming input data
  vector<double> savings_plan_data;
  vector<double> on_demand_data;
  vector<vector<double>> total_demand;
  vector<string> market_names;

  for (string instance : instances) {
    string savings_plan_hourly_price =
        get_value_by_unique_ref(savings_plan_config, instance, "hourly_price");
    savings_plan_data.push_back(stod(savings_plan_hourly_price));

    market_names = {"on_demand"};

    on_demand_data.push_back(stod(
        get_value_by_unique_ref(on_demand_config, instance, "hourly_price")));

    vector<double> instance_demand =
        to_double(get_column(raw_demand, instance));
    total_demand.push_back(instance_demand);
  }

  int t = total_demand[0].size();
  int savings_plan_duration =
      stoi(get_value_by_index(savings_plan_config, 0, "duration"));

  pair<double, vector<double>> result =
      optimize_model(t, total_demand, on_demand_data, savings_plan_data,
                     savings_plan_duration);

  double total_cost = result.first;
  auto values =
      generate_list(result.second, t, instances.size(), market_names.size());

  // generating output files
  generate_result_cost(total_cost, values, t, instances, market_names,
                       on_demand_data, savings_plan_duration);

  vector<int> hour_index = to_int(get_column(raw_demand, "hour"));

  generate_total_purchases_savings_plan(values, hour_index);
  generate_total_purchases(values, hour_index, instances, market_names);

  return 0;
}

vector<vector<vector<double>>> generate_list(vector<double> values, int t,
                                             int num_instances,
                                             int num_markets) {
  int index = 0;
  vector<vector<vector<double>>> result;

  for (int _ = 0; _ < t; ++_) {
    vector<vector<double>> list_time;
    list_time.push_back({values[index], values[index + 1]});
    index += 2;
    for (int _ = 0; _ < num_instances; ++_) {
      // number of active instances for savings plan and OD
      list_time.push_back({values[index], values[index + 1]});
      index += 2;
    }
    result.push_back(list_time);
  }

  return result;
}

void generate_result_cost(double total_cost,
                          vector<vector<vector<double>>> values, int t,
                          vector<string> instance_names,
                          vector<string> market_names,
                          vector<double> on_demand_data,
                          int savings_plan_duration) {
  vector<vector<string>> result_cost = {{"instance", "total_cost"},
                                        {"all", to_string(total_cost)}};
  double savings_plan_cost = 0.0;

  for (int i_time = 0; i_time < t; ++i_time) {
    // value of savings plan reserves made * savings plan duration
    savings_plan_cost += values[i_time][0][1] * savings_plan_duration;
  }

  result_cost.push_back({"savings_plan", to_string(savings_plan_cost)});

  for (int i_instance = 0; i_instance < instance_names.size(); ++i_instance) {
    double instance_cost = 0;

    for (int _ = 0; _ < market_names.size(); ++_) {
      for (int i_time = 0; i_time < t; ++i_time) {
        double on_demand_price = on_demand_data[i_instance];
        double active = values[i_time][i_instance + 1][1];
        instance_cost += active * on_demand_price;
      }
    }

    result_cost.push_back(
        {instance_names[i_instance], to_string(instance_cost)});
  }

  matrix_to_csv(result_cost, "result_cost.csv");
}

void generate_total_purchases_savings_plan(
    vector<vector<vector<double>>> values, vector<int> hour_index) {
  vector<vector<string>> total_purchases_savings_plan = {
      {"hour", "market", "value_active", "value_reserves"}};

  for (int i_time = 0; i_time < hour_index.size(); ++i_time) {
    vector<double> values_savings_plan = values[i_time][0];
    vector<string> line = {to_string(hour_index[i_time]), "savings_plan",
                           to_string(values_savings_plan[0]),
                           to_string(values_savings_plan[1])};
    total_purchases_savings_plan.push_back(line);
  }

  matrix_to_csv(total_purchases_savings_plan,
                "total_purchases_savings_plan.csv");
}

void generate_total_purchases(vector<vector<vector<double>>> values,
                              vector<int> hour_index,
                              vector<string> instance_names,
                              vector<string> market_names) {
  for (int i_instance = 0; i_instance < instance_names.size(); ++i_instance) {
    vector<vector<string>> total_purchases = {
        {"hour", "instance_type", "market", "count_active", "count_reserves"}};
    string instance_name = instance_names[i_instance];

    // savings plan
    for (int i_time = 0; i_time < hour_index.size(); ++i_time) {
      double active = values[i_time][i_instance + 1][0];
      vector<string> line = {to_string(hour_index[i_time]), instance_name,
                             "savings_plan", to_string(active), 0};
      total_purchases.push_back(line);
    }

    // on demand
    for (int i_time = 0; i_time < hour_index.size(); ++i_time) {
      double active = values[i_time][i_instance + 1][1];
      vector<string> line = {to_string(hour_index[i_time]), instance_name,
                             "on_demand", to_string(active), to_string(active)};
      total_purchases.push_back(line);
    }

    matrix_to_csv(total_purchases, "total_purchases_" + instance_name + ".csv");
  }
}
