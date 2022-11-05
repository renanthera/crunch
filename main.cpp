#include <iostream>
#include <typeinfo>
#include <any>

#include "LinkedList.hpp"
#include "LoadData.cpp"
#include "temp.cpp"

using namespace LinkedList;

int main() {
  int*  one = new int(7);
  char* two = new char('c');
  // Base<Node, int>* obj = Base<Node, int>::constructor(0, one);
  // int type = 0;
  // Node<int>* n = new Node(type, init);
  // std::cout << typeid(n).name() << ' ' << *n->data << std::endl;
  // List* list = new List(type, init);
  // std::cout << typeid(list).name() << ' ' << typeid(list->iterator).name() << std::endl;
  // std::cout << typeid(static_cast<Node<int>*>(list->iterator)).name() << std::endl;
  // std::cout << typeid(cast(list->iterator)).name() << std::endl;
  // Node<int>* temp = list->iterator->castNode();
  // std::cout << typeid(list->iterator->castNode()).name() << std::endl;
  // for (int k = 1; k < 10; k++) {
  //   int* b = new int(k);
  //   list->appendNode(type);
  //   list->tail->addData<int>(b);
  //   list->nextNode();
    // if (k % 2 == 0) {
    //   Data<int>* d = new Data<int>(k);
    //   list->appendNode(d);
    // }
    // if (k % 2 == 1) {
    //   Data<int>* d = new Data<int>(k);
    //   list->appendNode(d);
    // }
  // };

  // while (list->iterator) {
  //   // std::cout << list->iterator->t << ' ' << list->iterator->returnData().type() << std::endl;
  //   std::cout << list->iterator->t << ' ' << std::endl;
  //   list->iterator = list->iterator->next;
  // }

  // // if you want to change event payload type:
  // // these two lines change
  // char p = 'a';
  // List<char>* list = new List<char>(&p);
  // for (int i = 1; i < 10; i++) {
  //   // this line changes
  //   char* k = new char('a'+i);
  //   list->iterator = list->addNode(list->iterator, k);
  // };
  // list->resetIterator();
  // int j = 0;
  // while (list->iterator) {
  //   std::cout << j << ' ' << *list->iterator->data << ' ' << list->iterator->next << std::endl;
  //   list->iterator = list->iterator->next;
  //   j++;
  // };
  // list->resetIterator();

  // std::cout << std::endl;
  // for (int i = 1; i < 4; i++) {
  //   list->iterator = list->iterator->next;
  // };
  // std::cout << *list->iterator->data << std::endl;
  // list->swapConsecutiveNodes(list->iterator);
  // list->resetIterator();
  // j = 0;
  // while (list->iterator) {
  //   std::cout << j << ' ' << *list->iterator->data << ' ' << list->iterator->next << std::endl;
  //   list->iterator = list->iterator->next;
  //   j++;
  // };
  // readFile("cache/index.json");
};
