import jax.numpy as jnp
import matplotlib.pyplot as plt
import sax

import hhi
from hhi import PDK

if __name__ == "__main__":
    PDK.activate()
    c = hhi.cells.mzi_E1700(delta_length=10)
    c.show()
    c.plot_schematic_networkx()
    netlist = c.get_netlist()
    models = PDK.models
    circuit, _ = sax.circuit(netlist, models=models)  # type: ignore
    wl = jnp.linspace(1.5, 1.6, 256)

    S = circuit(wl=wl)
    plt.figure(figsize=(14, 4))
    plt.title("MZI")
    plt.plot(1e3 * wl, jnp.abs(S["o1", "o2"]) ** 2)  # type: ignore
    plt.xlabel("λ [nm]")
    plt.ylabel("T")
    plt.grid(True)
    plt.show()
