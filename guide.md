# OnPy

**A comprehensive, all-in-one guide to modeling in OnPy**

## What is OnPy & What is it for?

OnPy is a Python API for creating 3D models in OnShape, a popular cloud-based CAD tool. OnShape is a parametric tool, meaning that parts are built via a series of _features_. This concept is fundamental to parametric modeling.

OnPy provides the ability to define basic features in Python. Currently, many features are not supported, so all modeling must happen through a few basic features.

OnPy is _not_ intended to create complex designs; it functions entirely to provide a simple interface to OnShape through python. Do not attempt to make complex models using OnPy.

## OnShape Documents

OnShape documents contain everything related to a project. In OnPy, you can fetch or create documents with the following syntax:

```python
import onpy

document = onpy.create_document("my document") # creates a new document

document = onpy.get_document(name="my document") # get a document by name

document = onpy.get_document("5aaf074sd1sabcc2bebb6ecf") # or, reference by id
```

## OnShape Elements

In OnShape, there are a few types of elements, all of which are contained under a single document. If you are familiar with the GUI, elements are effectively the tabs at the bottom of the window. Most commonly, these are partstudios and assemblies, however, they can take other forms.

Because OnPy is intended for simple models, it currently only supports partstudios.

### The Partstudio

In OnShape, the partstudio is the element where all part modeling takes place.
Here, you can control parts and features. A document can have any number of partstudios, but there is usually only one. To get the default partstudio, you can use:

```python
partstudio = document.get_partstudio()
```

This partstudio will be the entry to everything else that happens in OnPy.

## Creating Models

### Overview

As mentioned, in OnPy, only a select number of features are supported. These will be detailed soon. In general, however, use this following logic to guide your project development:

Firstly, start with sketches. Sketches house 2D geometries and are always the starting point for 3D geometries. In OnPy, there are no sketch constraints. Whatever is defined in OnPy code is immutable.

Depending on the circumstance, you can move sketches to other planes using offset planes. These are very useful and can be used extensively. They do not interfere with future geometry in any way.

After you have created a sketch, perform some 3D operation on it. Currently, OnPy only supports extrusions and lofts, but these are powerful in their own right. If your sketch has multiple regions, you can query them based on their properties. Queries will be discussed later.

After you have created a 3D object, also known as a Part, you can perform additional queries and operations on it. You can reference part faces, edges, vertices, etc. in order to define additional sketches.

## Defining a Sketch

Sketches are features that belong to a partstudio. We can create a sketch on our partstudio with:

```python
partstudio.add_sketch(plane=partstudio.features.top_plane, name="My Sketch")
```

Here, we provide the `.add_sketch` method two parameters: a plane to define the plane on, and an optional name for the feature.

> Feature names are always optional. They are visible in the UI and are generally good practice, but do not actually influence the model.

Because we haven't defined any other features yet, we need to select one of the **default planes** to define our first sketch on. In OnShape, there are three default planes, all orthogonal to each other:

1. The top plane, on the x-y axis
2. The front plane, on the x-z axis
3. The right plane, on the y-z axis

We can get a reference to these planes with:

```python
partstudio.features.top_plane
partstudio.features.front_plane
partstudio.features.right_plane
```

In the example above, we create a sketch on the top plane, i.e., on the x-y plane.

### Sketch Items

We build a sketch by using a series of `SketchItem`s. Sketches are made up of:

1. Line segmnets
2. Circles
3. Arcs

> Note, in future releases of OnPy, more sketch items will be added.

From a `Sketch` object, we can add these different objects with a few different methods.

The following are the function signatures for the methods on the sketch object:

