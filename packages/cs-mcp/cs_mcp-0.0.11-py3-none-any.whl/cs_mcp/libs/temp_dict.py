import uuid


class TempDict:
  def __init__(self):
    self._data = {}

  def create_key(self):
    return str(uuid.uuid4())

  def set(self, value):
    key = self.create_key()
    self._data[key] = value
    return key

  def get(self, key, default=None):
    return self._data.get(key, default)

  def delete(self, key):
    if key in self._data:
      del self._data[key]

  def clear(self):
    self._data.clear()


temp_dict = TempDict()