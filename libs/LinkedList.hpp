// template <typename Event> struct Node;

namespace LinkedList {
  template <typename Event>
  struct Node {
    char t;
    Event* event;
    Node* next;
  };

  template <typename Event> class List;

  template <typename Event> class List {
  public:
    Node<Event>* head;
    Node<Event>* iterator;

    Node<Event>* addNode(Node<Event>* previous, Event* event);
    void swapConsecutiveNodes(Node<Event>* previous);
    void resetIterator();

    List(Event* event);
  };

  template <typename Event>
  Node<Event>* List<Event>::
  addNode(Node<Event>* previous, Event* event) {
    previous->next = new Node<Event>;
    previous->next->event = event;
    return previous->next;
  };

  template <typename Event>
  void List<Event>::
  swapConsecutiveNodes(Node<Event>* previous) {
    // a -> b -> c -> d
    // a -> c -> b -> d
    Node<Event>* a = previous;
    Node<Event>* b = a->next;
    Node<Event>* c = b->next;
    Node<Event>* d = c->next;
    a->next = c;
    c->next = b;
    b->next = d;
  };

  template <typename Event>
  void List<Event>::
  resetIterator() {
    iterator = head;
  };

  template <typename Event>
  List<Event>::
  List(Event* event) {
    head = new Node<Event>;
    head->event = event;
    resetIterator();
  };
};
