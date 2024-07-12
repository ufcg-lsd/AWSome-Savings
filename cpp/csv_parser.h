#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

using namespace std;

vector<vector<string>> read_csv(const string &file_name);
vector<string> get_column(const vector<vector<string>> data,
                          const string column);
vector<string> get_line_by_instance(const vector<vector<string>> &data,
                                    const string instance);
string get_value_by_unique_ref(const vector<vector<string>> &data,
                               const string instance, const string value);
string get_value_by_index(const vector<vector<string>> &data, const int index,
                          const string value);
vector<double> to_double(const vector<string> input_vector);
vector<int> to_int(const vector<string> input_vector);
void matrix_to_csv(const vector<vector<string>> &matrix,
                   const string &filePath);
