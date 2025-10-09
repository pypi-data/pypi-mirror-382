from typing import Literal, Optional

from markupsafe import Markup

from .basic_types import LatLng, LatLngBounds
from .layers.base import Layer
from .layers.paths import CreatesPathLayers
from .layers.raster import CreatesRasterLayers
from .layers.ui import CreatesUILayers
from .mixins import RenderOptionsMixin, RendersVarNameMixin


class Map(
    RenderOptionsMixin,
    RendersVarNameMixin,
    CreatesRasterLayers,
    CreatesUILayers,
    CreatesPathLayers,
):
    __not_render_options__ = ["id", "var_name", "layers"]

    prefer_canvas: bool = True

    attribution_control: bool = True
    zoom_control: bool = True

    close_popup_on_click: bool = True
    box_zoom: bool = True
    double_click_zoom: bool | Literal["center"] = True
    dragging: bool = True
    zoom_snap: int = 1
    zoom_delta: int = 1
    track_resize: bool = True

    inertia: bool = False
    inertia_deceleration: int = 3000
    inertia_max_speed: float = float("inf")
    ease_linearity: bool | float = 0.2
    world_copy_jump: bool = False
    max_bounds_viscosity: float = 0.0

    keyboard: bool = True
    keyboard_pan_delta: int = 80

    scroll_wheel_zoom: bool | str = True
    wheel_debounce_time: int = 40
    wheel_px_per_zoom_level: int = 60

    tap_hold: bool = True
    tap_tolerance: int = 15
    touch_zoom: bool | Literal["center"] = False
    bounce_at_zoom_limits: bool = True

    center: Optional[LatLng] = None
    zoom: int = 14
    min_zoom: int = 0
    max_zoom: int = 18

    layers: list[Layer]
    max_bounds: Optional[list[LatLng]] = None

    zoom_animation: bool = True
    zoom_animation_threshold: int = 4
    fade_animation: bool = True
    marker_zoom_animation: bool = True
    transform_3D_Limit: int = 2**23
    _fit_bounds: Optional[LatLngBounds] = None

    def __init__(
        self,
        id: str,
        center: Optional[LatLng | tuple[float, float]] = None,
        zoom: int = 13,
        layers: Optional[list[Layer]] = None,
        **kwargs,
    ) -> None:
        self.id = id
        self.center = LatLng(*center) if isinstance(center, (list, tuple)) else center
        self.zoom = zoom
        self.layers = layers or []

        for key, val in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, val)

    def fit_bounds(self, bounds: LatLngBounds | list[list[int | float]]) -> None:
        if isinstance(bounds, (tuple, list)):
            bounds = LatLngBounds(LatLng(*bounds[0]), LatLng(*bounds[1]))
        self._fit_bounds = bounds

    def lock_interaction(self) -> None:
        self.keyboard = False
        self.scroll_wheel_zoom = False
        self.box_zoom = False
        self.dragging = False
        self.zoom_control = False
        self.double_click_zoom = False
        self.tap_hold = False

    def unlock_interaction(self) -> None:
        self.keyboard = True
        self.scroll_wheel_zoom = True
        self.box_zoom = True
        self.dragging = True
        self.zoom_control = True
        self.double_click_zoom = True
        self.tap_hold = True

    def __render_js__(self) -> Markup:
        string = Markup(f"var {self.var_name} = L.map({self.id},{self.render_options()});")
        for layer in self.layers:
            string += layer.__render_html__(as_variable=True)
        if self._fit_bounds:
            string += Markup(f"{self.var_name}.fitBounds({self._fit_bounds.__render_html__()});")
        return string

    def __render_html__(self, class_: str = "") -> Markup:
        return Markup(f'<div id="{self.id}" class="{class_}" ></div>')
