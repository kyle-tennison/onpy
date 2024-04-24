from pyshape import Client
from pyshape.features import Sketch, Extrude


def test_sketch_extrude():
    """Tests the ability to extrude a sketch"""

    client = Client()

    doc = client.create_document(name="test_features::test_sketch_extrude")
    partstudio = doc.get_partstudio(name="Part Studio 1")

    sketch = Sketch(
        partstudio=partstudio, plane=partstudio.features.front_plane, name="Base Sketch"
    )

    sketch.add_circle((-1, 0), 1)
    sketch.add_circle((1, 0), 1)

    partstudio.add_feature(sketch)

    extrude = Extrude(
        partstudio=partstudio, targets=[sketch], distance=1, name="new extrude"
    )

    partstudio.add_feature(extrude)

    doc.delete()
