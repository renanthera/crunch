#include <string>

namespace types {

  // i should probably just write a type generator to do this automatically and guarantee i dont fuck up numbering and it remains consistent
  // also auto-generate manipulators where needed
  struct t {
  };

  struct json_t : t {
  public:
    const static int cache_t = 0;
  };

  struct misc_t : t {
  public:
    const static int int_t = 1;
    const static int char_t = 2;
  };


  struct Cache {
    std::string reportCode;
    int startTime;
    int endTime;
    int actorID;
    std::string dataType;
    int abilityID;
    std::string path;
  };
};
