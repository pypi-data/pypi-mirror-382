from flask_leaflet import Map


def test_new_tile_layer():
    """Test adding a tile layer to map."""
    my_map = Map("test-map", center=[51.505, -0.09], zoom=13)

    tile_layer = my_map.new_tile_layer(
        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", max_zoom=19
    )

    assert tile_layer is not None
    assert len(my_map.layers) > 0


def test_tile_layer_with_options():
    """Test tile layer with custom options."""
    my_map = Map("test-map", center=[51.505, -0.09], zoom=13)

    tile_layer = my_map.new_tile_layer(
        "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        max_zoom=15,
        min_zoom=10,
        attribution="Test Attribution",
    )

    assert tile_layer is not None
