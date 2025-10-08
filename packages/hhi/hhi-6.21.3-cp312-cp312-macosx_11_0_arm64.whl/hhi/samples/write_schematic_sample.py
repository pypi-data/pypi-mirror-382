"""Write all cells into schematic."""

import pathlib

import gdsfactory.schematic as gt

from hhi import PDK

if __name__ == "__main__":
    PDK.activate()
    s = gt.Schematic()

    grid_size = int(len(PDK.cells) ** 0.5) + 1  # Determine grid dimensions
    spacing = 1000  # Adjust spacing as needed

    for i, cell_name in enumerate(PDK.cells.keys()):
        print(f"Adding {cell_name} to schematic")
        x = (i % grid_size) * spacing
        y = (i // grid_size) * spacing
        s.add_instance(cell_name, gt.Instance(component=cell_name))
        s.add_placement(cell_name, gt.Placement(x=x, y=y))

    yaml_component = s.write_netlist(s.netlist.model_dump())
    print(yaml_component)
    filepath = pathlib.Path(__file__).parent / "schematic_all.pic.yml"
    filepath.write_text(yaml_component)
