namespace LinkedList {
  struct Base {
    const int t;
    Base* next;

    Base(const int t) : t{t} {};
    template <typename T>
    static Base* constructor(const int t, T* data);
  };

  template <typename T>
  struct Node : Base {
    T* data;

    Node(const int t, T* data) : Base(t) {
      this->data = data;
    };
  };

  template <typename T>
  Base* Base::constructor(const int t, T* data) {
    return new Node(t, data);
  };

  class List {
  public:
    Base* head;
    Base* tail;
    Base* iterator;

    List(const int t, void* d) {
      this->head = Base::constructor(t, d);
      this->tail = this->head;
      this->iterator = this->head;
    };

    void appendNode(const int t, void* d) {
      this->tail->next = Base::constructor(t, d);
      this->tail = this->tail->next;
    };

    void nextNode() {
      this->iterator = this->iterator->next;
    };

    void swapConsecutiveNodes(Base* previous) {
      // a -> b -> c -> d => a -> c-> b -> d
      Base* a = previous;
      Base* b = a->next;
      Base* c = b->next;
      Base* d = c->next;
      a->next = c;
      c->next = b;
      b->next = d;
    };

    void resetIterator() {
      this->iterator = head;
    };
  };

  template <typename T>
  Node<T>* read(Base* node, Node<T>* (*funct_ptr)(Node<T>* node)) {
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
};
