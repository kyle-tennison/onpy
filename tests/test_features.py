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
        targets=new_sketch.queries.contains_point((3.5, 3.5, 0)),
        distance=1,
    )

    # test extrude on a new plane
    new_plane = partstudio.add_offset_plane(
        target=partstudio.features.top_plane, distance=3
    )
    offset_sketch = partstudio.add_sketch(new_plane)
    offset_sketch.add_circle((0, 0), 1)
    partstudio.add_extrude(
        targets=offset_sketch.queries.contains_point((0, 0, 3)), distance=-3
    )

    # try to extrude between the sketches
    partstudio.add_loft(sketch.queries.largest(), offset_sketch.queries.largest())


    doc.delete()


def test_sketch_queries():
    """Test the ability to query sketch regions"""

    document = Client().create_document("test_features::test_sketch_queries")

    partstudio = document.get_partstudio()
    partstudio.wipe()

    sketch = partstudio.add_sketch(plane=partstudio.features.top_plane)
    sketch.trace_points((-2, -2), (-2, 2), (2, 2), (2, -2))
    sketch.add_circle(center=(0, 0), radius=1)

    sketch.add_line((-2, -1), (2, 2))

    print(sketch.queries.contains_point((1, -1, 0)))

    partstudio.add_extrude(targets=sketch.queries.largest(), distance=1)
    partstudio.add_extrude(targets=sketch.queries.smallest(), distance=0.5)
    partstudio.add_extrude(
        targets=sketch.queries.contains_point((0, 0, 0)), distance=-3
    )

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


def test_pseudo_elements():
    """Tests the ability to mirror, rotate, and translate items, along with
    pseudo elements like fillets."""

    document = Client().create_document("test_features::test_pseudo_elements")
    partstudio = document.get_partstudio()

    partstudio.wipe()

    sketch = partstudio.add_sketch(plane=partstudio.features.top_plane)

    lines = sketch.trace_points((-1, 0), (-0.5, 1), (0.5, 1), end_connect=False)
    fillet_arc = sketch.add_fillet(lines[0], lines[1], radius=0.2)
    main_arc = sketch.add_centerpoint_arc(
        centerpoint=(0.5, 0), radius=1, start_angle=0, end_angle=90
    )

    sketch.mirror(*lines, fillet_arc, main_arc, line_point=(0, 0), line_dir=(1, 0))

    sketch.translate(*sketch.entities, x=1, y=1)
    sketch.rotate(*sketch.entities, origin=(0, 0), theta=180)
    partstudio.add_extrude(
        targets=sketch.queries.contains_point((-1, -1, 0)), distance=1
    )

    document.delete()
