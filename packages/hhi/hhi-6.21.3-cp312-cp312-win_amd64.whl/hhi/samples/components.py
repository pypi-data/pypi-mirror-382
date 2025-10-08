from functools import partial

import gdsfactory as gf
from gdsfactory.add_pins import add_pins_inside2um

from hhi import PDK

cell = gf.cell
layer_bbox = (55, 0)
layer_bbmetal = None
layer_pin_label = (1001, 0)
layer_pin = (1002, 0)
layer_pin_optical = (1003, 0)
layer_pin_electrical = (1004, 0)
layer_label = (56, 0)

add_pins = partial(add_pins_inside2um, layer_label=layer_label, layer=layer_pin_optical)
layer_text = (59, 0)
text_function = gf.partial(
    gf.components.text, layer=layer_text, justify="center", size=2.0
)

cell = gf.partial(gf.cell, set_name=False)


# This may be added to the hhi pdk at some point. For now, it lives here
@cell
def JonnysDevice() -> gf.Component:
    """."""
    c = gf.Component()
    c.add_polygon(
        [[0.0, 60.0], [700.0, 60.0], [700.0, -60.0], [0.0, -60.0]], layer=layer_bbox
    )
    name = "JonnysDevice"
    c.add_port(
        name="o1",
        width=2.0,
        cross_section="ACT",
        center=(0.0, 6.5),
        orientation=180,
        port_type="optical",
    )
    c.add_label(
        text="alias: InOut\ndoc: optical I/O\nwidth: 2.0\nxsection: ACT\nxya:\n- 0.0\n- 6.5\n- 180\nname: o1\n",
        position=(0.0, 6.5),
        layer=layer_pin_label,
    )
    c.add_port(
        name="o2",
        width=2.0,
        cross_section="ACT",
        center=(700.0, 6.5),
        orientation=0,
        port_type="optical",
    )
    c.add_label(
        text="alias: InOut\ndoc: optical I/O\nwidth: 2.0\nxsection: ACT\nxya:\n- 700.0\n- 6.5\n- 0\nname: o2\n",
        position=(700.0, 6.5),
        layer=layer_pin_label,
    )
    c.add_port(
        name="o3",
        width=2.0,
        cross_section="ACT",
        center=(0.0, -6.5),
        orientation=180,
        port_type="optical",
    )
    c.add_label(
        text="alias: InOut\ndoc: optical I/O\nwidth: 2.0\nxsection: ACT\nxya:\n- 0.0\n- -6.5\n- 180\nname: o3\n",
        position=(0.0, -6.5),
        layer=layer_pin_label,
    )
    c.add_port(
        name="o4",
        width=2.0,
        cross_section="ACT",
        center=(700.0, -6.5),
        orientation=0,
        port_type="optical",
    )
    c.add_label(
        text="alias: InOut\ndoc: optical I/O\nwidth: 2.0\nxsection: ACT\nxya:\n- 700.0\n- -6.5\n- 0\nname: o4\n",
        position=(700.0, -6.5),
        layer=layer_pin_label,
    )

    c.add_port(
        name="p1",
        cross_section="DC",
        center=(310, 60.0),
        orientation=90,
        port_type="electrical",
    )
    c.add_label(
        text="alias: In\ndoc: p-contact 0\nwidth: 16.0\nxsection: DC\nxya:\n- L_B/2\n- 60.0\n- 90\nname: p1\n",
        position=(310, 60.0),
        layer=layer_pin_label,
    )
    c.add_port(
        name="p2",
        cross_section="DC",
        center=(390, 60.0),
        orientation=90,
        port_type="electrical",
    )
    c.add_label(
        text="alias: In\ndoc: p-contact 1\nwidth: 16.0\nxsection: DC\nxya:\n- 390\n- 60.0\n- 90\nname: p2\n",
        position=(390, 60.0),
        layer=layer_pin_label,
    )

    c.add_port(
        name="n1",
        cross_section="DC",
        center=(350, -60.0),
        orientation=-90,
        port_type="electrical",
    )
    c.add_label(
        text="alias: In\ndoc: n-contact 1\nwidth: 16.0\nxsection: DC\nxya:\n- 350\n- -60.0\n- -90\nname: n1\n",
        position=(350, -60.0),
        layer=layer_pin_label,
    )

    text = c << text_function(text=name)
    text.dx = c.dx
    text.dy = c.dy

    c.name = name
    if layer_pin:
        add_pins(c, layer=layer_pin)
    return c


if __name__ == "__main__":
    PDK.activate()
    c = JonnysDevice()
    c.show()
