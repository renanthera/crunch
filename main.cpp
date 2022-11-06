#include <iostream>
#include <typeinfo>

#include "LinkedList.hpp"
#include "LoadData.cpp"

int main() {
  int length = 10;

  int*  one = new int(0);
  char* two = new char('a');
  LinkedList::List* list = new LinkedList::List(0, one);
  for (int i = 1; i < length; i++) {
    if (i % 2 == 0) {
      int* d = new int(i);
      list->appendNode(types::misc_t::int_t, d);
    };
    if (i % 2 == 1) {
      char* d = new char(*two+i);
      list->appendNode(types::misc_t::char_t, d);
    };
  };

  // LinkedList::printList(list, length);

  list->resetIterator();
  list->nextNode();
  list->nextNode();
  list->nextNode();
  list->swapConsecutiveNodes(list->iterator);
  list->resetIterator();
  // LinkedList::printList(list, length);
  LinkedList::List* index = LoadData::readFile("cache/index.json");
};
