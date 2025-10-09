import sys
import os
import unittest

# Add the root directory to the Python path so mAbLab can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mAbLab import Mab

LC_SEQ = 'DIQMTQSPSSLSASVGDRVTITCRASQGIRNYLAWYQQKPGKAPKLLIYAASTLQSGVPSRFSGSGSGTDFTLTISSLQPEDVATYYCQRYNRAPYTFGQGTKVEIKRTVAAPSVFIFPPSDEQLKSGTASVVCLLNNFYPREAKVQWKVDNALQSGNSQESVTEQDSKDSTYSLSSTLTLSKADYEKHKVYACEVTHQGLSSPVTKSFNRGEC'
HC_SEQ = 'EVQLVESGGGLVQPGRSLRLSCAASGFTFDDYAMHWVRQAPGKGLEWVSAITWNSGHIDYADSVEGRFTISRDNAKNSLYLQMNSLRAEDTAVYYCAKVSYLSTASSLDYWGQGTLVTVSSASTKGPSVFPLAPSSKSTSGGTAALGCLVKDYFPEPVTVSWNSGALTSGVHTFPAVLQSSGLYSLSSVVTVPSSPAPTQTYICNVNHKPSNTKVDKKVEPKSCDKTHTCPPCPAPELLGGPSVFLFPPKPKDTLMISRTPEVTCVVVDVSHEDPEVKFNWYVDGVEVHNAKTKPREEQYNSTYRVVSVLTVLHQDWLNGKEYKCKVSNKALPAPIEKTISKAKGQPREPQVYTLPPSRDELTKNQVSLTCLVKGFYPSDIAVEWESNGQPENNYKTTPPVLDSDGSFFLYSKLTVDKSRWQQGNVFSCSVMHEALHNHYTQKSLSLSPGK'
HC2_SEQ = 'DKTHTCPPCPAPEAAGGPSVFLFPPKPKDTLMISRTPEVTCVVVDVSHEDPEVKFNWYVDGVEVHNAKTKPREEQYNSTYRVVSVLTVLHQDWLNGKEYKCKVSNKALPAPIEKTISKAKGQPREPQVYTLPPSREEMTKNQVSLWCLVKGFYPSDIAVEWESNGQPENNYKTTPPVLDSDGSFFLYSKLTVDKSRWQQGNVFSCSVMHEALHNHYTQKSLSLSPGK'

