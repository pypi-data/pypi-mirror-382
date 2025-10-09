import inspect
import json
from abc import ABC, abstractmethod
from typing import Any, Optional
from uuid import UUID, uuid4

from markupsafe import Markup

VARIABLE_START_CHARACTER = "%"


def to_camel_case(string: str) -> str:
    words = string.split("_")
    if len(words) > 1:
        for i, word in enumerate(words[1:], 1):
            words[i] = word.capitalize()
            if words[i].startswith("3"):
                words[i] = word.upper()
    return "".join(words)


class Renderable(ABC):
    @abstractmethod
    def __render_html__(self, as_variable: bool = False) -> Markup:
        pass


class RenderOptionsMixin:
    __not_render_options__: list[str]

    def _render_list_str(self, data_list: list[Any] | tuple[Any], as_variable: bool = False) -> str:
        render_list_str = "[" if isinstance(data_list, list) else "("
        for data in data_list:
            if isinstance(data, Renderable):
                render_list_str += str(data.__render_html__(as_variable))
            elif isinstance(data, dict):
                render_list_str += self._render_dict_str(data, as_variable)
            elif isinstance(data, (list, tuple)):
                render_list_str += self._render_list_str(data, as_variable)
            elif isinstance(data, str) and data.startswith(VARIABLE_START_CHARACTER):
                render_list_str += data[1:]
            else:
                render_list_str += json.dumps(data)
            render_list_str += ","
        render_list_str += "]" if isinstance(data_list, list) else ")"
        replace_args = (",]", "]") if isinstance(data_list, list) else (",)", ")")
        return render_list_str.replace(*replace_args)

    def _render_dict_str(self, data_dict: dict[str, Any], as_variable: bool = False) -> str:
        render_str = "{"
        for key, val in data_dict.items():
            render_str += f"{key}: "
            if isinstance(val, Renderable):
                render_str += str(val.__render_html__(as_variable))
            elif isinstance(val, dict):
                render_str += self._render_dict_str(val)
            elif isinstance(val, (tuple, list)):
                render_str += self._render_list_str(val)
            elif isinstance(val, str) and val.startswith(VARIABLE_START_CHARACTER):
                render_str += val[1:]
            else:
                render_str += json.dumps(val)
            render_str += ","
        render_str += "}"
        return render_str.replace(",}", "}")

    def __options(self) -> dict[str, Any]:
        options = {}

        for i in inspect.getmembers(self):
            if not i[0].startswith("_") and not inspect.ismethod(i[1]) and i[0] not in self.__not_render_options__ and getattr(self, i[0]) is not None:
                options[to_camel_case(i[0])] = i[1]

        return options

    def render_options(self, as_variable: bool = False) -> str:
        return self._render_dict_str(self.__options(), as_variable)


class RendersArgsMixin(RenderOptionsMixin):
    __render_args__: list[str]

    def __init__(self):
        super().__init__()

    def __args(self) -> list[Any]:
        return [getattr(self, name) for name in self.__render_args__]

    def render_args(self, as_variable: bool = False) -> str:
        string = ""
        for attr in self.__args():
            if isinstance(attr, Renderable):
                string += attr.__render_html__(as_variable)
            elif isinstance(attr, dict):
                string += self._render_dict_str(attr)
            elif isinstance(attr, (tuple, list)):
                print(self._render_list_str)
                string += self._render_list_str(attr)
            elif isinstance(attr, str) and attr.startswith(VARIABLE_START_CHARACTER):
                string += attr[1:]
            else:
                string += json.dumps(attr)
            string += ","
        return string


class RendersVarNameMixin:
    id: UUID | str

    def __init__(self, id: Optional[str | UUID] = None):
        self.id = id or uuid4()

    @property
    def var_name(self) -> str:
        return f"{self.__class__.__name__.lower()}_{self.id!s}".replace("-", "_")
