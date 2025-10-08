import gdsfactory as gf

from hhi import PDK, cells, tech


@gf.cell
def sample_route_bundle_dc():
    c = gf.Component()
    d1 = c << cells.HHI_DFB()
    p1 = c << cells.pad()
    p1.movey(150)
    p1.movex(-200)
    _ = tech.route_bundle_dc(
        c,
        [d1.ports["e1"]],
        [p1.ports["e1"]],
        auto_taper=False,
        start_straight_length=50,
        end_straight_length=50,
    )
    return c


@gf.cell
def sample_route_bundle_dc2():
    c = gf.Component()
    d1 = c << cells.HHI_DFB()
    p1 = c << cells.pad()
    p2 = c << cells.pad()
    p3 = c << cells.pad()

    p1.movey(250)
    p2.movey(400)
    p3.movey(550)
    _ = tech.route_bundle_dc(
        c,
        [d1.ports["g1"], d1.ports["s1"], d1.ports["g2"]],
        [p1.ports["e1"], p2.ports["e1"], p3.ports["e1"]],
        end_angles=0,
    )
    return c


@gf.cell
def sample_route_bundle_dc_corner():
    c = gf.Component()
    d1 = c << cells.HHI_DFB()
    p1 = c << cells.pad()
    p1.movey(150)
    p1.movex(-200)
    _ = tech.route_bundle_dc_corner(
        c,
        [d1.ports["e1"]],
        [p1.ports["e1"]],
        start_straight_length=50,
        end_straight_length=50,
        auto_taper=False,
    )
    return c


if __name__ == "__main__":
    PDK.activate()
    c = sample_route_bundle_dc_corner()
    c.show()
