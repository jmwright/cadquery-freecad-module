# Applying a Fastener

This `fasteners` collection has some utilities to automatically apply and select
an apropriate fastener. What they do, and how to use them is documented below.

Using these tools is **not mandatory**; you'll always have the option to
explicitly select your fastener with the placement and orientation of your
choosing.


## Evaluation

An evaluation is an assessment of the workpieces intended to be fastened along
a given vector.
An evaluation is required for a fastener selector, and an applicator.
If a fastener selector is used to fine an appropriate fastener, that same evaluation
can be passed to the applicator.

Evaluations are given, the _what_, and the _where_:
- _what_: list of parts (those that may be effected, should be as short as possible)
- _where_: linear edge, a vector along which the fastener is intended to be applied

A successful evaluation will yield:
- list of parts effected (in order)
- start & finish points on each effected part
    (the start being closer to the head)

There are 2 methods of evaluation
- vector : faster, but may miss something
- cylindrical : slower, but will find all interfacing solids


```python
# TODO: sample eval code
```


## Fastener Selector

An evaluation can be used to determine which fastener you need.
Or simply, how long the thread on your chosen fastener needs to be.

```python
# TODO: sample selector code
```


## Fastener Application

So you have the fastener to apply, and the workpieces to attach, the workpieces
just need holes.

```python
from cqparts.search import find
screw = find('10g_30mm_CS_PHIL')()
# TODO:
box = Box()  # FIXME
plate = Plate()  # FIXME
screw.apply()
```
