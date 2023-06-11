import json

import jmespath


class Jemes:
    """
    Позволяет читать json как объект.
    Для работы требуется указать путь к файлу json.

    Например файл содержит следующий json

    `{"name": "foo"}`

    >>> o = Jemes("/path.json")
    >>> o.name == "foo"
    True
    """

    def __init__(self, file_path: str):
        self.__json = self._load_json(file_path)

    def __getattr__(self, item: str) -> str:
        _json = self.__json

        if item not in _json:
            raise AttributeError(f"{self} has no attribute {item}")
        value = jmespath.search(item, _json)
        return value

    def __iter__(self):
        return iter(self.__json.keys())

    def _load_json(self, filepath) -> dict:
        with open(filepath) as f:
            _json = json.load(f)
        return _json
