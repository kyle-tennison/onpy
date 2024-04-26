from onpy import Client
from onpy.features import Sketch, Extrude


def test_sketch_extrude():
    """Tests the ability to extrude a sketch"""

    client = Client()

    doc = client.create_document(name="test_features::test_sketch_extrude")
    partstudio = doc.get_partstudio(name="Part Studio 1")

    sketch = Sketch(
        partstudio=partstudio, plane=partstudio.features.front_plane, name="Base Sketch"
    )

    # draw a circle
    sketch.add_circle((-1, 0), 1)
    sketch.add_circle((1, 0), 1)

    partstudio.add_feature(sketch)

    extrude = Extrude(
        partstudio=partstudio, targets=[sketch], distance=1, name="new extrude"
    )
    partstudio.add_feature(extrude)

    new_sketch = Sketch(
        partstudio=partstudio,
        plane=partstudio.features.top_plane, name="Second Sketch"
    )

    # a box with an arc
    new_sketch.trace_points(
        (3,4),
        (3,3),
        (4,3)
    )
    new_sketch.add_centerpoint_arc(centerpoint=(3,3), radius=1, start_angle=0, end_angle=90)

    partstudio.add_feature(new_sketch)
    partstudio.add_feature(
        Extrude(partstudio=partstudio, targets=[new_sketch.query_point((3.5, 3.5, 0))], distance=1)
    )

    doc.delete()

def test_sketch_point_query():
    """Test the ability to extrude from a select point in a sketch region"""

    client = Client()

    document = client.create_document("test_features::test_sketch_point_query")
    partstudio = document.get_partstudio()

    sketch = Sketch(
        partstudio=partstudio,
        plane=partstudio.features.top_plane,
        name="Overlapping Sketch",
    )

    sketch.add_circle(center=(-0.5, 0), radius=1)
    sketch.add_circle(center=(0.5, 0), radius=1)

    partstudio.add_feature(sketch)

    extrude = Extrude(
        partstudio=partstudio, targets=[sketch.query_point((0.6, 0, 0))], distance=1
    )
    partstudio.add_feature(extrude)

    document.delete()
