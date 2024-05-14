import onpy

document = onpy.create_document("Lamp Example")
partstudio = document.get_partstudio()
partstudio.wipe()


# Create the lamp base
lower_base_sketch = partstudio.add_sketch(
    plane=partstudio.features.top_plane, name="Base Bottom Sketch"
)
lower_base_sketch.add_corner_rectangle(corner_1=(-2.5, -2.5), corner_2=(2.5, 2.5))

# Create an offset plane 1.25 inches above the lower base sketch
upper_base_plane = partstudio.add_offset_plane(
    target=partstudio.features.top_plane, distance=1.25, name="Upper Base Plane"
)

# Then, make a new sketch on this new plane
upper_base_sketch = partstudio.add_sketch(
    plane=upper_base_plane, name="Upper Base Sketch"
)

# Add a slightly smaller rectangle on this elevated plane
upper_base_sketch.add_corner_rectangle(corner_1=(-2.25, -2.25), corner_2=(2.25, 2.25))

# Then, create a loft to blend the two base profiles to get a model bottom
loft = partstudio.add_loft(
    start=lower_base_sketch, end=upper_base_sketch, name="Base Loft"
)

# Next, create a sketch with a circle to represent the lamp rod
rod_profile = partstudio.add_sketch(plane=partstudio.features.top_plane)
rod_profile.add_circle(center=(0, 0), radius=0.5)

# First, cut a hole through the base
partstudio.add_extrude(
    faces=rod_profile,
    distance=2,  # a bit excess, just to be safe
    subtract_from=loft.get_created_parts()[0],
)

# Then, extrude up 15 inches
rod_extrude = partstudio.add_extrude(faces=rod_profile, distance=15, name="Lamp Rod")
rod = rod_extrude.get_created_parts()[0]  # save a reference to the part

# Get a reference to the top of the rod
top_of_rod = rod.faces.closest_to((0, 0, 100))

# ... then, create a new sketch off of it
lampshade_top = partstudio.add_sketch(plane=top_of_rod, name="Lampshade Top Profile")

# Go down 4.5 inches and create another sketch
lampshade_bottom = partstudio.add_sketch(
    plane=partstudio.add_offset_plane(target=lampshade_top.plane, distance=-4.5),
    name="Lampshade Bottom Profile",
)

# Add a small circle on top and a larger one on the bottom to create a taper
lampshade_top.add_circle(center=(0, 0), radius=3)
lampshade_bottom.add_circle(center=(0, 0), radius=4)

# Loft between the two profiles to create a lampshade
lampshade_loft = partstudio.add_loft(
    start=lampshade_bottom, end=lampshade_top, name="Lampshade Loft"
)
