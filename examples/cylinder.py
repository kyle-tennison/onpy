"""

In this example, we draw a circle, then extrude it. Simple enough.

"""

from onpy import Client
from onpy.features import Sketch, Extrude

client = Client()  # we use the client object as the entry-point to OnShape

# we'll create a new document, then reference the default partstudio
document = client.create_document("Cylinder Example")
partstudio = document.get_partstudio()

# now, we'll define a sketch
sketch = partstudio.add_sketch(
    plane=partstudio.features.top_plane,  # we define the plane to draw on
    name="New Sketch",  # and we name the sketch
)

# in this new sketch, we'll draw a circle
sketch.add_circle(center=(0, 0), radius=0.5)  # the default units are inches

# next, we'll extrude the sketch. the syntax is similar
extrude = partstudio.add_extrude(
    faces=sketch,  # we'll extrude the entire sketch ...
    distance=1,  # ... by one inch
)
