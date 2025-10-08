import gdsfactory as gf

from hhi import PDK, cells, tech


@gf.cell
def sample_route_bundle_sbend_dc():
    c = gf.Component()
    d1 = c << cells.HHI_DFB()

    p1 = c << cells.pad()
    p1.movey(-900)
    _ = tech.route_bundle_sbend_dc(
        c,
        [d1.ports["e2"]],
        [p1.ports["e2"]],
    )
    return c


if __name__ == "__main__":
    PDK.activate()
    c = sample_route_bundle_sbend_dc()
    c.show()
