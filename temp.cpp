// spell ids

enum purificationSpells {
  purifying_brew = 119582
};

// event payload

struct Event {
  int timestamp;
};

struct StaggerTick : Event {
  int amount;
  int amountabsorbed;
  int unmitigatedamount;
};

struct AbsorbTick : Event {
  int amount;
};

struct Purification : Event {
  int spellID;
};

struct BuffApplication : Event {
  int spellID;
  int stacks;
};
