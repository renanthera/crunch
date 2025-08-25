import json
import os
import uuid

# Caches queries by identifier in a lookup table in `repo root/cache`.
# As implemented in requests, identifier is completed query that has been
# stringified and is ready to be passed as a Request.


def cache(Request):
  def decorator(query):
    ret = None
    cache = Cache()

    if query.cacheable:
      ret = Request(query, cache.get_artifact(query.string))
    if ret is None:
      ret = Request(query)
    if query.cacheable and not cache.lookup_uuid(query.string):
      cache.put_artifact(query.string, ret.data)
    return ret

  return decorator


class Cache:
  cache_root = 'cache'
  cache_index = cache_root + '/index.json'
  cache_artifacts = cache_root + '/artifacts/'

  def __init__(self):
    self.cache = read_artifact(self.cache_index)
    if self.cache is None:
      self.initialize_cache()
      self.cache = read_artifact(self.cache_index)
    assert self.cache is not None

  def initialize_cache(self):
    init = []
    write_artifact(init, self.cache_index)

  def get_artifact(self, identifier):
    self.artifact = None
    self.uuid = self.lookup_uuid(identifier)

    if self.uuid is None:
      self.uuid = uuid.uuid4()
    self.path = self.generate_path()
    self.artifact = read_artifact(self.path)

    return self.artifact

  def put_artifact(self, identifier, data):
    self.data = data
    payload = {'identifier': identifier, 'uuid': str(self.uuid)}

    self.cache.append(payload)  # type: ignore
    write_artifact(self.cache, self.cache_index)
    write_artifact(self.data, self.path)

  def lookup_uuid(self, identifier):
    for entry in self.cache:  # type: ignore
      if entry.get('identifier') == identifier:
        return entry['uuid']
    return None

  def generate_path(self):
    return self.cache_artifacts + str(self.uuid) + '.json'


def read_artifact(path):
  if not os.path.isfile(path):
    return None
  with open(path, 'r') as handle:
    json_object = json.load(handle)
  return json_object


def write_artifact(artifact, path):
  json_object = json.dumps(artifact, indent=2)
  os.makedirs(os.path.dirname(path), exist_ok=True)
  with open(path, 'w') as handle:
    handle.write(json_object)
  return 0
