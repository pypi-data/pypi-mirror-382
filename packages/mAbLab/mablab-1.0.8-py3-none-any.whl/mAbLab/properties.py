import numpy as np
from Bio.SeqUtils.ProtParam import ProteinAnalysis
from . import common_methods as calc

class ProteinProperties:
    """
    A class to calculate and store various properties of a protein sequence.

    Attributes:
        length (int): Length of the amino acid sequence.
        isoelectric_point (float): The isoelectric point of the protein.
        charge_ph_profile (list[tuple[float, float]]): Charge profile across pH values.
        average_molecular_weight (float): Average molecular weight of the protein.
        monoisotopic_molecular_weight (float): Monoisotopic molecular weight of the protein.
        reduced_average_molecular_weight (float): Average molecular weight of the reduced protein.
        reduced_monoisotopic_molecular_weight (float): Monoisotopic molecular weight of the reduced protein.
        reduced_molar_extinction_coefficient (float): Extinction coefficient of the reduced protein.
        molar_extinction_coefficient (float): Extinction coefficient of the protein.
        reduced_e_one_percent (float): Reduced protein's absorbance at 1% concentration.
        e_one_percent (float): Protein's absorbance at 1% concentration.
        gravy_score (float): Grand average of hydropathy (GRAVY) score.
        aromaticity (float): Aromaticity of the protein.
    """

    def __init__(self, aa_sequence_list: list[str] = None) -> None:
        """
        Initialize the ProteinProperties object with an amino acid sequence.

        Args:
            aa_sequence_list (list[str]): List of amino acid sequences.
        """
        aa_sequence = ''.join(aa_sequence_list)
        self._chain_properties = ProteinAnalysis(aa_sequence)
        self.length = len(aa_sequence)
        self.isoelectric_point = self._chain_properties.isoelectric_point()
        self.charge_ph_profile = self._calculate_charge_profile()
        self.average_molecular_weight = calc.calculate_average_mass(aa_sequence_list, reduced=False)
        self.monoisotopic_molecular_weight = calc.calculate_monoisotopic_mass(aa_sequence_list, reduced=False)
        self.reduced_average_molecular_weight = calc.calculate_average_mass(aa_sequence_list, reduced=True)
        self.reduced_monoisotopic_molecular_weight = calc.calculate_monoisotopic_mass(aa_sequence_list, reduced=True)
        self.reduced_molar_extinction_coefficient, self.molar_extinction_coefficient = self._chain_properties.molar_extinction_coefficient()
        self.reduced_e_one_percent = calc.calculate_e_one_percent(self.reduced_molar_extinction_coefficient, self.reduced_average_molecular_weight)
        self.e_one_percent = calc.calculate_e_one_percent(self.molar_extinction_coefficient, self.average_molecular_weight)
        self.gravy_score = self._chain_properties.gravy()
        self.aromaticity = self._chain_properties.aromaticity()

    def charge_at_ph(self, ph: float) -> float:
        """
        Calculate the charge of the protein at a given pH.

        Args:
            ph (float): The pH value.

        Returns:
            float: The charge of the protein at the given pH.

        Raises:
            ValueError: If the pH is not between 1 and 12.
        """
        if ph < 1 or ph > 12:
            raise ValueError("pH must be between 1 and 12")
        return self._chain_properties.charge_at_pH(ph)

    def _calculate_charge_profile(self) -> list[tuple[float, float]]:
        """
        Calculate the charge profile of the protein across pH values.

        Returns:
            list[tuple[float, float]]: A list of tuples containing pH and corresponding charge.
        """
        charge_ph_profile = []
        for ph in np.arange(1, 12.25, 0.25):
            charge_ph_profile.append((float(ph), float(self._chain_properties.charge_at_pH(ph))))
        return charge_ph_profile

    def to_dict(self):
        """
        Convert the protein properties to a dictionary.

        Returns:
            dict: A dictionary containing all the protein properties.
        """
        return {
            "length": self.length,
            "isoelectric_point": self.isoelectric_point,
            "charge_ph_profile": self.charge_ph_profile,
            "average_molecular_weight": self.average_molecular_weight,
            "monoisotopic_molecular_weight": self.monoisotopic_molecular_weight,
            "reduced_average_molecular_weight": self.reduced_average_molecular_weight,
            "reduced_monoisotopic_molecular_weight": self.reduced_monoisotopic_molecular_weight,
            "reduced_molar_extinction_coefficient": self.reduced_molar_extinction_coefficient,
            "molar_extinction_coefficient": self.molar_extinction_coefficient,
            "reduced_e_one_percent": self.reduced_e_one_percent,
            "e_one_percent": self.e_one_percent,
            "gravy_score": self.gravy_score,
            "aromaticity": self.aromaticity,
        }
