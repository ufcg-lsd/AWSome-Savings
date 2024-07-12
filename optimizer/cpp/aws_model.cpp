#include <memory>
#include <ortools/linear_solver/linear_solver.h>

using namespace std;
using namespace operations_research;

template <typename T>
vector<T> multiply_vector(vector<T> &input_vector, int multiplier) {
  if (multiplier < 1 || input_vector.empty()) {
    return vector<T>();
  }

  vector<T> final_vector;
  final_vector.reserve(input_vector.size() * multiplier);

  for (int i = 0; i < multiplier; ++i) {
    final_vector.insert(final_vector.end(), input_vector.begin(),
                        input_vector.end());
  }
  return final_vector;
}

vector<vector<vector<double>>> create_coefficients_base(int t,
                                                        int num_instances) {
  auto coefficients = vector<vector<vector<double>>>();
  for (int _ = 0; _ < t; ++_) {
    vector<vector<double>> time_coef = {
        {0, 0}}; // savings plan coefficients (0 * s_t + 1 * rs_t)
    for (int _ = 0; _ < num_instances; ++_) {
      // number of active instances for savings plan and OD
      vector<double> instance_coef = {0, 0};
      time_coef.push_back(instance_coef);
    }
    coefficients.push_back(time_coef);
  }
  return coefficients;
}

vector<double> generate_array(vector<vector<vector<double>>> coefficients) {
  vector<double> result;
  for (auto time : coefficients) {
    for (auto instance : time) {
      for (auto value : instance) {
        result.push_back(value);
      }
    }
  }
  return result;
}

int get_index(int num_vars, int t, int i_time, int i_instance, int i_value) {
  int result = (i_time * (num_vars / t) + i_instance * 2 + i_value);
  return result;
}

void constraint1(MPSolver *solver, unordered_map<int, MPVariable *> x,
                 int num_vars, vector<vector<double>> demand, int t,
                 int num_instances) {
  for (int i_time = 0; i_time < t; ++i_time) {
    for (int i_instance = 1; i_instance <= num_instances; ++i_instance) {
      int i1 = get_index(num_vars, t, i_time, i_instance, 0);
      int i2 = get_index(num_vars, t, i_time, i_instance, 1);

      // set the interval for the constraint
      MPConstraint *c1 = solver->MakeRowConstraint(
          demand[i_instance - 1][i_time], solver->infinity());

      for (int i = 0; i < num_vars; ++i) {
        c1->SetCoefficient(x[i], 0);
      }

      c1->SetCoefficient(x[i1], 1);
      c1->SetCoefficient(x[i2], 1);
    }
  }
}

void constraint3(MPSolver *solver, unordered_map<int, MPVariable *> x,
                 int num_vars, int t, int num_instances,
                 vector<double> savings_plan_data) {
  for (int i_time = 0; i_time < t; ++i_time) {
    vector<double> coefficients;
    coefficients.resize(num_vars, 0.0);

    coefficients[get_index(num_vars, t, i_time, 0, 0)] = -1;
    coefficients[get_index(num_vars, t, i_time, 0, 1)] = 0;

    // for (int i_instance = 1; i_instance < coefficients[i_time].size();
    // ++i_instance) {
    for (int i_instance = 1; i_instance <= num_instances; ++i_instance) {
      // coefficients[i_time][i_instance][0] = savings_plan_data[i_instance -
      // 1];
      coefficients[get_index(num_vars, t, i_time, i_instance, 0)] =
          savings_plan_data[i_instance - 1];
    }

    // generate vector<int> from the coefficients
    // vector<double> constraint_expr = generate_array(coefficients);

    // set the interval for the constraint
    MPConstraint *c3 = solver->MakeRowConstraint(-solver->infinity(), 0.0);

    // add the sum of the linear expressions in constraint_expr
    for (int i = 0; i < num_vars; ++i) {
      // c3->SetCoefficient(x[i], constraint_expr[i]);
      c3->SetCoefficient(x[i], coefficients[i]);
    }
  }
}

