#include <iostream>
#include <typeinfo>

#include "LinkedList.hpp"
// #include "LoadData.cpp"
// #include "temp.cpp"

using namespace LinkedList;

int main() {
  int length = 10;

  manipulator<int> func_i = doSomething<int>;
  manipulator<char> func_c = doSomething<char>;
  manipulator<int> funcn_i = doNothing<int>;
  manipulator<char> funcn_c = doNothing<char>;

  int*  one = new int(0);
  char* two = new char('a');
  List* list = new List(0, one);
  for (int i = 1; i < length; i++) {
    if (i % 2 == 0) {
      int t = 0;
      int* d = new int(i);
      list->appendNode(t, d);
    };
    if (i % 2 == 1) {
      int t = 1;
      char* d = new char(*two+i);
      list->appendNode(t, d);
    };
  };

  for (int i = 0; i < length; i++) {
    switch (list->iterator->t) {
      case 0: {
        Node<int>* temp = read(list->iterator, funcn_i);
        std::cout << i << ' ' << temp->t << ' ' << *temp->data << ' ' << list->iterator << std::endl;
        break;
      };
      case 1: {
        Node<char>* temp = read(list->iterator, funcn_c);
        std::cout << i << ' ' << temp->t << ' ' << *temp->data << ' ' << list->iterator << std::endl;
        break;
      };
    };
    list->nextNode();
  };
  // readFile("cache/index.json");
};
