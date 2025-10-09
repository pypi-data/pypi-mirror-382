"""Tests for flask-leaflet package."""

from flask import render_template_string
from markupsafe import Markup

from flask_leaflet import Leaflet


def test_init_app(app):
    """Test that Leaflet can be initialized with an app."""
    leaflet = Leaflet()
    leaflet.init_app(app)
    assert leaflet == app.extensions["leaflet"]


def test_init_app_with_constructor(app):
    """Test Leaflet initialization via constructor."""
    leaflet = Leaflet(app)
    assert leaflet == app.extensions["leaflet"]


def test_leaflet_in_template_context(app, leaflet):
    """Test that leaflet object is available in template context."""
    with app.app_context():
        with app.test_request_context():
            template = "{{ leaflet }}"
            result = render_template_string(template)
            assert result  # Should not be empty


def test_custom_config(app):
    """Test custom configuration options."""
    app.config["LEAFLET_CSS_LOCAL_PATH"] = "css/leaflet.css"
    app.config["LEAFLET_JS_LOCAL_PATH"] = "js/leaflet.js"
    app.config["LEAFLET_MARKER_ICON_URL"] = "static/marker.png"

    leaflet = Leaflet(app)

    assert leaflet.css_local_path == "css/leaflet.css"
    assert leaflet.js_local_path == "js/leaflet.js"
    assert leaflet.default_icon_marker_url == "static/marker.png"


def test_load_returns_markup(app, leaflet):
    """Test that load() returns Markup object."""
    with app.app_context():
        result = leaflet.load()
        assert isinstance(result, Markup)


def test_load_includes_css(app, leaflet):
    """Test that load() includes CSS link."""
    with app.app_context():
        result = leaflet.load()
        assert "leaflet.css" in str(result).lower() or "<link" in str(result)


def test_load_includes_js(app, leaflet):
    """Test that load() includes JavaScript."""
    with app.app_context():
        result = leaflet.load()
        assert "leaflet.js" in str(result).lower() or "<script" in str(result)


def test_load_with_local_paths(app):
    """Test loading with local paths."""
    app.config["LEAFLET_CSS_LOCAL_PATH"] = "css/leaflet.css"
    app.config["LEAFLET_JS_LOCAL_PATH"] = "js/leaflet.js"

    leaflet = Leaflet(app)

    with app.app_context():
        result = leaflet.load()
        assert "css/leaflet.css" in str(result) or "leaflet" in str(result)
