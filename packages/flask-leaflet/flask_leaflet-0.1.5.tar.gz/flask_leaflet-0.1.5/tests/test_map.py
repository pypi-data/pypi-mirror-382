from flask_leaflet import Map


def test_map_creation():
    """Test basic map creation."""
    my_map = Map("test-map", center=[51.505, -0.09], zoom=13)

    assert my_map.id == "test-map"
    assert my_map.center.as_tuple() == (51.505, -0.09, None)
    assert my_map.zoom == 13


def test_map_with_defaults():
    """Test map creation with default values."""
    my_map = Map("test-map")

    assert my_map.id == "test-map"
    assert hasattr(my_map, "center")
    assert hasattr(my_map, "zoom")


def test_map_snake_case_options():
    """Test that snake_case options work."""
    my_map = Map(
        "test-map",
        center=[51.505, -0.09],
        zoom=13,
        zoom_control=True,
        scroll_wheel_zoom=False,
    )

    assert my_map.zoom == 13
