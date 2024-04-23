from pyshape import Client
from pyshape.features.sketch import Sketch

client = Client()

doc = client.get_document(id="f777e86638feb16f2a2925c6")
partstudio = doc.get_partstudio(name="Part Studio 1")

sketch = Sketch(
    partstudio=partstudio, plane=partstudio.features.front_plane, name="Base Sketch"
)

sketch.add_circle((-1, 0), 1)
sketch.add_circle((1, 0), 1)

partstudio.add_feature(sketch)