class TestToDictEquivalence(unittest.TestCase):
    def setUp(self):
        self.mab = Mab(hc1_aa_sequence=HC_SEQ, hc2_aa_sequence=HC_SEQ, lc1_aa_sequence=LC_SEQ, lc2_aa_sequence=LC_SEQ)

    def test_ch2_annotation_kabat_equivalence(self):
        # Direct attribute access
        direct = self.mab.hc1.ch2.annotation.kabat
        # Dict access
        dict_access = self.mab.to_dict()["hc1"]["ch2"]["annotation"]["kabat"]
        self.assertEqual(direct, dict_access)

    def test_ch2_annotation_imgt_equivalence(self):
        direct = self.mab.hc1.ch2.annotation.imgt
        print(direct)
        print('/n')
        dict_access = self.mab.to_dict()["hc1"]["ch2"]["annotation"]["imgt"]
        print(dict_access)
        self.assertEqual(direct, dict_access)

    def test_lc1_vl_numbering_eu_equivalence(self):
        direct = self.mab.lc1.vl.numbering.eu
        dict_access = self.mab.to_dict()["lc1"]["vl"]["numbering"]["eu"]
        self.assertEqual(direct, dict_access)

    def test_lc2_cl_annotation_martin_equivalence(self):
        direct = self.mab.lc2.cl.annotation.martin
        dict_access = self.mab.to_dict()["lc2"]["cl"]["annotation"]["martin"]
        self.assertEqual(direct, dict_access)
    
    def test_full_length_annotated_sequence_printing(self):
        """Test to print full length annotated sequences with Kabat Variable and EU constant numbering"""
        print("\n" + "="*80)
        print("FULL LENGTH ANNOTATED SEQUENCES")
        print("="*80)
        
        # Heavy Chain - Kabat Variable + EU Constant
        print("\nHEAVY CHAIN (HC1) - Kabat Variable + EU Constant:")
        print("-" * 50)
        
        # Get VH Kabat sequence/numbering/annotation
        try:
            vh_sequence = self.mab.hc1.vh.sequence
            vh_kabat_numbering = self.mab.hc1.vh.numbering.kabat
            vh_kabat_annotation = self.mab.hc1.vh.annotation.kabat
            print(f"VH Sequence: {','.join(vh_sequence)}")
            print(f"VH Kabat Numbering: {vh_kabat_numbering}")
            print(f"VH Kabat Annotation: {vh_kabat_annotation}")
        except Exception as e:
            print(f"VH Kabat error: {e}")
        
        # Get CH1 EU sequence/numbering/annotation
        try:
            ch1_sequence = self.mab.hc1.ch1.sequence
            ch1_eu_numbering = self.mab.hc1.ch1.numbering.eu
            ch1_eu_annotation = self.mab.hc1.ch1.annotation.eu
            print(f"CH1 Sequence: {','.join(ch1_sequence)}")
            print(f"CH1 EU Numbering: {ch1_eu_numbering}")
            print(f"CH1 EU Annotation: {ch1_eu_annotation}")
        except Exception as e:
            print(f"CH1 EU error: {e}")
            
        # Get Hinge EU sequence/numbering/annotation
        try:
            hinge_sequence = self.mab.hc1.hinge.sequence
            hinge_eu_numbering = self.mab.hc1.hinge.numbering.eu
            hinge_eu_annotation = self.mab.hc1.hinge.annotation.eu
            print(f"Hinge Sequence: {','.join(hinge_sequence)}")
            print(f"Hinge EU Numbering: {hinge_eu_numbering}")
            print(f"Hinge EU Annotation: {hinge_eu_annotation}")
        except Exception as e:
            print(f"Hinge EU error: {e}")
            
        # Get CH2 EU sequence/numbering/annotation
        try:
            ch2_sequence = self.mab.hc1.ch2.sequence
            ch2_eu_numbering = self.mab.hc1.ch2.numbering.eu
            ch2_eu_annotation = self.mab.hc1.ch2.annotation.eu
            print(f"CH2 Sequence: {','.join(ch2_sequence)}")
            print(f"CH2 EU Numbering: {ch2_eu_numbering}")
            print(f"CH2 EU Annotation: {ch2_eu_annotation}")
        except Exception as e:
            print(f"CH2 EU error: {e}")
            
        # Get CH3 EU sequence/numbering/annotation
        try:
            ch3_sequence = self.mab.hc1.ch3.sequence
            ch3_eu_numbering = self.mab.hc1.ch3.numbering.eu
            ch3_eu_annotation = self.mab.hc1.ch3.annotation.eu
            print(f"CH3 Sequence: {','.join(ch3_sequence)}")
            print(f"CH3 EU Numbering: {ch3_eu_numbering}")
            print(f"CH3 EU Annotation: {ch3_eu_annotation}")
        except Exception as e:
            print(f"CH3 EU error: {e}")
        
        # Print full Heavy Chain sequence with combined numbering and annotation
        try:
            hc_full_sequence = self.mab.hc1.hc.sequence
            hc_kabat_vl_numbering = self.mab.hc1.vh.numbering.kabat + self.mab.hc1.ch1.numbering.eu + self.mab.hc1.hinge.numbering.eu + self.mab.hc1.ch2.numbering.eu + self.mab.hc1.ch3.numbering.eu
            hc_kabat_vl_annotation = self.mab.hc1.vh.annotation.kabat + self.mab.hc1.ch1.annotation.eu + self.mab.hc1.hinge.annotation.eu + self.mab.hc1.ch2.annotation.eu + self.mab.hc1.ch3.annotation.eu
            print(f"\nFULL HC SEQUENCE: {','.join(hc_full_sequence)}")
            print(f"FULL HC Kabat(VH)+EU(Constant) Numbering: {hc_kabat_vl_numbering}")
            print(f"FULL HC Kabat(VH)+EU(Constant) Annotation: {hc_kabat_vl_annotation}")
        except Exception as e:
            print(f"Full HC error: {e}")
        
        # Light Chain - Kabat Variable + EU Constant
        print("\nLIGHT CHAIN (LC1) - Kabat Variable + EU Constant:")
        print("-" * 50)
        
        # Get VL Kabat sequence/numbering/annotation
        try:
            vl_sequence = self.mab.lc1.vl.sequence
            vl_kabat_numbering = self.mab.lc1.vl.numbering.kabat
            vl_kabat_annotation = self.mab.lc1.vl.annotation.kabat
            print(f"VL Sequence: {','.join(vl_sequence)}")
            print(f"VL Kabat Numbering: {vl_kabat_numbering}")
            print(f"VL Kabat Annotation: {vl_kabat_annotation}")
        except Exception as e:
            print(f"VL Kabat error: {e}")
        
        # Get CL EU sequence/numbering/annotation
        try:
            cl_sequence = self.mab.lc1.cl.sequence
            cl_eu_numbering = self.mab.lc1.cl.numbering.eu
            cl_eu_annotation = self.mab.lc1.cl.annotation.eu
            print(f"CL Sequence: {','.join(cl_sequence)}")
            print(f"CL EU Numbering: {cl_eu_numbering}")
            print(f"CL EU Annotation: {cl_eu_annotation}")
        except Exception as e:
            print(f"CL EU error: {e}")
            
        # Print full Light Chain sequence with combined numbering and annotation
        try:
            lc_full_sequence = self.mab.lc1.lc.sequence
            lc_kabat_vl_numbering = self.mab.lc1.vl.numbering.kabat + self.mab.lc1.cl.numbering.eu
            lc_kabat_vl_annotation = self.mab.lc1.vl.annotation.kabat + self.mab.lc1.cl.annotation.eu
            print(f"\nFULL LC SEQUENCE: {','.join(lc_full_sequence)}")
            print(f"FULL LC Kabat(VL)+EU(Constant) Numbering: {lc_kabat_vl_numbering}")
            print(f"FULL LC Kabat(VL)+EU(Constant) Annotation: {lc_kabat_vl_annotation}")
        except Exception as e:
            print(f"Full LC error: {e}")
            
        print("\n" + "="*80)
        
        # This test always passes - it's just for printing
        self.assertTrue(True)

if __name__ == "__main__":
    #unittest.main() 
    # Create a test instance and run the full length annotation printing test
    test_instance = TestToDictEquivalence()
    test_instance.setUp()
    test_instance.test_full_length_annotated_sequence_printing()
