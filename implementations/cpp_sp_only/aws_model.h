#include <vector>

using namespace std;

pair<double, vector<double>> optimize_model(int t,
                                            vector<vector<double>> demand,
                                            vector<double> on_demand_data,
                                            vector<double> savings_plan_data,
                                            int savings_plan_duration);
