// template <typename Data> struct Node;

#include <iostream>
#include <typeinfo>

namespace LinkedList {
  template <template <class> class Node, typename T>
  class Base {
  public:
    const int t;
    Base* next;
    Base(const int t) : t{t} {};
    virtual ~Base() = default;
    // static Base<Node, T>* constructor(const int t, T* data);
    T accessDerivedField() {
      Node<T>* derived = static_cast<Node<T>*>(this);
      return *derived->data;
    };
  };

  template <typename T>
  class Node : public Base<Node, T> {
  public:
    T* data;
    Node(const int t, T* data) : Base<Node,T>(t) {
      this->data = data;
    };
  };

  // struct Base {
  //   const int t;
  //   Base* next;
  //   Base(const int t) : t{t} {};
  //   template <typename T>
  //   static Base* constructor(const int t, T* data);
  //   virtual void printData() = 0;
  //   virtual Base* castNode() = 0;
  // };

  // template <typename T>
  // struct Node : Base {
  //   T* data;
  //   T* returnData() {
  //     return this->data;
  //   };
  //   void addData(T* data) {
  //     this->data = data;
  //   }
  //   Node(const int t, T* data) : Base(t) {
  //     std::cout << typeid(this).name() << std::endl;
  //     this->data = data;
  //   };
  //   void printData() {
  //     std::cout << *data << std::endl;
  //   };
  //   Node<T>* castNode() {
  //     return static_cast<Node<T>*>(this);
  //   };
  // };

  // template <typename T>
  // Base* Base::constructor(const int t, T* data) {
  //   return new Node(t, data);
  // };

  // class List {
  // public:
  //   Base* head;
  //   Base* tail;
  //   Base* iterator;

  //   List(const int t, void* data) {
  //     switch (t) {
  //     case 0:
  //       int* d = static_cast<int*>(data);
  //       this->head = Base::constructor(t, d);
  //     }
  //     this->tail = this->head;
  //     this->iterator = this->head;
  //   };

  //   // void appendNode(const int t) {
  //   //   this->tail->next = new Base(t);
  //   //   this->tail = this->tail->next;
  //   // };

  //   void nextNode() {
  //     this->tail = this->tail->next;
  //   }

  //   void swapConsecutiveNodes(Base* previous) {
  //     Base* a = previous;
  //     Base* b = a->next;
  //     Base* c = b->next;
  //     Base* d = c->next;
  //     a->next = c;
  //     c->next = b;
  //     b->next = d;
  //   };

  //   void resetIterator() {
  //     this->iterator = head;
  //   };
  // };
};
