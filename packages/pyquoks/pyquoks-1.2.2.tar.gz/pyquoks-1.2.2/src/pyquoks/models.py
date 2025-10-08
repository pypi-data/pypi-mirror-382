from __future__ import annotations


class IContainer:
    _ATTRIBUTES: set[str] = None
    _DATA: dict[str, type] = None
    _OBJECTS: dict[str, type] = None
    data: dict

    def __init__(self, json_data: dict) -> None:
        setattr(self, "data", json_data)
        if isinstance(self._ATTRIBUTES, set):
            for i in self._ATTRIBUTES:
                setattr(self, i, self.data.get(i, None))
        if isinstance(self._DATA, dict):
            for k, v in self._DATA.items():
                try:
                    setattr(self, k, [v(i) for i in self.data])
                except:
                    setattr(self, k, None)
        elif isinstance(self._OBJECTS, dict):
            for k, v in self._OBJECTS.items():
                try:
                    setattr(self, k, [v(i) for i in self.data.get(k)])
                except:
                    setattr(self, k, None)


class IModel:
    _ATTRIBUTES: set[str] | dict[str, set[str]] = None
    _OBJECTS: dict[str, type] = None
    data: dict | list[dict]

    def __init__(self, json_data: dict | list[dict]) -> None:
        setattr(self, "data", json_data)
        if isinstance(self._ATTRIBUTES, set):
            for i in self._ATTRIBUTES:
                setattr(self, i, self.data.get(i, None))
        elif isinstance(self._ATTRIBUTES, dict):
            for k, v in self._ATTRIBUTES.items():
                if isinstance(v, set):
                    for i in v:
                        try:
                            setattr(self, i, self.data.get(k).get(i, None))
                        except:
                            setattr(self, i, None)
        if isinstance(self._OBJECTS, dict):
            for k, v in self._OBJECTS.items():
                try:
                    setattr(self, k, v(self.data.get(k)))
                except:
                    setattr(self, k, None)


class IValues:
    _ATTRIBUTES: set[str] = None

    def __init__(self, **kwargs) -> None:
        for i in self._ATTRIBUTES:
            setattr(self, i, kwargs.get(i, None))

    def update(self, **kwargs) -> None:
        self.__init__(**kwargs)
