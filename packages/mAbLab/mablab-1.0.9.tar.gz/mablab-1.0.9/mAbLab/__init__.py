# Define the __all__ variable
__all__ = ["HeavyChain", "LightChain", "Mab", "ProteinProperties"]

# Import the submodules
from .heavy_chain import HeavyChain
from .light_chain import LightChain
from .mab import Mab
from .properties import ProteinProperties