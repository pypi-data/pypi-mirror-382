import gdsfactory as gf

from hhi import PDK, cells, tech


@gf.cell
def sample_route_bundle_gsg():
    """Sample route bundle with mzm."""
    c = gf.Component()
    d = cells.HHI_EAM()
    d.pprint_ports()
    m1 = c << d

    p1 = c << cells.pad_GSG()
    p1.rotate(90)
    p1.center = m1.ports["s1"].center
    p1.movey(2000)
    p1.movex(900)
    _ = tech.route_bundle_gsg(
        c,
        [m1["s1"]],
        [p1.ports["e1"]],
        end_straight_length=20,
    )
    return c


@gf.cell
def sample_route_bundle_sbend_gsg():
    """Sample route bundle with MZM."""
    c = gf.Component()
    m1 = c << cells.HHI_EAM()

    p1 = c << cells.pad_GSG()
    p1.rotate(90)
    p1.center = m1.ports["s1"].center
    p1.movey(800)
    p1.movex(50)
    _ = tech.route_bundle_sbend_gsg(
        c,
        [m1["s1"]],
        [p1.ports["e1"]],
    )
    return c


if __name__ == "__main__":
    PDK.activate()
    c = sample_route_bundle_gsg()
    c.show()
