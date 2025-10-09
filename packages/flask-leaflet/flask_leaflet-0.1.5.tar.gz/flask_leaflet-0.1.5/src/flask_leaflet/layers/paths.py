from typing import Iterable, Literal, Optional

from markupsafe import Markup

from ..basic_types import LatLng
from .base import HasLayers, Layer
from .ui import BindsUILayers

_LineCap = Literal["butt", "round", "square"]
_FillRule = Literal["evenodd", "nonzero"]
_LineJoin = Literal["arcs", "bevel", "miter", "miter-clip", "round"]


class Path(BindsUILayers, Layer):
    __not_render_options__ = Layer.__not_render_options__ + ["ui_layers"]

    stroke: bool = True
    color: str = "#3388ff"
    weight: int = 3
    opacity: float = 1.0
    line_cap: _LineCap = "round"
    line_join: _LineJoin = "round"
    dash_array: Optional[str] = None
    dash_offset: Optional[str] = None
    fill: bool = True
    fill_color: str = color
    fill_opacity: float = 0.2
    fill_rule: _FillRule = "evenodd"
    bubbling_mouse_events: bool = True
    # renderer
    class_name: Optional[str] = None

    def __init__(
        self,
        stroke: bool = True,
        color: str = "#3388ff",
        weight: int = 3,
        opacity: float = 1.0,
        line_cap: _LineCap = "round",
        line_join: _LineJoin = "round",
        dash_array: Optional[str] = None,
        dash_offset: Optional[str] = None,
        fill: bool = True,
        fill_color: str = color,
        fill_opacity: float = 0.2,
        fill_rule: _FillRule = "evenodd",
        bubbling_mouse_events: bool = True,
        class_name: Optional[str] = None,
        ui_layers: Optional[list[Layer]] = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.stroke = stroke
        self.color = color
        self.weight = weight
        self.opacity = opacity
        self.line_cap = line_cap
        self.line_join = line_join
        self.dash_array = dash_array
        self.dash_offset = dash_offset
        self.fill = fill
        self.fill_color = fill_color
        self.fill_opacity = fill_opacity
        self.fill_rule = fill_rule
        self.bubbling_mouse_events = bubbling_mouse_events
        self.class_name = class_name
        self.ui_layers = ui_layers or []

    def __render_html__(self, as_variable: bool = False) -> Markup:
        string = super().__render_html__(as_variable=as_variable)
        string = string + self.render_ui_layers(as_variable=as_variable)
        return string


class CircleMarker(Path):
    __render_args__ = ["latlng"]
    __not_render_options__ = Path.__not_render_options__ + __render_args__

    latlng: LatLng
    radius: int = 10

    def __init__(self, latlng: LatLng | list[float], radius: int = 10, **kwargs) -> None:
        super().__init__(**kwargs)
        self.latlng = latlng if isinstance(latlng, LatLng) else LatLng(*latlng)
        self.radius = radius


class Polyline(Path):
    __render_args__ = ["latlngs"]
    __not_render_options__ = Path.__not_render_options__ + __render_args__

    latlngs: list[LatLng]

    smooth_factor: float = 1.0
    no_clip: bool = False

    def __init__(
        self,
        latlngs: list[LatLng | tuple[float, float] | tuple[float, float, float]],
        smooth_fator: float = 1.0,
        no_clip: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.latlngs = self.__check_latlngs(latlngs)
        self.smooth_factor = smooth_fator
        self.no_clip = no_clip

    def __check_latlngs(
        self,
        latlngs: list[LatLng | tuple[float, float] | tuple[float, float, float]],
    ) -> list[LatLng]:
        out_latlngs = []

        for content in latlngs:
            if isinstance(content, (tuple, list, Iterable)):
                out_latlngs.append(LatLng(*content))

            elif isinstance(content, LatLng):
                out_latlngs.append(content)

        return out_latlngs


class Polygon(Polyline):
    def __init__(
        self,
        latlngs: list[LatLng | tuple[float, float] | tuple[float, float, float]],
        **kwargs,
    ) -> None:
        super().__init__(latlngs, **kwargs)


class Rectangle(Polygon):
    def __init__(
        self,
        latlngs: list[LatLng | tuple[float, float] | tuple[float, float, float]],
        **kwargs,
    ) -> None:
        super().__init__(latlngs, **kwargs)


class Circle(CircleMarker):
    def __init__(self, latlng: LatLng | list[float], radius: int = 10, **kwargs) -> None:
        super().__init__(latlng, radius, **kwargs)


class CreatesPathLayers(HasLayers):
    layers: list[Layer]

    def new_polyline(
        self,
        latlngs: list[LatLng | tuple[float, float] | tuple[float, float, float]],
        smooth_fator: float = 1.0,
        no_clip: bool = False,
        **kwargs,
    ) -> Polyline:
        polyline = Polyline(latlngs, smooth_fator, no_clip, **kwargs)
        polyline.owner = self
        self.layers.append(polyline)
        return polyline

    def new_polygon(
        self,
        latlngs: list[LatLng | tuple[float, float] | tuple[float, float, float]],
        **kwargs,
    ) -> Polygon:
        polygon = Polygon(latlngs, **kwargs)
        polygon.owner = self
        self.layers.append(polygon)
        return polygon

    def new_rectangle(
        self,
        latlngs: list[LatLng | tuple[float, float] | tuple[float, float, float]],
        **kwargs,
    ) -> Rectangle:
        rectangle = Rectangle(latlngs, **kwargs)
        rectangle.owner = self
        self.layers.append(rectangle)
        return rectangle

    def new_circle(self, latlng: LatLng | list[float], radius: int = 10, **kwargs) -> Circle:
        circle = Circle(latlng, radius, **kwargs)
        circle.owner = self
        self.layers.append(circle)
        return circle
