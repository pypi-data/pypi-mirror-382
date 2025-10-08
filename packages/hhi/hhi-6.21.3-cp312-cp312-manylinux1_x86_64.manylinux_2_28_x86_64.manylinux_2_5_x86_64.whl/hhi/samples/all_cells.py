"""This is the file that samples all HHI cells with variations for HHI to verify the PDK."""

import inspect
import re

import gdsfactory as gf

from hhi import PDK, cells
from hhi.cells.fixed import (
    HHI_BPD,
    HHI_DBR,
    HHI_DFB,
    HHI_EAM,
    HHI_GRAT,
    HHI_MIR1E1700,
    HHI_MIR2E1700,
    HHI_MZMDD,
    HHI_MZMDU,
    HHI_PDDC,
    HHI_PMTOE200,
    HHI_PMTOE600,
    HHI_PMTOE1700,
    HHI_R50GSG,
    HHI_SGDBRTO,
    HHI_SOA,
    HHI_SSCLATE200,
    HHI_SSCLATE1700,
    HHI_WGTE200E600,
    HHI_WGTE200E1700,
    HHI_WGTE600E1700,
    HHI_BJsingle,
    HHI_BJtwin,
    HHI_DBRsection,
    HHI_DFBsection,
    HHI_DirCoupE600,
    HHI_DirCoupE1700,
    HHI_EAMsection,
    HHI_EOBiasSectionSingle,
    HHI_EOBiasSectionTwin,
    HHI_EOElectricalGND,
    HHI_EOPMTermination,
    HHI_EOPMTWSingleDD,
    HHI_EOPMTWSingleDU,
    HHI_EOPMTWTwinDD,
    HHI_EOPMTWTwinDU,
    HHI_FacetWGE200,
    HHI_FacetWGE600,
    HHI_FacetWGE1700,
    HHI_FacetWGE1700twin,
    HHI_GRATsection,
    HHI_GSGtoGS,
    HHI_ISOsectionSingle,
    HHI_ISOsectionTwin,
    HHI_METMETx,
    HHI_MMI1x2ACT,
    HHI_MMI1x2E600,
    HHI_MMI1x2E1700,
    HHI_MMI2x2ACT,
    HHI_MMI2x2E600,
    HHI_MMI2x2E1700,
    HHI_MZIswitch,
    HHI_PDRFsingle,
    HHI_PDRFtwin,
    HHI_PolConverter45,
    HHI_PolConverter90,
    HHI_PolSplitter,
    HHI_SOAsection,
    HHI_TOBiasSection,
    HHI_WGMETxACTGSGsingle,
    HHI_WGMETxACTGSGtwin,
    HHI_WGMETxACTGSsingle,
    HHI_WGMETxACTGStwin,
    HHI_WGMETxACTsingle,
    HHI_WGMETxACTtwin,
    HHI_WGMETxE200,
    HHI_WGMETxE200GS,
    HHI_WGMETxE200GSG,
    HHI_WGMETxE600,
    HHI_WGMETxE600GS,
    HHI_WGMETxE600GSG,
    HHI_WGMETxE1700GSGsingle,
    HHI_WGMETxE1700GSGtwin,
    HHI_WGMETxE1700GSsingle,
    HHI_WGMETxE1700GStwin,
    HHI_WGMETxE1700single,
    HHI_WGMETxE1700twin,
)
from hhi.config import PATH
from hhi.samples.demo_route_bundle import sample_route_bundle
from hhi.samples.demo_route_bundle_dc import (
    sample_route_bundle_dc,
    sample_route_bundle_dc2,
    sample_route_bundle_dc_corner,
)
from hhi.samples.demo_route_bundle_dc_corner import sample_route_bundle_dc_corner1
from hhi.samples.demo_route_bundle_gs import sample_route_bundle_gs
from hhi.samples.demo_route_bundle_gsg import sample_route_bundle_gsg

size1 = (2e3, 8e3)
size2 = (4e3, 8e3)
size3 = (12e3, 8e3)


def extract_parameter_ranges(docstring):
    """Extract parameter ranges from docstring."""
    param_ranges = {}
    if not docstring:
        return param_ranges

    # Find all parameter descriptions
    param_pattern = r"(\w+):.*?\(min: ([\d.]+), max: ([\d.]+)"
    matches = re.findall(param_pattern, docstring)

    for param, min_val, max_val in matches:
        param_ranges[param] = {"min": float(min_val), "max": float(max_val)}

    return param_ranges


def run_with_parameter_variants(functions):
    results = []
    for fn in functions:
        sig = inspect.signature(fn)
        docstring = fn.__doc__ or ""
        param_ranges = extract_parameter_ranges(docstring)

        # Collect default parameters
        default_kwargs = {
            k: v.default
            for k, v in sig.parameters.items()
            if v.default is not inspect.Parameter.empty
        }

        # Create variants for each parameter
        variants = [default_kwargs]  # Start with default values

        for param, ranges in param_ranges.items():
            if param in default_kwargs and ranges["min"] != ranges["max"]:
                # Create min and max variants
                min_variant = default_kwargs.copy()
                min_variant[param] = ranges["min"]

                max_variant = default_kwargs.copy()
                max_variant[param] = ranges["max"]

                variants.extend([min_variant, max_variant])

        # Call function with each variant
        for variant in variants:
            try:
                result = fn(**variant)
                results.append(result)
            except Exception as e:
                print(f"Error creating variant for {fn.__name__} with {variant}: {e}")
                continue

    return results


