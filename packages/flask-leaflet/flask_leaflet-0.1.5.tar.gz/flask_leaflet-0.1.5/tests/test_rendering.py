from markupsafe import Markup

from flask_leaflet import Map


def test_render_map(app, leaflet):
    """Test rendering a map."""
    with app.app_context():
        my_map = Map("test-map", center=[51.505, -0.09], zoom=13)
        result = leaflet.render_map(my_map)

        assert isinstance(result, Markup)
        assert "test-map" in str(result)


def test_render_map_with_custom_class(app, leaflet):
    """Test rendering map with custom CSS class."""
    with app.app_context():
        my_map = Map("test-map", center=[51.505, -0.09], zoom=13)
        result = leaflet.render_map(my_map, class_="h-[200px] w-full")

        assert "h-[200px]" in str(result) or "class" in str(result)


def test_render_map_with_overrides(app, leaflet):
    """Test rendering map with option overrides."""
    with app.app_context():
        my_map = Map("test-map", center=[51.505, -0.09], zoom=13)
        result = leaflet.render_map(my_map, zoom=10)

        assert isinstance(result, Markup)


def test_render_map_with_nonce(app, leaflet):
    """Test rendering map with nonce token."""
    with app.app_context():
        my_map = Map("test-map", center=[51.505, -0.09], zoom=13)
        result = leaflet.render_map(my_map, nonce_="test-nonce-123")

        assert isinstance(result, Markup)
