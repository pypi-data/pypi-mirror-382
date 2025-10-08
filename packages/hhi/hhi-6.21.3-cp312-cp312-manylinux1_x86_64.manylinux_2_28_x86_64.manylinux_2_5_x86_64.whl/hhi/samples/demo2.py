import gdsfactory as gf

from hhi import PDK, cells


@gf.cell
def dfb_with_pads_bot():
    c = cells.HHI_DFB()
    cc = cells.add_pads_bot(
        component=c,
    )
    return cc


@gf.cell
def dfb_with_pads_top():
    c = cells.HHI_DFB()
    cc = cells.add_pads_top(
        component=c,
    )
    return cc


if __name__ == "__main__":
    PDK.activate()
    c = dfb_with_pads_top()
    c.show()
