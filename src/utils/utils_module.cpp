#include <stdio.h>
#include <math.h>
#include "utils_module.h"

std::string path_to_js(std::vector< std::vector< std::vector<float> > > path){
  char buf[50];
  std::string c_string("[");
  for (size_t layer = 0; layer < path.size(); layer += 1){
    c_string += "[";
      for (size_t point = 0; point < path[layer].size(); point += 1){
        // sprintf(buf, "[%g,%g,%g,%d]", path[layer][point][0], path[layer][point][1], path[layer][point][2], (int)path[layer][point][3]);
        sprintf(buf, "[%.2f,%.2f,%.2f,%d]", path[layer][point][0], path[layer][point][1], path[layer][point][2], (int)path[layer][point][3]);
        c_string += buf;
        c_string += ",";
      }
      c_string.erase(c_string.end() - 1);
    c_string += "],";
  }
  c_string.erase(c_string.end() - 1);
  c_string += "]";
  return c_string;
}