void constraint4(MPSolver *solver, unordered_map<int, MPVariable *> x,
                 int num_vars, int t, int num_instances,
                 int savings_plan_duration) {
  for (int i_time = 0; i_time < t; ++i_time) {
    // auto coefficients = create_coefficients_base(t, num_instances);
    vector<double> coefficients;
    coefficients.resize(num_vars, 0.0);

    // coefficients[i_time][0] = {1, -1};
    coefficients[get_index(num_vars, t, i_time, 0, 0)] = 1;
    coefficients[get_index(num_vars, t, i_time, 0, 1)] = -1;

    int reserve_duration = savings_plan_duration - 1;

    for (int i = i_time - 1; i >= 0; --i) {
      if (reserve_duration > 0) {
        // coefficients[i][0] = {0, -1};
        coefficients[get_index(num_vars, t, i, 0, 0)] = 0;
        coefficients[get_index(num_vars, t, i, 0, 1)] = -1;
        reserve_duration--;
      } else {
        break;
      }
    }

    // generate vector<int> from the coefficients
    // vector<double> constraint_expr = generate_array(coefficients);

    // set the interval for the constraint
    MPConstraint *c4 = solver->MakeRowConstraint(0.0, 0.0);

    // add the sum of the linear expressions in constraint_expr
    for (int i = 0; i < num_vars; ++i) {
      c4->SetCoefficient(x[i], coefficients[i]);
    }
  }
}

pair<double, vector<double>> optimize_model(int t,
                                            vector<vector<double>> demand,
                                            vector<double> on_demand_data,
                                            vector<double> savings_plan_data,
                                            int savings_plan_duration) {
  unique_ptr<MPSolver> solver(MPSolver::CreateSolver("GLOP"));
  if (!solver) {
    LOG(WARNING) << "GLOP solver unavailable.";
    throw runtime_error("GLOP solver unavaliable");
  }

  const double infinity = solver->infinity();
  int num_instances = on_demand_data.size();
  int num_vars = (2 * num_instances + 2) * t;
  unordered_map<int, MPVariable *> x;

  for (int j = 0; j < num_vars; ++j) {
    x[j] = solver->MakeIntVar(0.0, infinity, "x[" + to_string(j) + "]");
  }
  LOG(INFO) << "Number of variables = " << solver->NumVariables();

  // adding constraints
  LOG(INFO) << "Generating constraint 1";
  constraint1(solver.get(), x, num_vars, demand, t, num_instances);
  LOG(INFO) << "Generating constraint 3 (constraint 2 was removed)";
  constraint3(solver.get(), x, num_vars, t, num_instances, savings_plan_data);
  LOG(INFO) << "Generating constraint 4";
  constraint4(solver.get(), x, num_vars, t, num_instances,
              savings_plan_duration);

  // creating objective function
  LOG(INFO) << "Generating objective function";
  vector<double> obj_func = {0.0, 1.0 * savings_plan_duration};

  for (double instance : on_demand_data) {
    double on_demand_price = instance;
    obj_func.push_back(
        0); // coeff of number of active instances in SP (a_t, i, SP)
    obj_func.push_back(on_demand_price); // a_t, i, OD * on-demand hourly price
  }

  // repeat obj_func vector t times
  // ex: multiply_vector({1, 2}, 3) = {1, 2, 1, 2, 1, 2}
  obj_func = multiply_vector(obj_func, t);

  MPObjective *const objective = solver->MutableObjective();

  for (int j = 0; j < num_vars; ++j) {
    objective->SetCoefficient(x[j], obj_func[j]);
  }

  objective->SetMinimization();

  LOG(INFO) << "Starting optimization";
  const MPSolver::ResultStatus status = solver->Solve();
  LOG(INFO) << "End of optimization";

  if (status == MPSolver::OPTIMAL) {
    double total_value = objective->Value();

    LOG(INFO) << "Objective value = " << total_value;
    LOG(INFO) << "Problem solved in " << solver->wall_time()
              << " millisseconds";
    LOG(INFO) << "Problem solved in " << solver->iterations() << " iterations";
    LOG(INFO) << "Problem solved in " << solver->nodes()
              << " branch-and-bound nodes";

    vector<double> values = vector<double>();

    for (int j = 0; j < num_vars; ++j) {
      values.push_back(x[j]->solution_value());
    }

    return make_pair(total_value, values);
  }

  LOG(FATAL) << "The problem does not have an optimal solution";
}
