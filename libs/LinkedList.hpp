// template <typename Data> struct Node;

namespace LinkedList {
  template <typename Data>
  struct Node {
    char t;
    Data* data;
    Node* next;
  };

  template <typename Data> class List;

  template <typename Data> class List {
  public:
    Node<Data>* head;
    Node<Data>* iterator;

    Node<Data>* addNode(Node<Data>* previous, Data* data);
    void swapConsecutiveNodes(Node<Data>* previous);
    void resetIterator();

    List(Data* data);
  };

  template <typename Data>
  Node<Data>* List<Data>::
  addNode(Node<Data>* previous, Data* data) {
    previous->next = new Node<Data>;
    previous->next->data = data;
    return previous->next;
  };

  template <typename Data>
  void List<Data>::
  swapConsecutiveNodes(Node<Data>* previous) {
    // a -> b -> c -> d
    // a -> c -> b -> d
    Node<Data>* a = previous;
    Node<Data>* b = a->next;
    Node<Data>* c = b->next;
    Node<Data>* d = c->next;
    a->next = c;
    c->next = b;
    b->next = d;
  };

  template <typename Data>
  void List<Data>::
  resetIterator() {
    iterator = head;
  };

  template <typename Data>
  List<Data>::
  List(Data* data) {
    head = new Node<Data>;
    head->data = data;
    resetIterator();
  };
};
