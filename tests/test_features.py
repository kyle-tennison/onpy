from onpy import Client
from onpy.features import Sketch, Extrude
from onpy.api.versioning import WorkspaceWVM


def test_sketch_extrude():
    """Tests the ability to extrude a sketch"""

    client = Client()

    doc = client.create_document(name="test_features::test_sketch_extrude")
    partstudio = doc.get_partstudio(name="Part Studio 1")

    # draw a circle
    sketch = partstudio.add_sketch(
        plane=partstudio.features.front_plane, name="Base Sketch"
    )
    sketch.add_circle((-1, 0), 1)
    sketch.add_circle((1, 0), 1)

    partstudio.add_extrude(targets=[sketch], distance=1, name="new extrude")

    new_sketch = partstudio.add_sketch(
        plane=partstudio.features.top_plane, name="Second Sketch"
    )

    # a box with an arc
    new_sketch.trace_points((3, 4), (3, 3), (4, 3))
    new_sketch.add_centerpoint_arc(
        centerpoint=(3, 3), radius=1, start_angle=0, end_angle=90
    )

    partstudio.add_extrude(
        targets=[new_sketch.query_point((3.5, 3.5, 0))],
        distance=1,
    )

    doc.delete()


def test_sketch_point_query():
    """Test the ability to extrude from a select point in a sketch region"""

    client = Client()

    document = client.create_document("test_features::test_sketch_point_query")
    partstudio = document.get_partstudio()

    sketch = partstudio.add_sketch(
        plane=partstudio.features.top_plane,
        name="Overlapping Sketch",
    )

    sketch.add_circle(center=(-0.5, 0), radius=1)
    sketch.add_circle(center=(0.5, 0), radius=1)

    partstudio.add_extrude(targets=[sketch.query_point((0.6, 0, 0))], distance=1)

    document.delete()


def test_feature_wipe():
    """Test the ability to remove features"""

    client = Client()

    document = client.create_document("test_features::test_feature_wipe")
    partstudio = document.get_partstudio()

    # add dummy feature(s)
    sketch = partstudio.add_sketch(
        plane=partstudio.features.top_plane,
        name="Overlapping Sketch",
    )
    sketch.add_circle(center=(-0.5, 0), radius=1)
    sketch.add_circle(center=(0.5, 0), radius=1)
    partstudio.add_extrude(targets=[sketch], distance=1)

    partstudio.wipe()

    features = client._api.endpoints.list_features(
        document_id=document.id,
        version=WorkspaceWVM(document.default_workspace.id),
        element_id=partstudio.id,
    )

    assert len(features) == 0

    document.delete()
