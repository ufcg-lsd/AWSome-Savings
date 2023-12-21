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

vector<vector<vector<int>>> create_coefficients_base(int t, int num_instances) {
  auto coefficients = vector<vector<vector<int>>>();
  for (int _ = 0; _ < t; ++_) {
    vector<vector<int>> time_coef = {
        {0, 0}}; // savings plan coefficients (0 * s_t + 1 * rs_t)
    for (int _ = 0; _ < num_instances; ++_) {
      // number of active instances for savings plan and OD
      vector<int> instance_coef = {0, 0};
      time_coef.push_back(instance_coef);
    }
    coefficients.push_back(time_coef);
  }
  return coefficients;
}

vector<int> generate_array(vector<vector<vector<int>>> coefficients) {
  vector<int> result;
  for (auto time : coefficients) {
    for (auto instance : time) {
      for (auto value : instance) {
        result.push_back(value);
      }
    }
  }
  return result;
}

void constraint1(MPSolver *solver, unordered_map<int, MPVariable *> x,
                 int num_vars, vector<vector<double>> demand, int t,
                 int num_instances) {
  for (int i_time = 0; i_time < t; ++i_time) {
    for (int i_instance = 1; i_instance <= num_instances; ++i_instance) {
      auto coefficients = create_coefficients_base(t, num_instances);
      coefficients[i_time][i_instance] = {1, 1}; // 1 * a_t,i,SP e 1 * a_t,i,OD
                                                 //
      // generate vector<int> from the coefficients
      vector<int> constraint_expr = generate_array(coefficients);

      // set the interval for the constraint
      MPConstraint *c1 = solver->MakeRowConstraint(
          demand[i_instance - 1][i_time], solver->infinity());

      // add the sum of the linear expressions in constraint_expr
      for (int i = 0; i < num_vars; ++i) {
        c1->SetCoefficient(x[i], constraint_expr[i]);
      }
    }
  }
}

void constraint3(MPSolver *solver, unordered_map<int, MPVariable *> x,
                 int num_vars, int t, int num_instances,
                 vector<double> savings_plan_data) {
  for (int i_time = 0; i_time < t; ++i_time) {
    auto coefficients = create_coefficients_base(t, num_instances);

    coefficients[i_time][0] = {-1, 0};

    for (int i_instance = 1; i_instance <= coefficients[i_time].size();
         ++i_instance) {
      coefficients[i_time][i_instance][0] = savings_plan_data[i_instance - 1];
    }

    // generate vector<int> from the coefficients
    vector<int> constraint_expr = generate_array(coefficients);

    // set the interval for the constraint
    MPConstraint *c3 = solver->MakeRowConstraint(-solver->infinity(), 0.0);

    // add the sum of the linear expressions in constraint_expr
    for (int i = 0; i < num_vars; ++i) {
      c3->SetCoefficient(x[i], constraint_expr[i]);
    }
  }
}

void constraint4(MPSolver *solver, unordered_map<int, MPVariable *> x,
                 int num_vars, int t, int num_instances,
                 int savings_plan_duration) {
  for (int i_time = 0; i_time < t; ++i_time) {
    auto coefficients = create_coefficients_base(t, num_instances);

    coefficients[i_time][0] = {1, -1};

    int reserve_duration = savings_plan_duration - 1;

    for (int i = i_time - 1; i >= 0; --i) {
      if (reserve_duration > 0) {
        coefficients[i][0] = {0, -1};
        reserve_duration--;
      } else {
        break;
      }
    }

    // generate vector<int> from the coefficients
    vector<int> constraint_expr = generate_array(coefficients);

    // set the interval for the constraint
    MPConstraint *c4 = solver->MakeRowConstraint(0.0, 0.0);

    // add the sum of the linear expressions in constraint_expr
    for (int i = 0; i < num_vars; ++i) {
      c4->SetCoefficient(x[i], constraint_expr[i]);
    }
  }
}

pair<double, vector<double>> optimize_model(int t,
                                            vector<vector<double>> demand,
                                            vector<double> on_demand_data,
                                            vector<double> savings_plan_data,
                                            int savings_plan_duration) {
  unique_ptr<MPSolver> solver(MPSolver::CreateSolver("SCIP"));
  if (!solver) {
    LOG(WARNING) << "SCIP solver unavailable.";
    throw runtime_error("SCIP solver unavaliable");
  }

  const double infinity = solver->infinity();
  int num_instances = on_demand_data.size();
  int num_vars = (2 * num_instances + 2) * t;
  unordered_map<int, MPVariable *> x;

  for (int j = 0; j < num_vars; ++j) {
    x[j] = solver->MakeIntVar(0.0, infinity, "x[" + to_string(j) + "]");
  }

  // adding constraints
  constraint1(solver.get(), x, num_vars, demand, t, num_instances);
  constraint3(solver.get(), x, num_vars, t, num_instances, savings_plan_data);
  constraint4(solver.get(), x, num_vars, t, num_instances,
              savings_plan_duration);

  // creating objective function
  vector<int> obj_func = {0, 1 * savings_plan_duration};

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

  const MPSolver::ResultStatus status = solver->Solve();

  if (status == MPSolver::OPTIMAL) {
    vector<double> values = vector<double>();

    for (int j = 0; j < num_vars; ++j) {
      values.push_back(x[j]->solution_value());
    }

    return make_pair(objective->Value(), values);
  }

  throw runtime_error("The problem does not have an optimal solution");
}
