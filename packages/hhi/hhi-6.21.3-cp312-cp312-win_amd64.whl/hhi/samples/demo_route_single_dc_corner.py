import gdsfactory as gf

from hhi import PDK, cells, tech


@gf.cell
def sample_route_single_dc_corner():
    """"""
    c = gf.Component()
    d1 = c << cells.HHI_DFB()
    p1 = c << cells.pad()
    p1.movey(150)
    p1.movex(2000)
    _ = tech.route_single_dc(
        c,
        p1.ports["e1"],
        d1.ports["e1"],
        auto_taper=False,
        allow_width_mismatch=True,
    )
    return c


if __name__ == "__main__":
    PDK.activate()
    c = sample_route_single_dc_corner()
    c.show()
