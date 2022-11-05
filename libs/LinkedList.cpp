#include "LinkedList.hpp"

// namespace LinkedList {
//   Template class members must be defined in the header, or specifications must be instantiated at the footer of this file. Fuck me.


//   template <typename Event>
//   struct Node {
//     char t;
//     Event* event;
//     Node* next;
//   };

//   template <typename Event>
//   class List {
//   public:
//     Node<Event>* head;
//     Node<Event>* iterator;
//     Node<Event>* addNode(Node<Event>* previous, Event* event);
//     void resetIterator();
//     List(Event* event);
//   };

//   template <typename Event>
//   Node<Event>* List<Event>::
//   addNode(Node<Event>* previous, Event* event) {
//     previous->next = new Node<Event>;
//     previous->next->event = event;
//     return previous->next;
//   };

//   template <typename Event>
//   void List<Event>::
//   resetIterator() {
//     iterator = head;
//   };

//   template <typename Event>
//   List<Event>::
//   List(Event* event) {
//     head = new Node<Event>;
//     head->event = event;
//     resetIterator();
//   };
// };
