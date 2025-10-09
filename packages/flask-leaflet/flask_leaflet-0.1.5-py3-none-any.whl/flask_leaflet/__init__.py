import warnings
from typing import Callable, Optional

from flask import Blueprint, Flask, render_template
from markupsafe import Markup

from .layers.raster import TileLayer
from .layers.ui import Marker
from .map import Map

__all__ = ("Leaflet", "Map", "Marker")

CSPNonceCallback = Callable[[], str]


class Leaflet:
    app: Optional[Flask]
    css_local_path: Optional[str] = None
    js_local_path: Optional[str] = None

    config: Optional[dict] = None
    default_tile_layer: TileLayer | None = None

    default_icon_marker_url: Optional[str] = None
    default_icon_marker_shadow_url: Optional[str] = None

    __csp_nonce_callback: CSPNonceCallback | None = None

    def __init__(self, app: Optional[Flask] = None) -> None:
        if app is not None:
            self.init_app(app)

    def __register_blueprint(self, app: Flask) -> None:
        blueprint = Blueprint(
            "leaflet",
            __name__,
            template_folder="templates",
            static_folder="static",
            static_url_path="/leaflet/static",
        )
        app.register_blueprint(blueprint)

    def init_app(self, app: Flask) -> None:
        if "leaflet" in app.extensions:
            raise RuntimeError(
                "Leaflet extension is already registered on this Flask app."
            )

        app.extensions["leaflet"] = self

        self.__register_blueprint(app)

        self.css_local_path = app.config.get("LEAFLET_CSS_LOCAL_PATH")
        self.js_local_path = app.config.get("LEAFLET_JS_LOCAL_PATH")
        self.default_icon_marker_url = app.config.get("LEAFLET_MARKER_ICON_URL")
        self.default_icon_marker_shadow_url = app.config.get(
            "LEAFLET_MARKER_ICON_SHADOW_URL"
        )

        url_template: Optional[str] = app.config.get(
            "LEAFLET_DEFAULT_RASTER_TILE_URL_TEMPLATE"
        )
        if url_template:
            tile_options = app.config.get("LEAFLET_DEFAULT_RASTER_TILE_OPTIONS", {})
            self.default_tile_layer = TileLayer(url_template, **tile_options)

        @app.context_processor
        def inject_context_variables() -> dict:
            return dict(leaflet=self)

    def csp_nonce_callback(self, func: CSPNonceCallback) -> None:
        """Define a function that returns a nonce token for script safety

        >>> @csp_nonce_callback
        >>> def get_csp_nonce():
        >>>     ...
        >>>     return random_nonce
        """
        self.__csp_nonce_callback = func

    def load(self) -> Markup:
        return Markup(
            render_template(
                "load.html",
                css_local_path=self.css_local_path,
                js_local_path=self.js_local_path,
                css_version="1.9.3",
                js_version="1.9.3",
                csp_nonce_callback=self.__csp_nonce_callback,
            )
        )

    def render_map(
        self, map: Map, *, class_: str = "", nonce_: Optional[str] = None, **kwargs
    ) -> Markup:
        for key, val in kwargs.items():
            if hasattr(map, key):
                setattr(map, key, val)

        if not map.has_any_raster_layer() and self.default_tile_layer is not None:
            map.layers.append(self.default_tile_layer)
            self.default_tile_layer.owner = map

        html_string = map.__render_html__(class_)
        nonce_tag = f" nonce={nonce_}" if nonce_ else ""
        js_string = Markup(f"<script{nonce_tag}>{str(map.__render_js__())}</script>")
        return html_string + js_string
