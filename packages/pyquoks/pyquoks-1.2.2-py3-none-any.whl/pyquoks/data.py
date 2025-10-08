from __future__ import annotations
import configparser, datetime, logging, json, sys, io, os
import requests, PIL.Image, PIL.ImageDraw
from . import utils


# Providers
class IDataProvider:
    _PATH: str
    _DATA_VALUES: dict[str, type]

    def __init__(self) -> None:
        for k, v in self._DATA_VALUES.items():
            try:
                with open(self._PATH.format(k), "rb") as file:
                    setattr(self, k, v(json_data=json.loads(file.read())))
            except:
                setattr(self, k, None)


class IConfigProvider:
    class IConfig:
        _SECTION: str = None
        _CONFIG_VALUES: dict[str, type]

        def __init__(self, parent: IConfigProvider = None) -> None:
            if isinstance(parent, IConfigProvider):
                self._CONFIG_VALUES = parent._CONFIG_VALUES.get(self._SECTION)
                self._incorrect_content_exception = configparser.ParsingError("config.ini is filled incorrectly!")
                self._config = configparser.ConfigParser()
                self._config.read(utils.get_path("config.ini"))
                if not self._config.has_section(self._SECTION):
                    self._config.add_section(self._SECTION)
                for k, v in self._CONFIG_VALUES.items():
                    try:
                        setattr(self, k, self._config.get(self._SECTION, k))
                    except:
                        self._config.set(self._SECTION, k, v.__name__)
                        with open(utils.get_path("config.ini"), "w", encoding="utf-8") as file:
                            self._config.write(fp=file)
                for k, v in self._CONFIG_VALUES.items():
                    try:
                        if v == int:
                            setattr(self, k, int(getattr(self, k)))
                        elif v == bool:
                            if getattr(self, k) not in (str(True), str(False)):
                                setattr(self, k, None)
                                raise self._incorrect_content_exception
                            else:
                                setattr(self, k, getattr(self, k) == str(True))
                        elif v in (dict, list):
                            setattr(self, k, json.loads(getattr(self, k)))
                    except:
                        setattr(self, k, None)
                        raise self._incorrect_content_exception
                if not self.values:
                    raise self._incorrect_content_exception

        @property
        def values(self) -> dict | None:
            try:
                return {i: getattr(self, i) for i in self._CONFIG_VALUES}
            except:
                return None

    _CONFIG_VALUES: dict[str, dict[str, type]]
    _CONFIG_OBJECTS: dict[str, type]

    def __init__(self) -> None:
        for k, v in self._CONFIG_OBJECTS.items():
            setattr(self, k, v(self))


class IAssetsProvider:
    class IDirectory:
        _PATH: str = None
        _NAMES: set[str]

        def __init__(self, parent: IAssetsProvider) -> None:
            for i in self._NAMES:
                setattr(self, i, parent.file_image(parent._PATH.format(self._PATH.format(i))))

    class INetwork:
        _URLS: dict[str, str]

        def __init__(self, parent: IAssetsProvider) -> None:
            for k, v in self._URLS:
                setattr(self, k, parent.network_image(v))

    _PATH: str
    _ASSETS_OBJECTS: dict[str, type]

    def __init__(self) -> None:
        for k, v in self._ASSETS_OBJECTS.items():
            setattr(self, k, v(self))

    @staticmethod
    def file_image(path: str) -> PIL.Image.Image:
        with open(path, "rb") as file:
            return PIL.Image.open(io.BytesIO(file.read()))

    @staticmethod
    def network_image(url: str) -> PIL.Image.Image:
        return PIL.Image.open(io.BytesIO(requests.get(url).content))

    @staticmethod
    def round_corners(image: PIL.Image.Image, radius: int) -> PIL.Image.Image:
        if image.mode != "RGB":
            image = image.convert("RGB")
        width, height = image.size
        shape = PIL.Image.new("L", (radius * 2, radius * 2), 0)
        alpha = PIL.Image.new("L", image.size, "white")
        PIL.ImageDraw.Draw(shape).ellipse((0, 0, radius * 2, radius * 2), fill=255)
        alpha.paste(shape.crop((0, 0, radius, radius)), (0, 0))
        alpha.paste(shape.crop((0, radius, radius, radius * 2)), (0, height - radius))
        alpha.paste(shape.crop((radius, 0, radius * 2, radius)), (width - radius, 0))
        alpha.paste(shape.crop((radius, radius, radius * 2, radius * 2)), (width - radius, height - radius))
        image.putalpha(alpha)
        return image


class IStringsProvider:
    class IStrings:
        pass

    _STRINGS_OBJECTS: dict[str, type]

    def __init__(self) -> None:
        for k, v in self._STRINGS_OBJECTS.items():
            setattr(self, k, v())


# Managers
if sys.platform == "win32":
    import winreg


    class IRegistryManager:
        class IRegistry:
            _NAME: str = None
            _REGISTRY_VALUES: dict[str, int]

            def __init__(self, parent: IRegistryManager = None) -> None:
                if isinstance(parent, IRegistryManager):
                    self._REGISTRY_VALUES = parent._REGISTRY_VALUES.get(self._NAME)
                    self._path = winreg.CreateKey(parent._path, self._NAME)
                    for i in self._REGISTRY_VALUES.keys():
                        try:
                            setattr(self, i, winreg.QueryValueEx(self._path, i)[int()])
                        except:
                            setattr(self, i, None)

            @property
            def values(self) -> dict | None:
                try:
                    return {i: getattr(self, i) for i in self._REGISTRY_VALUES}
                except:
                    return None

            def refresh(self) -> IRegistryManager.IRegistry:
                self.__init__()
                return self

            def update(self, **kwargs) -> None:
                for k, v in kwargs.items():
                    winreg.SetValueEx(self._path, k, None, self._REGISTRY_VALUES.get(k), v)
                    setattr(self, k, v)

        _KEY: str
        _REGISTRY_VALUES: dict[str, dict[str, int]]
        _REGISTRY_OBJECTS: dict[str, type]
        _path: winreg.HKEYType

        def __init__(self) -> None:
            self._path = winreg.CreateKey(winreg.HKEY_CURRENT_USER, self._KEY)
            for k, v in self._REGISTRY_OBJECTS.items():
                setattr(self, k, v(self))

        def refresh(self) -> IRegistryManager:
            self.__init__()
            return self


# Services
class LoggerService(logging.Logger):
    def __init__(
            self,
            name: str, file_handling: bool = True,
            filename: str = datetime.datetime.now().strftime("%d-%m-%y-%H-%M-%S"),
            level: int = logging.NOTSET,
            folder_name: str = "logs",
    ) -> None:
        super().__init__(name, level)
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(
            logging.Formatter(fmt="$levelname $asctime $name - $message", datefmt="%d-%m-%y %H:%M:%S", style="$")
        )
        self.addHandler(stream_handler)
        if file_handling:
            os.makedirs(utils.get_path(folder_name, only_abspath=True), exist_ok=True)
            file_handler = logging.FileHandler(
                utils.get_path(f"{folder_name}/{filename}-{name}.log", only_abspath=True),
                encoding="utf-8",
            )
            file_handler.setFormatter(
                logging.Formatter(fmt="$levelname $asctime - $message", datefmt="%d-%m-%y %H:%M:%S", style="$"),
            )
            self.addHandler(file_handler)

    def log_exception(self, e: Exception) -> None:
        self.error(msg=e, exc_info=True)
