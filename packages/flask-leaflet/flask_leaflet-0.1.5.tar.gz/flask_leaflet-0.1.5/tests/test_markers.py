from flask_leaflet import Map


def test_new_marker():
    """Test adding a marker to map."""
    my_map = Map("test-map", center=[51.505, -0.09], zoom=13)

    marker = my_map.new_marker([51.5, -0.09])

    assert marker is not None


def test_marker_with_options():
    """Test marker with custom options."""
    my_map = Map("test-map", center=[51.505, -0.09], zoom=13)

    marker = my_map.new_marker([51.5, -0.09], opacity=0.8)

    assert marker is not None


def test_marker_with_tooltip():
    """Test adding tooltip to marker."""
    my_map = Map("test-map", center=[51.505, -0.09], zoom=13)

    marker = my_map.new_marker([51.5, -0.09])
    tooltip = marker.new_tooltip("Test Tooltip")

    assert tooltip is not None


def test_marker_with_popup():
    """Test adding popup to marker."""
    my_map = Map("test-map", center=[51.505, -0.09], zoom=13)

    marker = my_map.new_marker([51.5, -0.09])
    popup = marker.new_popup("<b>Test Popup</b>")

    assert popup is not None
