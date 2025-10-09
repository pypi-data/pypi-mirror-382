from pandas_plink import read_plink1_bin
from typing import Optional
from pathlib import Path
import xarray as xr


def load_plink(
    bed: str, bim: Optional[str] = None, fam: Optional[str] = None
) -> xr.DataArray:
    """
    Load PLINK genotype data (.bed/.bim/.fam) using pandas-plink.

    Parameters:
        bed (str): BED file path or prefix without extension (e.g., "chr1")
        bim (str, optional): BIM file path
        fam (str, optional): FAM file path

    Returns:
        xarray.DataArray: Genotype matrix (sample x variant x allele)
    """

    bed_path = Path(bed)

    # Caso o usuário forneça apenas o prefixo
    if bed_path.suffix == "":
        base = bed_path
        bed_file = base.with_suffix(".bed")
        bim_file = base.with_suffix(".bim") if bim is None else Path(bim)
        fam_file = base.with_suffix(".fam") if fam is None else Path(fam)
    else:
        bed_file = bed_path
        bim_file = Path(bim) if bim else bed_path.with_suffix(".bim")
        fam_file = Path(fam) if fam else bed_path.with_suffix(".fam")

    if not bed_file.exists():
        raise FileNotFoundError(f"BED file not found: {bed_file}")
    if not bim_file.exists():
        raise FileNotFoundError(f"BIM file not found: {bim_file}")
    if not fam_file.exists():
        raise FileNotFoundError(f"FAM file not found: {fam_file}")

    G = read_plink1_bin(
        str(bed_file), str(bim_file), str(fam_file), verbose=False
    )  # noqa: E501
    return G


"""
from igem.load import load_plink

# With Prefix
G = load_plink("data/plink/chr11")

# or with full paths
G = load_plink(
    "data/plink/chr11.bed",
    bim="data/plink/chr11.bim",
    fam="data/plink/chr11.fam"
)
"""
