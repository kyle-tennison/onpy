# A preliminary example of how this module should look

from pyshpae import Client
from pyshape.features.sketch import Sketch
from pyshape.features.extrude import Extrude

client = Client()

document = client.create_document("my example")
partstudio = document.create_partstudio("Part Studio 1", units="inch")

# Add sketch
base_sketch = Sketch(
    partstudio=partstudio, plane=partstudio.features.front_plane, name="Base Sketch"
)
base_sketch.add_circle(center=(0, 1), radius=5)
base_sketch.add_circle(center=(0, 1), radius=2)

part_studio.add_feature(base_sketch)

print(part_studio.features)

"""
[
    Plane("Front Plane")
    Plane("Right Plane")
    Plane("Top Plane")
    Sketch("Base Sketch")
]
"""

# Extrude Sketch
base_extrusion = Extrude(base_sketch.regions[0], type="BLIND", distance=0.5)