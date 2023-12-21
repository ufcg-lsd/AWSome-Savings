#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

using namespace std;

vector<string> get_line_by_instance(const vector<vector<string>> &data,
                                    const string instance) {
  int instance_col_index;
  for (int i = 0; i < data[0].size(); ++i) {
    if (data[0][i] == "instance") {
      instance_col_index = i;
      break;
    }
  }

  for (int i = 0; i < data.size(); ++i) {
    if (data[i][instance_col_index] == instance) {
      return data[i];
    }
  }

  return {};
}

string get_value_by_unique_ref(const vector<vector<string>> &data,
                               const string instance, const string value) {
  int value_col_index;
  for (int i = 0; i < data[0].size(); ++i) {
    if (data[0][i] == value) {
      value_col_index = i;
      break;
    }
  }

  vector<string> line = get_line_by_instance(data, instance);

  return line[value_col_index];
}

string get_value_by_index(const vector<vector<string>> &data, const int index,
                          const string value) {
  for (int i = 0; i < data[0].size(); ++i) {
    if (data[0][i] == value) {
      return data[index + 1][i];
    }
  }

  return "";
}

vector<vector<string>> read_csv(const string &file_name) {
  vector<vector<string>> data;

  ifstream file(file_name);
  if (!file.is_open()) {
    cerr << "Error opening file: " << file_name << endl;
    return data;
  }

  string line;
  while (getline(file, line)) {
    vector<string> row;
    istringstream iss(line);
    string value;

    while (getline(iss, value, ',')) {
      row.push_back(value);
    }

    data.push_back(row);
  }

  file.close();

  return data;
}

vector<string> get_column(const vector<vector<string>> data,
                          const string column) {
  int col_index;
  for (int i = 0; i < data[0].size(); ++i) {
    if (data[0][i] == column) {
      col_index = i;
      break;
    }
  }

  vector<string> column_values;
  for (int i = 1; i < data.size(); ++i) {
    string value = data[i][col_index];

    column_values.push_back(value);
  }

  return column_values;
}

vector<double> to_double(const vector<string> input_vector) {
  vector<double> result;
  for (string s : input_vector) {
    result.push_back(stod(s));
  }
  return result;
}

vector<int> to_int(const vector<string> input_vector) {
  vector<int> result;
  for (string s : input_vector) {
    result.push_back(stoi(s));
  }
  return result;
}

void matrix_to_csv(const vector<vector<string>> &matrix,
                   const string &filePath) {
  ofstream outputFile(filePath);

  if (!outputFile.is_open()) {
    cerr << "Error: Unable to open file " << filePath << " for writing."
         << endl;
    return;
  }

  for (const auto &row : matrix) {
    for (size_t i = 0; i < row.size(); ++i) {
      outputFile << row[i];

      if (i < row.size() - 1) {
        outputFile << ",";
      }
    }
    outputFile << "\n";
  }

  outputFile.close();
}