```python
def add_circle(
    self,
    center: tuple[float, float],
    radius: float,
    units: UnitSystem | None = None,
) -> SketchCircle:
    """Adds a circle to the sketch

    Args:
        center: An (x,y) pair of the center of the circle
        radius: The radius of the circle
        units: An optional other unit system to use
    """
    ...


def add_line(
    self, start: tuple[float, float], end: tuple[float, float]
) -> SketchLine:
    """Adds a line to the sketch

    Args:
        start: The starting point of the line
        end: The ending point of the line
    """
    ...

def add_centerpoint_arc(
    self,
    centerpoint: tuple[float, float],
    radius: float,
    start_angle: float,
    end_angle: float,
) -> SketchArc:
    """Adds a centerpoint arc to the sketch

    Args:
        centerpoint: The centerpoint of the arc
        radius: The radius of the arc
        start_angle: The angle to start drawing the arc at
        end_angle: The angle to stop drawing the arc at
    """
    ...

def add_fillet(
    self,
    line_1: SketchLine,
    line_2: SketchLine,
    radius: float,
) -> SketchArc:
    """Creates a fillet between two lines by shortening them and adding an
    arc in between. Returns the added arc.

    Args:
        line_1: Line to fillet
        line_2: Other line to fillet
        radius: Radius of the fillet

    Returns
        A SketchArc of the added arc. Updates line_1 and line_2
    """
    ...


def trace_points(
    self, *points: tuple[float, float], end_connect: bool = True
) -> list[SketchLine]:
    """Traces a series of points

    Args:
        points: A list of points to trace. Uses list order for line
        end_connect: Connects end points of the trace with an extra segment
            to create a closed loop. Defaults to True.

    Returns:
        A list of the added SketchLine objects
    """
```

These functions are the primary tools to build sketches, and they should
be used extensively.

However, sometimes complex math is required to describe relationships in sketches.
It would be error prone to attempt to line up values manually, so OnPy
provides a set of tools that allows some basic operations:

These are:

1. Mirroring
2. Translations
3. Rotations
4. Linear Pattern
5. Circular Pattern

You can use these with the following functions. The signatures are shown:

```python
def mirror[T: SketchItem](
    self,
    items: Sequence[T],
    line_point: tuple[float, float],
    line_dir: tuple[float, float],
    copy: bool = True,
) -> list[T]:
    """Mirrors sketch items about a line

    Args:
        items: Any number of sketch items to mirror
        line_point: Any point that lies on the mirror line
        line_dir: The direction of the mirror line
        copy: Whether or not to save a copy of the original entity. Defaults
            to True.

    Returns:
        A lit of the new items added
    """
    ...

def rotate[T: SketchItem](
    self,
    items: Sequence[T],
    origin: tuple[float, float],
    theta: float,
    copy: bool = False,
) -> list[T]:
    """Rotates sketch items about a point

    Args:
        items: Any number of sketch items to rotate
        origin: The point to pivot about
        theta: The degrees to rotate by
        copy: Whether or not to save a copy of the original entity. Defaults
            to False.

    Returns:
        A lit of the new items added
    """
    ...

def translate[T: SketchItem](
    self, items: Sequence[T], x: float = 0, y: float = 0, copy: bool = False
) -> list[T]:
    """Translates sketch items in a cartesian system

    Args:
        items: Any number of sketch items to translate
        x: The amount to translate in the x-axis
        y: The amount to translate in the y-axis
        copy: Whether or not to save a copy of the original entity. Defaults
            to False.

    Returns:
        A lit of the new items added
    """
    ...

def circular_pattern[T: SketchItem](
        self, items: Sequence[T], origin: tuple[float, float], num_steps: int, theta: float
) -> list[T]:
    """Creates a circular pattern of sketch items

    Args:
        items: Any number of sketch items to include in the pattern
        num_steps: The number of steps to take. Does not include original position
        theta: The degrees to rotate per step

    Returns:
        A list of the entities that compose the circular pattern, including the
        original items.
    """
    ...

def linear_pattern[T: SketchItem](
        self, items: Sequence[T], num_steps: int, x: float = 0, y: float =0
) -> list[T]:
    """Creates a linear pattern of sketch items

    Args:
        items: Any number of sketch items to include in the pattern
        num_steps: THe number of steps to take. Does not include original position
        x: The x distance to travel each step. Defaults to zero
        y: The y distance to travel each step. Defaults to zero

    Returns:
        A list of the entities that compose the linear pattern, including the
        original item.
    """
    ...
```

The general idea is to pass sketch items that were previously created and
perform operations on them. When performing operations, you can use the
copy keyword argument to tell OnPy if it should copy the items (and perform
the operation on the copy), or if it should modify the original item.

