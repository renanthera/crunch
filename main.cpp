#include <iostream>

#include "LinkedList.hpp"
#include "temp.cpp"

using namespace LinkedList;

int main() {
  // if you want to change event payload type:
  // these two lines change
  char p = 'a';
  List<char>* list = new List<char>(&p);
  for (int i = 1; i < 10; i++) {
    // this line changes
    char* k = new char('a'+i);
    list->iterator = list->addNode(list->iterator, k);
  };
  list->resetIterator();
  int j = 0;
  while (list->iterator) {
    std::cout << j << ' ' << *list->iterator->event << ' ' << list->iterator->next << std::endl;
    list->iterator = list->iterator->next;
    j++;
  };
  list->resetIterator();

  std::cout << std::endl;
  for (int i = 1; i < 4; i++) {
    list->iterator = list->iterator->next;
  };
  std::cout << *list->iterator->event << std::endl;
  list->swapConsecutiveNodes(list->iterator);
  list->resetIterator();
  j = 0;
  while (list->iterator) {
    std::cout << j << ' ' << *list->iterator->event << ' ' << list->iterator->next << std::endl;
    list->iterator = list->iterator->next;
    j++;
  };
};
