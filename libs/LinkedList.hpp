#include <iostream>

#include "../Types.cpp"

namespace LinkedList {
  struct Base {
    const int type;
    Base* next;

    Base(const int type) : type{type} {};
    template <typename T>
    static Base* constructor(const int type, T* data);
  };

  template <typename T>
  struct Node : Base {
    T* data;

    Node(const int type, T* data) : Base(type) {
      this->data = data;
    };
  };

  template <typename T>
  Base* Base::constructor(const int type, T* data) {
    return new Node(type, data);
  };

  class List {
  public:
    Base* head;
    Base* tail;
    Base* iterator;
    int length;

    List(const int type, void* data) {
      this->head = Base::constructor(type, data);
      this->tail = this->head;
      this->iterator = this->head;
      this->length = 1;
    };

    void appendNode(const int type, void* data) {
      this->tail->next = Base::constructor(type, data);
      this->tail = this->tail->next;
      this->length++;
    };

    void nextNode() {
      this->iterator = this->iterator->next;
    };

    void swapConsecutiveNodes(Base* previous) {
      // a -> b -> c -> d => a -> c-> b -> d
      Base* b = previous->next;
      Base* d = b->next->next;
      previous->next = b->next;
      previous->next->next = b;
      b->next = d;
    };

    void resetIterator() {
      this->iterator = head;
    };
  };

  template <typename T>
  Node<T>* access(Base* node, Node<T>* (*funct_ptr)(Node<T>* node)) {
    return funct_ptr(static_cast<Node<T>*>(node));
  };

  template <typename T>
  using manipulator = Node<T>* (*)(Node<T>* node);

  template <typename T>
  Node<T>* doSomething(Node<T>* node) {
    *node->data = *node->data + 10;
    return node;
  };

  template <typename T>
  Node<T>* doNothing(Node<T>* node) {
    return node;
  };

  template <typename T>
  void printEntry(int index, Node<T>* node) {
    std::cout << index << ' ' << static_cast<int>(node->type) << ' ' << *node->data << ' ' << node << std::endl;
  };

  template <>
  void printEntry(int index, Node<types::Cache>* node) {
    std::cout << index << ' ';
    std::cout << node->data->reportCode << ' ';
    std::cout << node->data->startTime << ' ';
    std::cout << node->data->endTime << ' ';
    std::cout << node->data->actorID << ' ';
    std::cout << node->data->dataType << ' ';
    std::cout << node->data->abilityID << ' ';
    std::cout << node->data->path << ' ';
    std::cout << std::endl;
  };

  void printList(List* list) {
    manipulator<types::Cache> func_0 = doNothing;
    manipulator<int> func_1 = doNothing;
    manipulator<char> func_2 = doNothing;

    int n = list->length;
    for (int i = 0; i < n; i++) {
      switch (list->iterator->type) {
        case types::json_t::cache_t: {
          printEntry(i, access(list->iterator, func_0));
          break;
        }
        case types::misc_t::int_t: {
          printEntry(i, access(list->iterator, func_1));
          break;
        };
        case types::misc_t::char_t: {
          printEntry(i, access(list->iterator, func_2));
          break;
        };
      };
      list->nextNode();
    };
    list->resetIterator();
    std::cout << std::endl;
  };
};
