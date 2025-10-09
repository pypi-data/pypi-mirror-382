from typing import Any, Optional, Union

from markupsafe import Markup

from .mixins import Renderable, RenderOptionsMixin, RendersVarNameMixin


class LatLng(Renderable, RendersVarNameMixin):
    """Object representing Latitud and Longitud"""

    lat: float
    lng: float
    alt: Optional[float] = None

    def __init__(
        self,
        lat: float,
        lng: float,
        alt: Optional[float] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.lat = lat
        self.lng = lng
        self.alt = alt

    def __render_html__(self, as_variable: bool = False) -> Markup:
        string = f"[{self.lat}, {self.lng}]"
        if as_variable:
            string = f"var {self.var_name} = L.latlng({string});"
        return Markup(string)

    def as_tuple(self) -> tuple[float, float, float | None]:
        return self.lat, self.lng, self.alt

    def __eq__(self, other: Union["LatLng", tuple[float], Any]):
        if not isinstance(other, (LatLng, tuple)):
            return NotImplemented
        if isinstance(other, LatLng):
            return self.as_tuple() == other.as_tuple()
        return self.as_tuple() == tuple(other)


class LatLngBounds(Renderable, RendersVarNameMixin):
    corner_1: LatLng
    corner_2: LatLng

    def __init__(
        self,
        corner_1: LatLng | list[float],
        corner_2: LatLng | list[float],
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.corner_1 = corner_1 if isinstance(corner_1, LatLng) else LatLng(*corner_1)
        self.corner_2 = corner_2 if isinstance(corner_2, LatLng) else LatLng(*corner_2)

    def __render_html__(self, as_variable: bool = False) -> Markup:
        string = f"[{str(self.corner_1.__render_html__())}, {str(self.corner_2.__render_html__())}]"
        if as_variable:
            string = f"var {self.var_name} = L.latLngBounds({string});"
        return Markup(string)


class Point(Renderable, RendersVarNameMixin):
    x: int
    y: int

    def __init__(self, *args, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        if isinstance(args[0], self.__class__):
            self.x = args[0].x
            self.y = args[0].y
        elif isinstance(args[0], (tuple, list)) and len(args[0]) == 2:
            self.x, self.y = args[0]
        elif isinstance(args[0], (int, float)) and isinstance(args[1], (int, float)) and len(args) == 2:
            self.x, self.y = list(args)
        else:
            raise ValueError(f"Error trying to intialize Point with given args: {args}")

    def __render_html__(self, as_variable: bool = False) -> Markup:
        string = f"[{self.x}, {self.y}]"
        if as_variable:
            string = f"var {self.var_name} = L.point({string});"
        return Markup(string)


class Icon(Renderable, RendersVarNameMixin, RenderOptionsMixin):
    __not_render_options__ = ["id"]

    icon_url: Optional[str] = None
    icon_retina_url: Optional[str] = None
    icon_size: Optional[Point] = None
    icon_anchor: Optional[Point] = None
    popup_anchor: Point = Point(0, 0)
    tooltip_anchor: Point = Point(0, 0)
    shadow_url: Optional[str] = None
    shadow_retina_url = None
    shadow_size: Optional[Point] = None
    shadow_anchor: Optional[Point] = None
    class_name: str = ""
    cross_origin: bool | str = False

    def __init__(
        self,
        icon_url: Optional[str] = None,
        icon_retina_url: Optional[str] = None,
        icon_size: Optional[Point | list[int]] = None,
        icon_anchor: Optional[Point | list[int]] = None,
        popup_anchor: Optional[Point | list[int]] = None,
        tooltip_anchor: Optional[Point | list[int]] = None,
        shadow_url: Optional[str] = None,
        shadow_retina_url: Optional[str] = None,
        shadow_size: Optional[Point | list[int]] = None,
        shadow_anchor: Optional[Point | list[int]] = None,
        class_name: str = "",
        cross_origin: bool | str = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.icon_url = icon_url
        self.icon_retina_url = icon_retina_url
        self.icon_size = Point(icon_size) if icon_size else None
        self.icon_anchor = Point(icon_anchor) if icon_anchor else None
        self.popup_anchor = Point(popup_anchor) if popup_anchor else Point(0, 0)
        self.tooltip_anchor = Point(tooltip_anchor) if tooltip_anchor else Point(0, 0)
        self.shadow_url = shadow_url
        self.shadow_retina_url = shadow_retina_url
        self.shadow_size = Point(shadow_size) if shadow_size else None
        self.shadow_anchor = Point(shadow_anchor) if shadow_anchor else None
        self.class_name = class_name
        self.cross_origin = cross_origin

    def __render_html__(self, as_variable: bool = False) -> Markup:
        string = f"L.icon({self.render_options()})"
        if as_variable:
            string = f"var {self.var_name} = {string};"
        return Markup(string)


class DivIcon(Icon):
    html: str = ""
    bg_pos: Point = Point(0, 0)

    def __init__(self, html: str = "", bg_pos: Optional[Point | list[int]] = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.html = html
        self.bg_pos = Point(bg_pos) if bg_pos else Point(0, 0)

    def __render_html__(self, as_variable: bool = False) -> Markup:
        string = f"L.divIcon({self.render_options()})"
        if as_variable:
            string = f"var {self.var_name} = {string};"
        return Markup(string)