Consider the following examples:

1. Here, we use the `translate`, and `mirror` operations on SketchItems
   created by `add_centerpoint_arc` and `add_line` to create two hearts.

```python
sketch = partstudio.add_sketch(plane=partstudio.features.top_plane, name="Heart Sketch")

# Define a line and an arc
line = sketch.add_line((0,-1), (1, 1))
arc = sketch.add_centerpoint_arc(centerpoint=(0.5, 1), radius=0.5, start_angle=0, end_angle=180)

# Mirror across vertical axis
new_items = sketch.mirror(items=[line, arc], line_point=(0,0), line_dir=(0,1))

# Translate and copy the entire heart
sketch.translate(
    items=[*new_items, line, arc],
    x=3,
    y=0,
    copy=True
)

# Extrude the heart closest to the origin
heart_extrude = partstudio.add_extrude(sketch.faces.closest_to((0,0,0)), distance=1, name="Heart extrude")
```

2. In this next example, we use the `circular_pattern` tool so create a hexagon,
   and then we use the `add_fillet` method to add fillets on the corners of the
   hexagon.

```python
import math
sketch = partstudio.add_sketch(plane=partstudio.features.top_plane, name="Hexagon Profile")

# Keep a list of hexagon sides
sides = []

# A side of a unit hexagon can be defined as:
hexagon_side = sketch.add_line(
    (-0.5, math.sqrt(3)/2),
    (0.5, math.sqrt(3)/2),
)

# Rotate and copy this side five times to create the full hexagon
sides = hexagon_side.circular_pattern(origin=(0,0), num_steps=5, theta=60)

# Fillet between each side
for i in range(len(sides)):
    side_1 = sides[i-1]
    side_2 = sides[i]

    sketch.add_fillet(side_1, side_2, radius=0.1)

# Add a hole in the middle of the hexagon
sketch.add_circle(center=(0,0), radius=5/32)

# Extrude the part of the sketch that isn't the hole
partstudio.add_extrude(sketch.faces.largest(), distance=3)
```

### Sketch Entities

As you build a OnShape sketch with sketch items, more geometry is being created
under the hood. For instance, when you add a circle and a line to a sketch,
you are actually defining two regions and two new vertices atop the circle
and line.

To differentiate between sketch items added by the user and entities created by
the sketch, OnPy uses two different terminologies:

**Sketch Item**—An item added to the sketch with one of the functions listed above
**Sketch Entity**—An entity that was created as the result of sketch items being
added to the sketch.

> Sketch entities are no different than OnShape entities in general. Other entities, like those that belong to a part, behave exactly the same.

SketchEntities are how the user interacts with a sketch; this is how you can
select which regions to extrude, loft, etc. To select a sketch entity, we use
an `EntityFilter`. The `EntityFilter` is an object that contains a list of
entities (usually of a certain type) with methods that allow us to filter
the entities it contains through different queries.

To get the EntityFilter that contains entities from a sketch, you can use:

```python
sketch.faces # EntityFilter[FaceEntity]
sketch.edges # EntityFilter[EdgeEntity]
sketch.vertices # EntityFilter[VertexEntity]
```

> Entities and entity types are covered later in this document

With an `EntityFilter` object, we can call the following methods to query
the objects it contains. The signatures are shown:

```python
def intersects(
        self, origin: tuple[float, float, float], direction: tuple[float, float, float]
    ) -> "EntityFilter":
    """Get the queries that intersect an infinite line

    Args:
        origin: The origin on the line. This can be any point that lays on
            the line.
        direction: The direction vector of the line
    """
    ...

def smallest(self) -> "EntityFilter":
    """Get the smallest entity"""
    ...

def largest(self) -> "EntityFilter":
    """Get the largest entity"""
    ...

def closest_to(self, point: tuple[float, float, float]) -> "EntityFilter":
    """Get the entity closest to the point

    Args:
        point: The point to use for filtering
    """
    ...

def contains_point(self, point: tuple[float, float, float]) -> "EntityFilter":
    """Filters out all queries that don't contain the provided point

    Args:
        point: The point to use for filtering
    """
    ...
```

