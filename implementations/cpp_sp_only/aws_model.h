#include <vector>
#include <filesystem>

using namespace std;
namespace fs = std::filesystem;

void build_constraints(int t, vector<vector<double>> demand,
                       vector<double> on_demand_data,
                       vector<double> savings_plan_data, 
                       int savings_plan_duration,
                       const fs::path& model_path);

pair<double, vector<double>> solve_model(const fs::path& model_path);

pair<double, vector<double>> optimize_model(int t,
                                            vector<vector<double>> demand,
                                            vector<double> on_demand_data,
                                            vector<double> savings_plan_data,
                                            int savings_plan_duration);
