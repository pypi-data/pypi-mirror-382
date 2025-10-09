from typing import Optional

from markupsafe import Markup

from ..basic_types import Icon, LatLng, Point
from .base import HasLayers, InteractiveLayer, Layer


class DivOverlay(InteractiveLayer):
    offset: Optional[Point] = None
    class_name: str = ""
    pane: Optional[str] = None  # type: ignore
    content: str = ""

    def __init__(
        self,
        offset: Optional[Point | tuple[float, float]] = None,
        class_name: str = "",
        pane: Optional[str] = None,
        content: str = "",
        **kwargs,
    ) -> None:
        super().__init__(pane=pane, **kwargs)
        self.offset = Point(*offset) if isinstance(offset, (tuple, list)) else offset
        self.class_name = class_name
        self.content = content


class Popup(DivOverlay):
    __render_args__ = ["latlng"]
    __not_render_options__ = DivOverlay.__not_render_options__ + __render_args__

    latlng: LatLng
    pane: str = "popupPane"
    offset: Optional[Point] = None
    max_width: int = 300
    min_width: int = 50
    max_height: Optional[int] = None
    auto_pan: bool = True
    auto_pan_padding_top_left: Optional[Point] = None
    auto_pan_padding_bottom_right: Optional[Point] = None
    auto_pan_padding: Point = Point(5, 5)
    keep_in_view: bool = False
    close_button: bool = True
    auto_close: bool = True
    close_on_escape_key: bool = True
    close_on_click: bool = False

    def __init__(
        self,
        latlng: LatLng | tuple[float, float],
        content: str = "",
        pane: str = "popupPane",
        offset: Optional[Point | tuple[float, float]] = None,
        max_width: int = 300,
        min_width: int = 50,
        max_height: Optional[int] = None,
        auto_pan: bool = True,
        auto_pan_padding_top_left: Optional[Point | tuple[float, float]] = None,
        auto_pan_padding_bottom_right: Optional[Point | tuple[float, float]] = None,
        auto_pan_padding: Optional[Point | tuple[float, float]] = None,
        keep_in_view: bool = False,
        close_button: bool = True,
        auto_close: bool = True,
        close_on_escape_key: bool = True,
        close_on_click: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(offset=offset or Point(0, 7), content=content, pane=pane, **kwargs)
        self.latlng = LatLng(*latlng) if isinstance(latlng, (tuple, list)) else latlng
        self.max_width = max_width
        self.min_width = min_width
        self.max_height = max_height
        self.auto_pan = auto_pan
        self.auto_pan_padding_top_left = Point(*auto_pan_padding_top_left) if isinstance(auto_pan_padding_top_left, (list, tuple)) else auto_pan_padding_top_left
        self.auto_pan_padding_bottom_right = (
            Point(*auto_pan_padding_bottom_right) if isinstance(auto_pan_padding_bottom_right, (list, tuple)) else auto_pan_padding_bottom_right
        )
        self.auto_pan_padding = Point(*auto_pan_padding) if isinstance(auto_pan_padding, (list, tuple)) else Point(5, 5)
        self.keep_in_view = keep_in_view
        self.close_button = close_button
        self.auto_close = auto_close
        self.close_on_escape_key = close_on_escape_key
        self.close_on_click = close_on_click


class Tooltip(DivOverlay):
    __render_args__ = ["latlng"]
    __not_render_options__ = DivOverlay.__not_render_options__ + __render_args__

    latlng: LatLng
    pane: str = "tooltipPane"
    offset: Point = Point(0, 0)
    direction: str = "auto"
    permanent: bool = False
    opacity: float = 0.9

    def __init__(
        self,
        latlng: tuple[float, float] | LatLng,
        content: str = "",
        pane: str = "tooltipPane",
        offset: Optional[Point] = None,
        direction: str = "auto",
        permanent: bool = False,
        opacity: float = 0.9,
        **kwargs,
    ) -> None:
        offset = Point(*offset) if isinstance(offset, (list, tuple)) else (offset or Point(0, 0))
        super().__init__(content=content, pane=pane, offset=offset, **kwargs)
        self.latlng = latlng if isinstance(latlng, LatLng) else LatLng(*latlng)
        self.direction = direction
        self.permanent = permanent
        self.opacity = opacity


class BindsUILayers:
    latlng: Optional[LatLng]
    latlngs: Optional[list[LatLng]]
    var_name: str
    ui_layers: list[Layer]

    def add_ui_layer(self, ui_layer: Tooltip | Popup) -> None:
        self.ui_layers.append(ui_layer)

    def new_tooltip(
        self,
        content: str = "",
        latlng: Optional[LatLng] = None,
        pane: str = "tooltipPane",
        offset: Optional[Point] = None,
        direction: str = "auto",
        permanent: bool = False,
        opacity: float = 0.9,
        **kwargs,
    ) -> Tooltip:
        _latlng = self.__resolve_latlng(latlng)
        tooltip = Tooltip(
            _latlng,
            content,
            pane,
            offset or Point(0, 0),
            direction,
            permanent,
            opacity,
            **kwargs,
        )
        self.add_ui_layer(tooltip)
        return tooltip

    def new_popup(
        self,
        content: str = "",
        latlng: Optional[LatLng] = None,
        pane: str = "popupPane",
        offset: Optional[Point | tuple[float, float]] = None,
        max_width: int = 300,
        min_width: int = 50,
        max_height: Optional[int] = None,
        auto_pan: bool = True,
        auto_pan_padding_top_left: Optional[Point | tuple[float, float]] = None,
        auto_pan_padding_bottom_right: Optional[Point | tuple[float, float]] = None,
        auto_pan_padding: Optional[Point | tuple[float, float]] = None,
        keep_in_view: bool = False,
        close_button: bool = True,
        auto_close: bool = True,
        close_on_escape_key: bool = True,
        close_on_click: bool = False,
        **kwargs,
    ) -> Popup:
        _latlng = self.__resolve_latlng(latlng)
        popup = Popup(
            _latlng,
            content,
            pane,
            offset or Point(0, 7),
            max_width,
            min_width,
            max_height,
            auto_pan,
            auto_pan_padding_top_left,
            auto_pan_padding_bottom_right,
            auto_pan_padding or Point(5, 5),
            keep_in_view,
            close_button,
            auto_close,
            close_on_escape_key,
            close_on_click,
            **kwargs,
        )
        self.add_ui_layer(popup)
        return popup

    def render_ui_layers(self, as_variable: bool = False) -> str:
        string = ""
        if as_variable:
            for ui_layer in self.ui_layers:
                string = ui_layer.__render_html__(as_variable)

                string = Markup(f"{string}{self.var_name}.bind{ui_layer.__class__.__name__}({ui_layer.var_name});")
        else:
            for ui_layer in self.ui_layers:
                string += f".bind{ui_layer.__class__.__name__}({ui_layer.__render_html__()})"
        return string

    def __resolve_latlng(self, latlng: Optional[LatLng] = None) -> LatLng:
        if latlng:
            return latlng
        if hasattr(self, "latlng") and self.latlng is not None:
            return self.latlng
        elif hasattr(self, "latlngs") and self.latlngs is not None and len(self.latlngs) > 1:
            return self.latlngs[0]
        else:
            raise AttributeError("Could not resolve latlng attribute. You must provide one")


class Marker(BindsUILayers, Layer):
    __render_args__ = ["latlng"]
    __not_render_options__ = Layer.__not_render_options__ + __render_args__ + ["ui_layers"]

    latlng: LatLng
    icon: Optional[Icon | str] = None
    keyboard: bool = True
    title: str = ""
    alt: str = "Marker"
    z_index_offset: int = 0
    opacity: float = 1.0
    rise_on_hover: bool = False
    rise_offset: int = 250
    pane: str = "markerPane"
    shadow_pane: str = "shadowPane"
    bubbling_mouse_events: bool = False
    auto_pan_on_focus: bool = True

    def __init__(
        self,
        latlng: tuple[float, float] | LatLng,
        icon: Optional[Icon | str] = None,
        keyboard: bool = True,
        title: str = "",
        alt: str = "Marker",
        z_index_offset: int = 0,
        opacity: float = 1.0,
        rise_on_hover: bool = False,
        rise_offset: int = 250,
        pane: str = "markerPane",
        shadow_pane: str = "shadowPane",
        bubbling_mouse_events: bool = False,
        auto_pan_on_focus: bool = True,
        ui_layers: Optional[list[Layer]] = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.latlng = latlng if isinstance(latlng, LatLng) else LatLng(*latlng)
        self.icon = icon or r"%leaflet_default_icon"
        self.keyboard = keyboard
        self.title = title
        self.alt = alt
        self.z_index_offset = z_index_offset
        self.opacity = opacity
        self.rise_on_hover = rise_on_hover
        self.rise_offset = rise_offset
        self.pane = pane
        self.shadow_pane = shadow_pane
        self.bubbling_mouse_events = bubbling_mouse_events
        self.auto_pan_on_focus = auto_pan_on_focus
        self.ui_layers = ui_layers or []

    def __render_html__(self, as_variable: bool = False) -> Markup:
        string = super().__render_html__(as_variable=as_variable)
        string = string + self.render_ui_layers(as_variable=as_variable)
        return string


class CreatesUILayers(HasLayers):
    layers: list[Layer]

    def new_marker(
        self,
        latlng: tuple[float, float] | LatLng,
        icon: Optional[Icon | str] = None,
        keyboard: bool = True,
        title: str = "",
        alt: str = "Marker",
        z_index_offset: int = 0,
        opacity: float = 1.0,
        rise_on_hover: bool = False,
        rise_offset: int = 250,
        pane: str = "markerPane",
        shadow_pane: str = "shadowPane",
        bubbling_mouse_events: bool = False,
        auto_pan_on_focus: bool = True,
        **kwargs,
    ) -> Marker:
        marker = Marker(
            latlng,
            icon,
            keyboard,
            title,
            alt,
            z_index_offset,
            opacity,
            rise_on_hover,
            rise_offset,
            pane,
            shadow_pane,
            bubbling_mouse_events,
            auto_pan_on_focus,
            **kwargs,
        )
        self.layers.append(marker)
        marker.owner = self
        return marker

    def new_tooltip(
        self,
        latlng: LatLng | tuple[float, float],
        content: str = "",
        pane: str = "tooltipPane",
        offset: Optional[Point] = None,
        direction: str = "auto",
        permanent: bool = False,
        opacity: float = 0.9,
        **kwargs,
    ) -> Tooltip:
        tooltip = Tooltip(
            latlng,
            content,
            pane,
            offset or Point(0, 0),
            direction,
            permanent,
            opacity,
            **kwargs,
        )
        self.layers.append(tooltip)
        tooltip.owner = self
        return tooltip

    def new_popup(
        self,
        latlng: LatLng | tuple[float, float],
        content: str = "",
        pane: str = "popupPane",
        offset: Optional[Point | tuple[float, float]] = None,
        max_width: int = 300,
        min_width: int = 50,
        max_height: Optional[int] = None,
        auto_pan: bool = True,
        auto_pan_padding_top_left: Optional[Point | tuple[float, float]] = None,
        auto_pan_padding_bottom_right: Optional[Point | tuple[float, float]] = None,
        auto_pan_padding: Optional[Point | tuple[float, float]] = None,
        keep_in_view: bool = False,
        close_button: bool = True,
        auto_close: bool = True,
        close_on_escape_key: bool = True,
        close_on_click: bool = False,
        **kwargs,
    ) -> Popup:
        popup = Popup(
            latlng,
            content,
            pane,
            offset or Point(0, 7),
            max_width,
            min_width,
            max_height,
            auto_pan,
            auto_pan_padding_top_left,
            auto_pan_padding_bottom_right,
            auto_pan_padding or Point(5, 5),
            keep_in_view,
            close_button,
            auto_close,
            close_on_escape_key,
            close_on_click,
            **kwargs,
        )
        self.layers.append(popup)
        popup.owner = self
        return popup
