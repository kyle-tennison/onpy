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

#### Overview

As mentioned, in OnPy, only a select number of features are supported. These will be detailed soon. In general, however, use this following logic to guide your project development:

Firstly, start with sketches. Sketches house 2D geometries and are always the starting point for 3D geometries. In OnPy, there are no sketch constraints. Whatever is defined in OnPy code is immutable.

Depending on the circumstance, you can move sketches to other planes using offset planes. These are very useful and can be used extensively. They do not interfere with future geometry in any way.

After you have created a sketch, perform some 3D operation on it. Currently, OnPy only supports extrusions and lofts, but these are powerful in their own right. If your sketch has multiple regions, you can query them based on their properties. Queries will be discussed later.

After you have created a 3D object, also known as a Part, you can perform additional queries and operations on it. You can reference part faces, edges, vertices, etc. in order to define additional sketches.

### Defining a Sketch

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

#### Sketch Items

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

You can use these with the following functions. The signatures are shown:

```python
def mirror(
    self,
    *items: SketchItem,
    line_point: tuple[float, float],
    line_dir: tuple[float, float],
    copy: bool = True,
) -> list[SketchItem]:
    """Mirrors sketch items about a line

    Args:
        *items: Any number of sketch items to mirror
        line_point: Any point that lies on the mirror line
        line_dir: The direction of the mirror line
        copy: Whether or not to save a copy of the original entity. Defaults
            to True.

    Returns:
        A lit of the new items added
    """
    ...

def rotate(
    self,
    *items: SketchItem,
    origin: tuple[float, float],
    theta: float,
    copy: bool = False,
) -> list[SketchItem]:
    """Rotates sketch items about a point

    Args:
        *items: Any number of sketch items to rotate
        origin: The point to pivot about
        theta: The degrees to rotate by
        copy: Whether or not to save a copy of the original entity. Defaults
            to False.

    Returns:
        A lit of the new items added
    """
    ...

def translate(
    self, *items: SketchItem, x: float = 0, y: float = 0, copy: bool = False
) -> list[SketchItem]:
    """Translates sketch items in a cartesian system

    Args:
        *items: Any number of sketch items to translate
        x: The amount to translate in the x-axis
        y: The amount to translate in the y-axis
        copy: Whether or not to save a copy of the original entity. Defaults
            to False.

    Returns:
        A lit of the new items added
    """
    ...
```

The general idea is to pass sketch items that were previously created and
perform operations on them. When performing operations, you can use the
copy keyword argument to tell OnPy if it should copy the items (and perform
the operation on the copy), or if it should modify the original item.

#### Sketch Entities

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
    """Gets the queries that intersect an infinite line

    Args:
        origin: The origin on the line. This can be any point that lays on
            the line.
        direction: The direction vector of the line
    """
    ...

def smallest(self) -> "EntityFilter":
    """Gets the smallest entity"""
    ...

def largest(self) -> "EntityFilter":
    """Gets the largest entity"""
    ...

def closest_to(self, point: tuple[float, float, float]) -> "EntityFilter":
    """Gets the entity closest to the point

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

### Features

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

### Parts

Sometimes, features will result in a new part. For instance, when you extrude a sketch for the first time, a new part is made.
We will often want to reference this part so that we can query it's faces and entities to create even more complex geometries.

To get the part(s) created by a feature, you can run the `.get_created_parts()` function. This returns a list of Part objects.

If you want to get a list of all parts in a partstudio, you can run `partstudio.parts`. This returns an object used to interface
with parts. If you want to get an idea of what parts are available, you can run:

```
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

### Example Model

Using everything discussed so far, let's see OnPy in work. This script will
create a new document

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
