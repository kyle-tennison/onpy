# A preliminary example of how this module should look

from onpy import Client
from onpy.features.sketch import Sketch
from onpy.features.extrude import Extrude

# from onpy.features.extrude import Extrude

client = Client()

document = client.create_document("my example")
partstudio = document.get_partstudio()

# Add sketch
base_sketch = Sketch(
    partstudio=partstudio, plane=partstudio.features.front_plane, name="Base Sketch"
)
base_sketch.add_circle(center=(0, 1), radius=5)
base_sketch.add_circle(center=(0, 1), radius=2)

partstudio.add_feature(base_sketch)

print(partstudio.features)

"""
[
    Plane("Front Plane")
    Plane("Right Plane")
    Plane("Top Plane")
    Sketch("Base Sketch")
]
"""

# Extrude Sketch

extrude_region = base_sketch.query_region(point=(0, 0))

base_extrusion = Extrude(base_sketch.extrude_region, type="BLIND", distance=0.5)
