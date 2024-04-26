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
sketch = Sketch(
    partstudio=partstudio,  # we pass a reference to the partstudio
    plane=partstudio.features.top_plane,  # we define the plane to draw on
    name="New Sketch",  # and we name the sketch
)

# in this new sketch, we'll draw a circle
sketch.add_circle(center=(0, 0), radius=0.5)  # the default units are inches, 🇺🇸

# that's all we'll add to this sketch. we can add this to the partstudio with:
partstudio.add_feature(sketch)

# next, we'll extrude the sketch. the syntax is similar
extrude = Extrude(
    partstudio=partstudio,  # another partstudio reference
    targets=[sketch],  # we'll extrude the entire sketch ...
    distance=1,  # ... by one inch
)
partstudio.add_feature(extrude)
