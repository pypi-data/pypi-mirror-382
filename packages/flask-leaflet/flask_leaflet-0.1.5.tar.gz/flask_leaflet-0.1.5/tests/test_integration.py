from markupsafe import Markup

from flask_leaflet import Map


def test_full_map_workflow(app, leaflet):
    """Test complete map creation and rendering workflow."""
    with app.app_context():
        # Create map
        my_map = Map("integration-test", center=[-41.139416, -73.025431], zoom=16)

        # Add tile layer
        my_map.new_tile_layer(
            "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", max_zoom=19
        )

        # Add marker with popup and tooltip
        marker = my_map.new_marker([-41.139416, -73.025431])
        marker.new_tooltip("Test Location")
        marker.new_popup("<b>Integration Test</b>")

        # Add shapes
        circle = my_map.new_circle([-41.139416, -73.025431], radius=100)
        circle.new_tooltip("Circle Area")

        rectangle = my_map.new_rectangle([[-41.140, -73.026], [-41.138, -73.024]])
        rectangle.new_popup("Rectangle Area")

        # Render map
        result = leaflet.render_map(my_map, class_="h-[400px]")

        assert isinstance(result, Markup)
        assert "integration-test" in str(result)


def test_multiple_maps(app, leaflet):
    """Test rendering multiple maps on same page."""
    with app.app_context():
        map1 = Map("map-1", center=[51.505, -0.09], zoom=13)
        map2 = Map("map-2", center=[40.712, -74.006], zoom=12)

        result1 = leaflet.render_map(map1)
        result2 = leaflet.render_map(map2)

        assert "map-1" in str(result1)
        assert "map-2" in str(result2)
        assert result1 != result2
