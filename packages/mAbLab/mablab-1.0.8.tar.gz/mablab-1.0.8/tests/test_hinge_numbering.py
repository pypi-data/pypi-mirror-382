import sys
import os
import unittest

# Add the root directory to the Python path so mAbLab can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mAbLab import Mab

HC1_SEQ = (
    "EVQLVQSGAEVKKPGSSVKVSCKASGYTFSSYWMHWVRQAPGQGLEWIGLIHPESGSTNYNEMFKNRATLTVDRSTSTAYMELSSLRSEDTAVYYCAGGGRLYFDYWGQGTTVTVSSASTKGPSVFPLAPSSKSTSGGTAALGCLVKDYFPEPVTVSWNSGALTSGVHTFPAVLQSSGLYSLSSVVTVPSSSLGTQTYICNVNHKPSNTKVDKKVEPKSCDKTHTCPPCPAPEAAGGPSVFLFPPKPKDTLMISRTPEVTCVVVDVSHEDPEVKFNWYVDGVEVHNAKTKPREEQYNSTYRVVSVLTVLHQDWLNGKEYKCKVSNKALPAPIEKTISKAKGQPREPQVYTLPPSREEMTKNQVSLTCLVKGFYPSDIAVEWESNGQPENNYKTTPPVLDSDGSFFLYSKLTVDKSRWQQGNVFSCSVMHEALHNHYTQKSLSLSPGK"
)
HC2_SEQ = HC1_SEQ
LC1_SEQ = (
    "DIVMTQSPLSLPVTPGEPASISCRSSQSLVHSNQDTYLRWYLQKPGQSPQLLIYKVSNRFSGVPDRFSGSGSGTDFTLKISRVEAEDVGVYYCSQSTHVPYTFGGGTKVEIKRTVAAPSVFIFPPSDEQLKSGTASVVCLLNNFYPREAKVQWKVDNALQSGNSQESVTEQDSKDSTYSLSSTLTLSKADYEKHKVYACEVTHQGLSSPVTKSFNRGEC"
)
LC2_SEQ = LC1_SEQ

class TestHingeNumbering(unittest.TestCase):
    def setUp(self):
        self.mab = Mab(
            hc1_aa_sequence=HC1_SEQ,
            hc2_aa_sequence=HC2_SEQ,
            lc1_aa_sequence=LC1_SEQ,
            lc2_aa_sequence=LC2_SEQ,
        )

    def test_hc1_hinge_numbering(self):
        # Try all common numbering schemes
        hinge = self.mab.hc1.hinge
        print("HC1 hinge numbering (IMGT):", hinge.numbering.imgt)
        print("HC1 hinge numbering (Kabat):", hinge.numbering.kabat)
        print("HC1 hinge numbering (EU):", hinge.numbering.eu)
        print("HC1 hinge numbering (Martin):", hinge.numbering.martin)
        print("HC1 hinge numbering (AHO):", hinge.numbering.aho)
        # Assert at least one is not None and is a list
        self.assertTrue(
            any(
                isinstance(getattr(hinge.numbering, scheme), list) and getattr(hinge.numbering, scheme)
                for scheme in ["imgt", "kabat", "eu", "martin", "aho"]
            )
        )

    def test_hc2_hinge_numbering(self):
        hinge = self.mab.hc2.hinge
        print("HC2 hinge numbering (IMGT):", hinge.numbering.imgt)
        print("HC2 hinge numbering (Kabat):", hinge.numbering.kabat)
        print("HC2 hinge numbering (EU):", hinge.numbering.eu)
        print("HC2 hinge numbering (Martin):", hinge.numbering.martin)
        print("HC2 hinge numbering (AHO):", hinge.numbering.aho)
        self.assertTrue(
            any(
                isinstance(getattr(hinge.numbering, scheme), list) and getattr(hinge.numbering, scheme)
                for scheme in ["imgt", "kabat", "eu", "martin", "aho"]
            )
        )

    def test_hc1_hinge_numbering_dict_equivalence(self):
        hinge = self.mab.hc1.hinge
        hinge_dict = self.mab.to_dict()["hc1"]["hinge"]["numbering"]
        for scheme in ["imgt", "kabat", "eu", "martin", "aho"]:
            direct = getattr(hinge.numbering, scheme)
            dict_val = hinge_dict.get(scheme)
            self.assertEqual(direct, dict_val, f"Mismatch for scheme {scheme}")

    def test_hc2_hinge_numbering_dict_equivalence(self):
        hinge = self.mab.hc2.hinge
        hinge_dict = self.mab.to_dict()["hc2"]["hinge"]["numbering"]
        for scheme in ["imgt", "kabat", "eu", "martin", "aho"]:
            direct = getattr(hinge.numbering, scheme)
            dict_val = hinge_dict.get(scheme)
            self.assertEqual(direct, dict_val, f"Mismatch for scheme {scheme}")

if __name__ == "__main__":
    unittest.main()
