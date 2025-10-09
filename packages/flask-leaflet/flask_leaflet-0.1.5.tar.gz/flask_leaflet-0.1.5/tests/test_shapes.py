from flask_leaflet import Map


def test_new_circle():
    """Test adding a circle to map."""
    my_map = Map("test-map", center=[51.505, -0.09], zoom=13)

    circle = my_map.new_circle([51.5, -0.09], radius=500)

    assert circle is not None


def test_circle_with_options():
    """Test circle with custom options."""
    my_map = Map("test-map", center=[51.505, -0.09], zoom=13)

    circle = my_map.new_circle([51.5, -0.09], radius=500, color="red", fill_color="#f03", fill_opacity=0.5)

    assert circle is not None


def test_circle_with_tooltip():
    """Test adding tooltip to circle."""
    my_map = Map("test-map", center=[51.505, -0.09], zoom=13)

    circle = my_map.new_circle([51.5, -0.09], radius=500)
    tooltip = circle.new_tooltip("Circle Tooltip")

    assert tooltip is not None


def test_new_rectangle():
    """Test adding a rectangle to map."""
    my_map = Map("test-map", center=[51.505, -0.09], zoom=13)

    rectangle = my_map.new_rectangle([[51.49, -0.08], [51.51, -0.06]])

    assert rectangle is not None


def test_rectangle_with_popup():
    """Test adding popup to rectangle."""
    my_map = Map("test-map", center=[51.505, -0.09], zoom=13)

    rectangle = my_map.new_rectangle([[51.49, -0.08], [51.51, -0.06]])
    popup = rectangle.new_popup("Rectangle Popup")

    assert popup is not None
