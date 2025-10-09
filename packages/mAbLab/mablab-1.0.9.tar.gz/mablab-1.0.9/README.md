# mAbLab

`mAbLab` is a Python library for analyzing monoclonal antibody (mAb) characteristics with domain granularity.

## Features
- Analyze VL, VC, VH, CH1, CH2, CH3, Fab, LC, HC, Fc, andHinge domains of antibodies.
- Calculate protein properties such as molecular weight, isoelectric point, and extinction coefficients.
- Annotate CDR regions and infer germline genes.
- number sequences with Kabat, Martin, IMGT numbering schemes

## Installation
Install the library using pip:
```bash
pip install mAbLab
```

## Usage
```python
import mAbLab

# Example sequences
hc_sequence = "EVQLVESGGGLVQPGRSLRLSCAASGFTFDDYAMHW..."
lc_sequence = "DIQMTQSPSSLSASVGDRVTITCRASQGIRNYLAW..."

# Create a Mab object
mab = mAbLab.Mab(hc1_aa_sequence=hc_sequence, lc1_aa_sequence=lc_sequence)

# Access Fab properties
print(mab.fab1.properties.charge_at_ph(6))
```

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.