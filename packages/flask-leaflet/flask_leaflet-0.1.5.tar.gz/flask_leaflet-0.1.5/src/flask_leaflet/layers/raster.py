from typing import Optional

from ..basic_types import LatLngBounds, Point
from .base import HasLayers, InteractiveLayer, Layer

RASTER_LAYERS = ("TileLayer", "WMSTileLayer", "ImageOverlay", "VideoOverlay")


class GridLayer(Layer):
    tile_size: int | Point = 256
    opacity: float = 1.0
    update_when_idle: bool = False
    update_when_zooming: bool = True
    update_interval: int = 200
    z_index: int = 1
    bounds: Optional[LatLngBounds] = None
    min_zoom: int = 0
    max_zoom: Optional[int] = None
    max_native_zoom: Optional[int] = None
    min_native_zoom: Optional[int] = None
    no_wrap: bool = False
    pane: str = "tilePane"
    class_name: str = ""
    keep_buffer: int = 2

    def __init__(
        self,
        tile_size: int | Point = 256,
        opacity: float = 1.0,
        update_when_idle: bool = False,
        update_when_zooming: bool = True,
        update_interval: int = 200,
        z_index: int = 1,
        bounds: Optional[LatLngBounds] = None,
        min_zoom: int = 0,
        max_zoom: Optional[int] = None,
        max_native_zoom: Optional[int] = None,
        min_native_zoom: Optional[int] = None,
        no_wrap: bool = False,
        pane: str = "tilePane",
        class_name: str = "",
        keep_buffer: int = 2,
        **kwargs,
    ) -> None:
        super().__init__(pane=pane, **kwargs)
        self.tile_size = tile_size
        self.opacity = opacity
        self.update_when_idle = update_when_idle
        self.update_when_zooming = update_when_zooming
        self.update_interval = update_interval
        self.z_index = z_index
        self.bounds = bounds
        self.min_zoom = min_zoom
        self.max_zoom = max_zoom
        self.max_native_zoom = max_native_zoom
        self.min_native_zoom = min_native_zoom
        self.no_wrap = no_wrap
        self.class_name = class_name
        self.keep_buffer = keep_buffer


class TileLayer(GridLayer):
    __render_args__ = ["url_template"]
    __not_render_options__ = GridLayer.__not_render_options__ + __render_args__

    url_template: str
    min_zoom: int = 0
    max_zoom: int = 18
    subdomains: str = "abc"
    error_tile_url: str = ""
    zoom_offset: int = 0
    tms: bool = False
    zoom_reverse: bool = False
    detect_retina: bool = False
    cross_origin: bool | str = False
    referrer_policy: bool | str = False

    def __init__(
        self,
        url_template: str,
        min_zoom: int = 0,
        max_zoom: int = 18,
        subdomains: str = "abc",
        error_tile_url: str = "",
        zoom_offset: int = 0,
        tms: bool = False,
        zoom_reverse: bool = False,
        detect_retina: bool = False,
        cross_origin: bool | str = False,
        referrer_policy: bool | str = False,
        **kwargs,
    ) -> None:
        super().__init__(min_zoom=min_zoom, max_zoom=max_zoom, **kwargs)
        self.url_template = url_template

        self.subdomains = subdomains
        self.error_tile_url = error_tile_url
        self.zoom_offset = zoom_offset
        self.tms = tms
        self.zoom_reverse = zoom_reverse
        self.detect_retina = detect_retina
        self.cross_origin = cross_origin
        self.referrer_policy = referrer_policy


class WMSTileLayer(TileLayer):
    __render_args__ = ["base_url"]
    __not_render_options__ = TileLayer.__not_render_options__ + __render_args__

    base_url: str
    layers: str = ""
    styles: str = ""
    format: str = "image/png"
    transparent: bool = False
    version: str = "1.1.1"
    uppercase: bool = False

    def __init__(
        self,
        base_url: str,
        layers: str,
        styles: str = "",
        format: str = "image/png",
        transparent: bool = False,
        version: str = "1.1.1",
        uppercase: bool = False,
        **kwargs,
    ) -> None:
        super().__init__("", **kwargs)
        self.base_url = base_url
        self.layers = layers
        self.styles = styles
        self.format = format
        self.transparent = transparent
        self.version = version
        self.uppercase = uppercase

    def __factory_str__(self) -> str:
        return "tileLayer.wms"


