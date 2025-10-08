from __future__ import annotations
import waitress, typing, flask


class ILocalhostFlask(flask.Flask):
    _RULES: dict[str, typing.Callable]

    def __init__(self, import_name: str) -> None:
        super().__init__(import_name)

        for k, v in self._RULES.items():
            self.add_url_rule(rule=k, view_func=v)

    def serve(self, port: int) -> None:
        waitress.serve(
            app=self,
            host="127.0.0.1",
            port=port,
        )
