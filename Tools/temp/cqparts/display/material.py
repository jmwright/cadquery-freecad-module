
from ..params import NonNullParameter


# Templates (may be used optionally)
COLOR = {
    # primary colours
    'red': (255, 0, 0),
    'green': (0, 255, 0),
    'blue': (0, 0, 255),
    'cyan': (0, 255, 255),
    'magenta': (255, 0, 255),
    'yellow': (255, 255, 0),

    # woods
    'wood_light': (235, 152, 78),
    'wood': (235, 152, 78),  # == wood_light
    'wood_dark': (169, 50, 38),

    # metals
    'aluminium': (192, 192, 192),
    'aluminum': (192, 192, 192),  # == aluminium
    'steel': (84, 84, 84),
    'steel_blue': (35, 107, 142),
    'copper': (184, 115, 51),
    'silver': (230, 232, 250),
    'gold': (205, 127, 50),
}

TEMPLATE = dict(
    (k, {'color': v, 'alpha': 1})
    for (k, v) in COLOR.items()
)
TEMPLATE.update({
    'default': {'color': COLOR['aluminium'], 'alpha': 1.0},
    'glass': {'color': (200, 200, 255), 'alpha': 0.2},
})


# -------------------- Parameter(s) --------------------
class RenderProps(object):
    """
    Properties for rendering.

    This class provides a :class:`RenderParam` instance
    as a :class:`Parameter <cqparts.params.Parameter>` for a
    :class:`ParametricObject <cqparts.params.ParametricObject>`.

    .. doctest::

        >>> from cqparts.params import ParametricObject
        >>> from cqparts.display.material import RenderParam, TEMPLATE, COLOR
        >>> class Thing(ParametricObject):
        ...     _render = RenderParam(TEMPLATE['red'], doc="render params")
        >>> thing = Thing()
        >>> thing._render.color
        (255, 0, 0)
        >>> thing._render.alpha
        1.0
        >>> thing = Thing(_render={'color': COLOR['green'], 'alpha': 0.5})
        >>> thing._render.color
        (0, 255, 0)
        >>> thing._render.alpha
        0.5
        >>> thing._render.dict
        {'color': (0, 255, 0), 'alpha': 0.5}

    The ``TEMPLATE`` and ``COLOR`` dictionaries provide named templates to
    display your creations quickly, but you can also provide custom properties.
    """

    def __init__(self, color=(200, 200, 200), alpha=1):
        """
        :param color: 3-tuple of RGB in the bounds: ``{0 <= val <= 255}``
        :type color: :class:`tuple`
        :param alpha: object alpha in the range ``{0 <= alpha <= 1}``
                      where ``0`` is transparent, and ``1`` is opaque
        :type alpha: :class:`float`
        """
        self.color = tuple(color)
        self.alpha = max(0., min(float(alpha), 1.))

    @property
    def dict(self):
        """
        Return a :class:`dict` of this instance.
        Can be used to set a property based on the property of another.

        :return: dict of render attributes
        :rtype: :class:`dict`
        """
        return {
            'color': self.color,
            'alpha': self.alpha,
        }

    def __hash__(self):
        hash(frozenset(self.dict.items()))

    def __eq__(self, other):
        return self.dict == other.dict

    def __ne__(self, other):
        return self.dict != other.dict

    @property
    def transparency(self):
        """
        :return: transparency value, 1 is invisible, 0 is opaque
        :rtype: :class:`float`
        """
        return 1. - self.alpha

    @property
    def rgb(self):
        """
        Red, Green, Blue

        :return: red, green, blue values
        :rtype: :class:`tuple`

        synonym for ``color``
        """
        return self.color

    @property
    def rgba(self):
        """
        Red, Green, Blue, Alpha

        :return: red, green, blue, alpha values
        :rtype: :class:`tuple`

        .. doctest::

            >>> from cqparts.display import RenderProps
            >>> r = RenderProps(color=(1,2,3), alpha=0.2)
            >>> r.rgba
            (1, 2, 3, 0.2)
        """
        return self.color + (self.alpha,)

    @property
    def rgbt(self):
        """
        Red, Green, Blue, Transparency

        :return: red, green, blue, transparency values
        :rtype: :class:`tuple`

        .. doctest::

            >>> from cqparts.display import RenderProps
            >>> r = RenderProps(color=(1,2,3), alpha=0.2)
            >>> r.rgbt
            (1, 2, 3, 0.8)
        """
        return self.color + (self.transparency,)

    @property
    def gltf_material(self):
        """
        :return: `glTF Material <https://github.com/KhronosGroup/glTF/tree/master/specification/2.0#materials>`_
        :rtype: :class:`dict`
        """
        # There's a lot of room for improvement here
        return {
            "pbrMetallicRoughness": {
                "baseColorFactor": [round(val / 255., 4) for val in self.rgb] + [self.alpha],
                "metallicFactor": 0.1,
                "roughnessFactor": 0.7,
            },
            'alphaMode': 'MASK',
            'alphaCutoff': 1.0,
            #"name": "red",
        }


class RenderParam(NonNullParameter):
    _doc_type = "kwargs for :class:`RenderProps <cqparts.display.material.RenderProps>`"

    def type(selv, value):
        return RenderProps(**value)

    # Serialize / Deserialize
    @classmethod
    def serialize(cls, value):
        return value.dict


def render_props(**kwargs):
    """
    Return a valid property for cleaner referencing in :class:`Part <cqparts.Part>`
    child classes.

    :param template: name of template to use (any of ``TEMPLATE.keys()``)
    :type template: :class:`str`
    :param doc: description of parameter for sphinx docs
    :type doc: :class:`str`

    :return: render property instance
    :rtype: :class:`RenderParam`

    .. doctest::

        >>> import cadquery
        >>> from cqparts.display import render_props
        >>> import cqparts
        >>> class Box(cqparts.Part):
        ...     # let's make semi-transparent aluminium (it's a thing!)
        ...     _render = render_props(template='aluminium', alpha=0.8)
        >>> box = Box()
        >>> box._render.rgba
        (192, 192, 192, 0.8)

    The tools in :mod:`cqparts.display` will use this colour and alpha
    information to display the part.
    """
    # Pop named args
    template = kwargs.pop('template', 'default')
    doc = kwargs.pop('doc', "render properties")

    params = {}

    # Template parameters
    if template in TEMPLATE:
        params.update(TEMPLATE[template])

    # override template with any additional params
    params.update(kwargs)

    # return parameter instance
    return RenderParam(params, doc=doc)
