import gdsfactory as gf

from hhi import PDK, cells, tech


@gf.cell
def sample_route_bundle():
    c = gf.Component()
    m1 = c << cells.HHI_MMI1x2E1700()
    m2 = c << cells.HHI_MMI1x2E1700()

    m2.xmin = m1.xmax + 1600
    m2.ymin = m1.ymax + 1600

    _ = tech.route_bundle_e1700(c, [m1.ports["o2"]], [m2.ports["o1"]])
    return c


if __name__ == "__main__":
    PDK.activate()
    c = sample_route_bundle()
    c.show()