Notice how each query returns an EntityFilter object? We can leverage this
behavior to stack multiple queries atop each other. Consider the following
example:

```python
sketch.faces.contains_point((0,0,0)).largest()
```

Here, we first query all of the faces that contain the origin (on the sketch),
then we get the largest of that set. We would not be able to achieve this
behavior with one query.

To apply a query, return the `EntityFilter` object to the corresponding function.

```python
partstudio.add_extrude(faces=leg_sketch.faces, distance=32, name="legs")
```

## Features

Once we have defined a sketch feature, we can continue onto defining more
complex, 3D features. OnPy supports the following features, all of which
are added through the `partstudio` object. The signatures are shown:

```python

def add_sketch(
    self, plane: Plane | FaceEntityConvertible, name: str = "New Sketch"
) -> Sketch:
    """Adds a new sketch to the partstudio

    Args:
        plane: The plane to base the sketch off of
        name: An optional name for the sketch

    Returns:
        A Sketch object
    """
    ...

def add_extrude(
    self,
    faces: FaceEntityConvertible,
    distance: float,
    name: str = "New Extrude",
    merge_with: BodyEntityConvertible | None = None,
    subtract_from: BodyEntityConvertible | None = None,
) -> Extrude:
    """Adds a new blind extrude feature to the partstudio

    Args:
        faces: The faces to extrude
        distance: The distance to extrude
        name: An optional name for the extrusion

    Returns:
        An Extrude object
    """
    ...

def add_loft(
    self,
    start: FaceEntityConvertible,
    end: FaceEntityConvertible,
    name: str = "Loft",
) -> Loft:
    """Adds a new loft feature to the partstudio

    Args:
        start: The start face(s) of the loft
        end: The end face(s) of the loft
        name: An optional name for the loft feature

    Returns:
        A Loft object
    """
    ...

def add_offset_plane(
    self,
    target: Plane | FaceEntityConvertible,
    distance: float,
    name: str = "Offset Plane",
) -> OffsetPlane:
    """Adds a new offset plane to the partstudio

    Args:
        target: The plane to offset from
        distance: The distance to offset
        name: An optional name for the plane

    Returns:
        An OffsetPlane object
    """
    ...

```

> Note, the `FaceEntityConvertible` type identifies that the object can be converted into a list of face entities. `Sketch` and `EntityFilter` are both subclasses of this type.

Before adding a new feature, check here for the function signature. Most are similar, but there
are some subtle differences.

Examples for adding features are shown below.

### Extrusions

Extrusions are the most basic of 3D operations. They allow you to pull a 2D shape by a linear distance
to create a 3D shape.

OnShape supports three types of extrusions:

1. New Extrusion
2. Add Extrusions
3. Subtract Extrusions

New extrusions _always_ create a new part. Parts will be discussed in more
detail later.

Add extrusions _add_ geometry to an existing part. In OnPy, you can add
to an existing part by passing it to the `merge_with` parameter. If you
try to add geometry that does not touch the existing part, OnShape will throw an
error. Each part must be one, continuous body; no disconnections are allowed.

Subtract extrusions _remove_ geometry from an existing part. In OnPy, you can
subtract from a part by passing it to the `subtract_from` parameter. By default,
all extrusions are blind, i.e., you specify how "deep" to extrude/cut. If you
want to preform a through cut, you should provide a large value to the
distance parameter.

The following example shows how a user can use extrusions to create a moderately
complex part:

