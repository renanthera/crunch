#include <fstream>
#include <string>

// int readFile(std::string filename) {
//   std::ifstream myfile;
//   std::string line;
//   myfile.open(filename);
//   if (myfile.is_open()) {
//     while (std::getline(myfile, line)) {
//       std::cout << line << std::endl;
//     }
//     myfile.close();
//     return 0;
//   }
//   return 1;
// };

std::ifstream* openFile(std::string filename) {
  std::ifstream* filehandle = new std::ifstream();
  filehandle->open(filename);
  if (filehandle->is_open()) {
    return filehandle;
  }
  return 0;
};

std::string* fileHandler(std::ifstream* filehandle_ptr, std::string* line_ptr) {
  std::cout << "here4" << std::endl;
  if (std::getline(*filehandle_ptr, *line_ptr)) {
    std::cout << "here3" << std::endl;
    return line_ptr;
  }
  std::cout << "here2" << std::endl;
  filehandle_ptr->close();
  return 0;
};

int readFile(std::string filename) {
  std::ifstream* filehandle = openFile(filename);
  std::string* line;
  std::cout << "here" << std::endl;
  while (fileHandler(filehandle, line)) {
    std::cout << *line << std::endl;
  }
  std::cout << "here100" << std::endl;
  return 0;
};
