#include <fstream>
#include <string>

#include "LinkedList.hpp"

namespace LoadData {
  using namespace LinkedList;

  int readFile(std::string filename) {
    std::ifstream myfile;
    std::string line;
    myfile.open(filename);
    if (myfile.is_open()) {
      while (std::getline(myfile, line)) {
        std::cout << line << std::endl;
      }
      myfile.close();
      return 0;
    }
    return 1;
  };
};
