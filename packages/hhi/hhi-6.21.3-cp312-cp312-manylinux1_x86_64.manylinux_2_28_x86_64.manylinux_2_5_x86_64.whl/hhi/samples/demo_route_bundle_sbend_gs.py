import gdsfactory as gf

from hhi import PDK, cells, tech


@gf.cell
def sample_route_bundle_sbend_GS():
    """Sample route bundle with a gs corner."""
    c = gf.Component()
    m1 = c << cells.HHI_MZMDU()

    p1 = c << cells.pad_GS()
    p1.rotate(90)
    p1.center = m1.ports["g2"].center
    p1.movey(990)
    p1.movex(10)
    _ = tech.route_bundle_sbend_gs(
        c,
        [m1.ports["g2"]],
        [p1.ports["e1"]],
        use_port_width=True,
        allow_type_mismatch=True,
    )
    return c


if __name__ == "__main__":
    PDK.activate()
    c = sample_route_bundle_sbend_GS()
    c.show()
