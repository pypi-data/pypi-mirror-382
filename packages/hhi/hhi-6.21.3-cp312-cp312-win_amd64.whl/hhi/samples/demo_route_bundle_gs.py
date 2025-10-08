import gdsfactory as gf

from hhi import PDK, cells, tech


@gf.cell
def sample_route_bundle_gs():
    """Sample route bundle with mzm."""
    c = gf.Component()
    m1 = c << cells.HHI_MZMDU()

    p1 = c << cells.pad_GS()
    p1.rotate(90)
    p1.center = m1.ports["g2"].center
    p1.movey(2000)
    p1.movex(900)
    _ = tech.route_bundle_gs(
        c,
        [m1["g2"]],
        [p1.ports["e1"]],
    )

    p2 = c << cells.pad_GS()
    p2.rotate(90)
    p2.center = m1.ports["g2"].center
    p2.movey(2000)
    p2.movex(-6000)
    _ = tech.route_bundle_gs(
        c,
        [m1["g1"]],
        [p2.ports["e1"]],
        sort_ports=True,
    )
    return c


@gf.cell
def sample_route_bundle_sbend_gs():
    """Sample route bundle with MZM."""
    c = gf.Component()
    m1 = c << cells.HHI_MZMDU()

    p1 = c << cells.pad_GS()
    p1.rotate(90)
    p1.center = m1.ports["g2"].center
    p1.movey(800)
    p1.movex(50)
    _ = tech.route_bundle_sbend_gs(
        c,
        [m1["g2"]],
        [p1.ports["e1"]],
    )
    return c


@gf.cell
def sample_route_bundle_sbend_gs_reverse():
    """Sample route bundle with MZM."""
    c = gf.Component()
    m1 = c << cells.HHI_MZMDU()

    p1 = c << cells.pad_GS()
    p1.rotate(90)
    p1.center = m1.ports["g2"].center
    p1.movey(800)
    p1.movex(50)
    _ = tech.route_bundle_sbend_gs(
        c,
        [p1.ports["e1"]],
        [m1["g2"]],
    )
    return c


if __name__ == "__main__":
    PDK.activate()
    # c = sample_route_bundle_gs()
    # c = sample_route_bundle_sbend_gs_reverse()
    c = sample_route_bundle_sbend_gs()
    c.show()
