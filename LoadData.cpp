#include <fstream>
#include <string>
#include <typeinfo>

// #include "Types.cpp"

namespace LoadData {
  std::string stripWhitespace(std::string str) {
    int t = 0;
    for (int i = 0; i < str.length(); i++) {
      if (str[i] != ' ' && str[i] != '\t') {
        t = i;
        break;
      };
    };
    return str.erase(0, t);
  };

  std:: string extractToken(std::string str) {
    int t = 0;
    int u = 0;
    for (int i = 0; i < str.length(); i++) {
      if (str[i] != ' ' && str[i] != '\t' && t == 0) {
        t = i;
      };
      if (t != 0 && str[i] == ' ') {
        u = i;
      };
    };
    return str.substr(t, u-t);
  };

  std:: string extractValue(std::string str) {
    int t = 0;
    int u = 0;
    int v = str.length();
    for (int i = 0; i < str.length(); i++) {
      if (str[i] != ' ' && str[i] != '\t' && t == 0) {
        t = i;
      };
      if (t != 0 && str[i] == ' ') {
        u = i;
        break;
      };
    };
    if (str[u+1] == '"' || str[u] == ' ') u += 2;
    for (int i = str.length()-1; i > 0; i--) {
      if (str[i] != ',' && str[i] != '"') break;
      v--;
    };
    // std::cout << str << " => " << str.substr(u, v-u) << std::endl;
    return str.substr(u, v-u);
  };

  void processLine(std::string line, LinkedList::List* list, const int type) {
    std::string nowhitespace;
    std::string token;
    std::string value;
    LinkedList::manipulator<types::Cache> func_cache_t_w = LinkedList::doNothing;

    if (list == NULL) {
    };

    nowhitespace = stripWhitespace(line);
    if (nowhitespace == "[" || nowhitespace == "]") {
    } else if (nowhitespace == "{") {
      // std::cout << "START ENTRY" << std::endl;
      // this needs reworking into something more automated
      types::Cache* entry = new types::Cache;
      list->appendNode(types::json_t::cache_t, entry);
    } else if (nowhitespace == "}," || nowhitespace == "}") {
        // std::cout << "END ENTRY OF " << i << " LINES" << std::endl;
    } else {
      // std::cout << line << std::endl;
      // this needs reworking into something more automated
      token = extractToken(line);
      value = extractValue(line);

      // probably generate these. can probably also simultaneously generate types::* data too
      // oh holy shit i can just use the graphql data from wcl + some aliases for that. that'd be cool.
      if (token == "\"reportCode\":") {
        LinkedList::access(list->tail,func_cache_t_w)->data->reportCode = value;
      } else if (token == "\"startTime\":") {
        LinkedList::access(list->tail,func_cache_t_w)->data->startTime = stoi(value);
      } else if (token == "\"endTime\":") {
        LinkedList::access(list->tail,func_cache_t_w)->data->endTime = stoi(value);
      } else if (token == "\"id\":") {
        LinkedList::access(list->tail,func_cache_t_w)->data->actorID = stoi(value);
      } else if (token == "\"abilityID\":") {
        LinkedList::access(list->tail,func_cache_t_w)->data->abilityID = stoi(value);
      } else if (token == "\"dataType\":") {
        LinkedList::access(list->tail,func_cache_t_w)->data->dataType = value;
      } else if (token == "\"path\":") {
        LinkedList::access(list->tail,func_cache_t_w)->data->path = value;
      }
    }
  }

#define WRITELINE(t) if (token == "\"t\"")

  LinkedList::List* readFile(std::string filename) {
    std::ifstream myfile;
    std::string line;
    int i = 0;
    int ct = 0;
    // LinkedList::List* list = NULL;
    types::Cache* entry = new types::Cache;
    LinkedList::List* list = new LinkedList::List(types::json_t::cache_t, entry);

    myfile.open(filename);
    if (myfile.is_open()) {
      while (std::getline(myfile, line)) {
        processLine(line, list, types::json_t::cache_t);
        i++;
      }
      myfile.close();
    };
    printList(list);
    return list;
  };
};