```python
sketch = partstudio.add_sketch(plane=partstudio.features.top_plane, name="Main Sketch")

# create a 2x10 bar
lines = sketch.trace_points(
    (-5, -1), (-5,1), (5, 1), (5, -1), end_connect=True
)

# fillet the sides of the bar
for i in range(len(lines)):
    side_1 = lines[i-1]
    side_2 = lines[i]

    sketch.add_fillet(side_1, side_2, radius=0.1)

# add holes every half inch, starting at (-4, 0)
hole_profile = sketch.add_circle(center=(-4, 0), radius=0.125)
sketch.linear_pattern([hole_profile], num_steps=15, x=0.5)

# add a line through the center
sketch.add_line((0, -5), (0, 5))

# extrude the left part of the bar by 1 inch
extrusion_left = partstudio.add_extrude(
    faces=sketch.faces.closest_to((-100,0,0)), # pick the furthest left region
    distance=2,
    name="Left Extrude"
    )

# get a reference to the new part
bar_part = extrusion_left.get_created_parts()[0]

# extrude the right side by 1.25 inches and add it to the first part
extrusion_right = partstudio.add_extrude(
    faces=sketch.faces.closest_to((100,0,0)), # pick the furthest right region
    distance=1.25,
    merge_with=bar_part, # <-- add to the bar part
    name="Right Extrude",
    )

# create a new sketch on top of the part
sketch_on_part = partstudio.add_sketch(
    plane=bar_part.faces.closest_to((0,0,100)), # get the highest face
    name="Sketch on part"
)

# draw a slot
sketch_on_part.add_corner_rectangle((-5, 0.25), (5, -0.25))

# cut extrude this slot into the existing slot
cut_extrude = partstudio.add_extrude(
    faces=sketch_on_part,
    distance=-1, # <-- flip the direction of the extrude using a negative sign
    subtract_from=bar_part, # <-- subtract from the bar part
    name="Slot cut"
)
```

### Offset Plane

In OnShape, planes are construction geometry; they are used to define models,
but are not part of the model itself. Offset planes allow you to create a new plane
based off another plane.

The following example shows how to create and reference an offset plane. On their
own, these planes are not very useful, but they are integral to using more advanced
features like Lofts.

```python
offset_plane = partstudio.add_offset_plane(
    target=partstudio.features.top_plane, # <-- based on the default top plane
    distance=3.0 # offset by a distance of 3 inches
    )

bottom_sketch = partstudio.add_sketch(plane=partstudio.features.top_plane, name="Bottom Profile")
top_sketch = partstudio.add_sketch(
    plane=offset_plane # <-- create this sketch on the offset plane
)

bottom_sketch.add_circle((0,0), radius=2)
top_sketch.add_circle((0,0), radius=0.1)

partstudio.add_loft(bottom_sketch, top_sketch) # loft between the two sketches, offset by the offset plane
```

Here, we create an offset plane. We add one sketch to it, and another sketch
on the default plane under it. Then, because these sketches are offset, we can loft between these
two profiles.

### Lofts

Lofts are an easy way to create a solid that extends between two offset
profiles. These profiles must be orthogional, but they can be apart by any
distance.

Lofts are usually used to loft between one profile to another, but sometimes
they can split into multiple profiles. However, this is discouraged as it
often leads to feature errors.

Lofts take two parameters, start and end, with a third, optional name parameter.
The example above in the "Offset Plane" section exemplifies how to use lofts.

## Parts

Sometimes, features will result in a new part. For instance, when you extrude a sketch for the first time, a new part is made.
We will often want to reference this part so that we can query it's faces and entities to create even more complex geometries.

To get the part(s) created by a feature, you can run the `.get_created_parts()` function. This returns a list of Part objects.

If you want to get a list of all parts in a partstudio, you can run `partstudio.parts`. This returns an object used to interface
with parts. If you want to get an idea of what parts are available, you can run:

```txt
>>> print(partstudio.parts)
+-------+----------------+---------+
| Index |   Part Name    | Part ID |
+-------+----------------+---------+
|   0   | Bearing Holder |   JKD   |
|   1   |  Impact Plate  |   JPD   |
|   2   |    Housing     |   JVD   |
+-------+----------------+---------+
```

This will display the parts available. Then, you can access the parts by index (`partstudio.parts[0]`),
name (`partstudio.parts.get("Housing")`), or id (`partstudio.parts.get_id("JKD")`)

If you want to manually iterate over a list of parts, you can call `partstudio.list_parts()`
and this will return a plain list of Part objects.

## Example Model

Using everything discussed so far, let's see OnPy in work. This script
will use many of the features we discussed to create a tri-part lamp model.

```python
import onpy

document = onpy.create_document("Lamp Example")
partstudio = document.get_partstudio()

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
```