class ImageOverlay(InteractiveLayer):
    __render_args__ = ["image_url", "image_bounds"]
    __not_render_options__ = InteractiveLayer.__not_render_options__ + __render_args__

    image_url: str
    bounds: LatLngBounds

    opacity: float = 1.0
    alt: str = ""
    interactive: bool = False
    cross_origin: bool | str = False
    error_overlay_url: str = ""
    z_index: int = 1
    class_name: str = ""

    def __init__(
        self,
        image_url: str,
        bounds: LatLngBounds | list[list[float]],
        opacity: float = 1.0,
        alt: str = "",
        interactive: bool = False,
        cross_origin: bool | str = False,
        error_overlay_url: str = "",
        z_index: int = 1,
        class_name: str = "",
        **kwargs,
    ) -> None:
        super().__init__(interactive=interactive, **kwargs)
        self.image_url = image_url
        self.bounds = (
            bounds if isinstance(bounds, LatLngBounds) else LatLngBounds(*bounds)
        )
        self.opacity = opacity
        self.alt = alt
        self.interactive = interactive
        self.cross_origin = cross_origin
        self.error_overlay_url = error_overlay_url
        self.z_index = z_index
        self.class_name = class_name


class VideoOverlay(ImageOverlay):
    __render_args__ = ["video", "bounds"]
    __not_render_options__ = ImageOverlay.__not_render_options__ + __render_args__

    video: str | list[str]
    bounds: LatLngBounds

    autoplay: bool = True
    loop: bool = True
    keep_aspect_ratio: bool = True
    muted: bool = False
    plays_inline: bool = True

    def __init__(
        self,
        video: str | list[str],
        bounds: LatLngBounds | list[list[float]],
        autoplay: bool = True,
        loop: bool = True,
        keep_aspect_ratio: bool = True,
        muted: bool = False,
        plays_inline: bool = True,
        **kwargs,
    ) -> None:
        super().__init__("", bounds, **kwargs)
        self.video = video
        self.autoplay = autoplay
        self.loop = loop
        self.keep_aspect_ratio = keep_aspect_ratio
        self.muted = muted
        self.plays_inline = plays_inline


class CreatesRasterLayers(HasLayers):
    layers: list[Layer]

    def has_any_raster_layer(self) -> bool:
        for layer in self.layers:
            if layer.__class__.__name__ in RASTER_LAYERS:
                return True
        return False

    def new_tile_layer(
        self,
        url_template: str,
        min_zoom: int = 0,
        max_zoom: int = 18,
        subdomains: str = "abc",
        error_tile_url: str = "",
        zoom_offset: int = 0,
        tms: bool = False,
        zoom_reverse: bool = False,
        detect_retina: bool = False,
        cross_origin: bool | str = False,
        referrer_policy: bool | str = False,
        **kwargs,
    ) -> TileLayer:
        tile_layer = TileLayer(
            url_template,
            min_zoom,
            max_zoom,
            subdomains,
            error_tile_url,
            zoom_offset,
            tms,
            zoom_reverse,
            detect_retina,
            cross_origin,
            referrer_policy,
            **kwargs,
        )
        tile_layer.owner = self
        self.layers.append(tile_layer)
        return tile_layer

    def new_wms_tile_layer(
        self,
        base_url: str,
        layers: str,
        styles: str = "",
        format: str = "image/png",
        transparent: bool = False,
        version: str = "1.1.1",
        uppercase: bool = False,
        **kwargs,
    ) -> WMSTileLayer:
        wms_tile_layer = WMSTileLayer(
            base_url, layers, styles, format, transparent, version, uppercase, **kwargs
        )
        wms_tile_layer.owner = self
        self.layers.append(wms_tile_layer)
        return wms_tile_layer

    def new_image_overlay(
        self,
        image_url: str,
        image_bounds: LatLngBounds | list[list[float]],
        opacity: float = 1.0,
        alt: str = "",
        interactive: bool = False,
        cross_origin: bool | str = False,
        error_overlay_url: str = "",
        z_index: int = 1,
        class_name: str = "",
        **kwargs,
    ) -> ImageOverlay:
        image_overlay = ImageOverlay(
            image_url,
            image_bounds,
            opacity,
            alt,
            interactive,
            cross_origin,
            error_overlay_url,
            z_index,
            class_name,
            **kwargs,
        )
        image_overlay.owner = self
        self.layers.append(image_overlay)
        return image_overlay

    def new_video_overlay(
        self,
        video: str | list[str],
        bounds: LatLngBounds | list[list[float]],
        autoplay: bool = True,
        loop: bool = True,
        keep_aspect_ratio: bool = True,
        muted: bool = False,
        plays_inline: bool = True,
        **kwargs,
    ) -> VideoOverlay:
        video_overlay = VideoOverlay(
            video,
            bounds,
            autoplay,
            loop,
            keep_aspect_ratio,
            muted,
            plays_inline,
            **kwargs,
        )
        video_overlay.owner = self
        self.layers.append(video_overlay)
        return video_overlay