@gf.cell
def sample_all_cells_with_variations() -> gf.Component:
    """Returns a sample die."""
    c = gf.Component()

    components = [
        HHI_BJsingle,
        HHI_BJtwin,
        HHI_BPD,
        HHI_DBR,
        HHI_DBRsection,
        HHI_DFB,
        HHI_DFBsection,
        HHI_DirCoupE1700,
        HHI_DirCoupE600,
        HHI_EAM,
        HHI_EAMsection,
        HHI_EOBiasSectionSingle,
        HHI_EOBiasSectionTwin,
        HHI_EOElectricalGND,
        HHI_EOPMTWSingleDD,
        HHI_EOPMTWSingleDU,
        HHI_EOPMTWTwinDD,
        HHI_EOPMTWTwinDU,
        HHI_EOPMTermination,
        HHI_FacetWGE1700,
        HHI_FacetWGE1700twin,
        HHI_FacetWGE200,
        HHI_FacetWGE600,
        HHI_GRAT,
        HHI_GRATsection,
        HHI_GSGtoGS,
        HHI_ISOsectionSingle,
        HHI_ISOsectionTwin,
        HHI_METMETx,
        HHI_MIR1E1700,
        HHI_MIR2E1700,
        HHI_MMI1x2ACT,
        HHI_MMI1x2E1700,
        HHI_MMI1x2E600,
        HHI_MMI2x2ACT,
        HHI_MMI2x2E1700,
        HHI_MMI2x2E600,
        HHI_MZIswitch,
        HHI_MZMDD,
        HHI_MZMDU,
        HHI_PDDC,
        HHI_PDRFsingle,
        HHI_PDRFtwin,
        HHI_PMTOE1700,
        HHI_PMTOE200,
        HHI_PMTOE600,
        HHI_PolConverter45,
        HHI_PolConverter90,
        HHI_PolSplitter,
        HHI_R50GSG,
        HHI_SGDBRTO,
        HHI_SOA,
        HHI_SOAsection,
        HHI_SSCLATE1700,
        HHI_SSCLATE200,
        HHI_TOBiasSection,
        HHI_WGMETxACTGSGsingle,
        HHI_WGMETxACTGSGtwin,
        HHI_WGMETxACTGSsingle,
        HHI_WGMETxACTGStwin,
        HHI_WGMETxACTsingle,
        HHI_WGMETxACTtwin,
        HHI_WGMETxE1700GSGsingle,
        HHI_WGMETxE1700GSGtwin,
        HHI_WGMETxE1700GSsingle,
        HHI_WGMETxE1700GStwin,
        HHI_WGMETxE1700single,
        HHI_WGMETxE1700twin,
        HHI_WGMETxE200,
        HHI_WGMETxE200GS,
        HHI_WGMETxE200GSG,
        HHI_WGMETxE600,
        HHI_WGMETxE600GS,
        HHI_WGMETxE600GSG,
        HHI_WGTE200E1700,
        HHI_WGTE200E600,
        HHI_WGTE600E1700,
    ]

    print(f"Number of components: {len(components)}")

    components = run_with_parameter_variants(components)

    print(f"Number of components: {len(components)}")

    # Add waveguides
    length = 100  # um
    waveguides = gf.pack(
        [
            cells.straight(length=length, cross_section="E1700"),
            cells.straight(length=length, cross_section="E600"),
            cells.straight(length=length, cross_section="E200"),
            cells.straight(length=length, cross_section="GSG"),
            cells.straight(length=length, cross_section="GS"),
            cells.bend_circular(cross_section="E1700"),
            cells.bend_circular(cross_section="E600"),
            cells.bend_circular(cross_section="E200"),
            cells.bend_circular(cross_section="GSG"),
            cells.bend_circular(cross_section="GS"),
        ],
        spacing=20,
    )[0]

    waveguides.name = "waveguides"

    bbox_cells = gf.pack(components, spacing=20)[0]
    bbox_cells.name = "bbox_cells"

    version = cells.text_rectangular(PDK.version, layer=(55, 0)).copy()
    version.name = "version"

    components = [
        cells.die,
        cells.cleave_mark,
        cells.pad,
        cells.die_rf,
        sample_route_bundle,
        sample_route_bundle_dc,
        sample_route_bundle_dc2,
        sample_route_bundle_dc_corner,
        sample_route_bundle_dc_corner1,
        sample_route_bundle_gs,
        sample_route_bundle_gsg,
        waveguides,
        bbox_cells,
        version,
    ]

    c = gf.pack(components, spacing=20)[0]
    c.add_label("HHI PDK " + PDK.version, position=(c.xmin, c.ymin), layer=(55, 0))
    return c


if __name__ == "__main__":
    PDK.activate()

    exclude_layers = [(1004, 0)]
    # exclude_layers = None

    c = sample_all_cells_with_variations()
    # c.remove_layers(layers=[(1004, 0)], unlock=True)

    gdspath = c.write_gds(
        gdspath=PATH.home / "Downloads" / "hhi_all_cells.gds",
        with_metadata=False,
        exclude_layers=exclude_layers,
    )
    gf.show(gdspath)
