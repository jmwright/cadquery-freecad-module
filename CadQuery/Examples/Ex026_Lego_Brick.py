# This example is meant to be used from within the CadQuery module of FreeCAD.
# This script can create any regular rectangular Lego(TM) Brick
import cadquery
import Part

#####
# Inputs
######
lbumps = 1       # number of bumps long
wbumps = 1        # number of bumps wide
thickness = 3.2   # this is a thin lego
# thickness = 9.6 # a thick lego

#
# Lego Brick Constants-- these make a lego brick a lego :)
#
pitch = 8.0
clearance = 0.1
height = 3.2
bumpDiam = 4.8
bumpHeight = 1.8

t = (pitch - (2 * clearance) - bumpDiam) / 2.0
postDiam = pitch - t  # works out to 6.5
total_length = lbumps*pitch - 2.0*clearance
total_width = wbumps*pitch - 2.0*clearance

# make the base
s = cadquery.Workplane("XY").box(total_length, total_width, height)

# shell inwards not outwards
s = s.faces("<Z").shell(-1.0 * t)

# make the bumps on the top
s = s.faces(">Z").workplane(). \
    rarray(pitch, pitch, lbumps, wbumps, True).circle(bumpDiam / 2.0) \
    .extrude(bumpHeight)

# add posts on the bottom. posts are different diameter depending on geometry
# solid studs for 1 bump, tubes for multiple, none for 1x1
tmp = s.faces("<Z").workplane(invert=True)

if lbumps > 1 and wbumps > 1:
    tmp = tmp.rarray(pitch, pitch, lbumps - 1, wbumps - 1, center=True). \
        circle(postDiam / 2.0).circle(bumpDiam / 2.0).extrude(height - t)
elif lbumps > 1:
    tmp = tmp.rarray(pitch, pitch, lbumps - 1, 1, center=True). \
        circle(t).extrude(height - t)
elif wbumps > 1:
    tmp = tmp.rarray(pitch, pitch, 1, wbumps - 1, center=True). \
        circle(t).extrude(height - t)
else:
    tmp = s

Part.show(tmp.toFreecad())
