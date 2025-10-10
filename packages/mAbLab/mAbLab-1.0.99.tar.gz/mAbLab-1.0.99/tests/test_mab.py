import sys
import os
import unittest
# Add the root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mAbLab import Mab, HeavyChain, LightChain

LC_SEQ = 'DIQMTQSPSSLSASVGDRVTITCRASQGIRNYLAWYQQKPGKAPKLLIYAASTLQSGVPSRFSGSGSGTDFTLTISSLQPEDVATYYCQRYNRAPYTFGQGTKVEIKRTVAAPSVFIFPPSDEQLKSGTASVVCLLNNFYPREAKVQWKVDNALQSGNSQESVTEQDSKDSTYSLSSTLTLSKADYEKHKVYACEVTHQGLSSPVTKSFNRGEC'
HC_SEQ = 'EVQLVESGGGLVQPGRSLRLSCAASGFTFDDYAMHWVRQAPGKGLEWVSAITWNSGHIDYADSVEGRFTISRDNAKNSLYLQMNSLRAEDTAVYYCAKVSYLSTASSLDYWGQGTLVTVSSASTKGPSVFPLAPSSKSTSGGTAALGCLVKDYFPEPVTVSWNSGALTSGVHTFPAVLQSSGLYSLSSVVTVPSSSLGTQTYICNVNHKPSNTKVDKKVEPKSCDKTHTCPPCPAPELLGGPSVFLFPPKPKDTLMISRTPEVTCVVVDVSHEDPEVKFNWYVDGVEVHNAKTKPREEQYNSTYRVVSVLTVLHQDWLNGKEYKCKVSNKALPAPIEKTISKAKGQPREPQVYTLPPSRDELTKNQVSLTCLVKGFYPSDIAVEWESNGQPENNYKTTPPVLDSDGSFFLYSKLTVDKSRWQQGNVFSCSVMHEALHNHYTQKSLSLSPGK'

class TestMab(unittest.TestCase):
    def setUp(self):
        self.mab = Mab(hc1_aa_sequence=HC_SEQ, hc2_aa_sequence=HC_SEQ, lc1_aa_sequence=LC_SEQ, lc2_aa_sequence=LC_SEQ)

    def test_fab_properties(self):
        self.assertIsNotNone(self.mab.fab1)
        self.assertIsNotNone(self.mab.fab2)
        self.assertIsNotNone(self.mab.fab1.properties)
        self.assertIsNotNone(self.mab.fab2.properties)
        self.assertAlmostEqual(self.mab.fab1.properties.charge_at_ph(6), 8.512393887952456, places=2)
        self.assertAlmostEqual(self.mab.fab2.properties.charge_at_ph(6), 8.512393887952456, places=2)

    def test_heavy_chain_cdr1(self):
        self.assertIsNotNone(self.mab.hc1)
        self.assertIsNotNone(self.mab.hc1.cdr1)
        self.assertIsNotNone(self.mab.hc1.cdr1.properties)
        self.assertEqual(self.mab.hc1.cdr1.properties.martin.length, 7)
        self.assertEqual(self.mab.hc1.cdr1.sequence.martin, ['G', 'F', 'T', 'F', 'D', 'D', 'Y'])
        self.assertEqual(self.mab.hc1.cdr1.numbering.martin, ['26', '27', '28', '29', '30', '31', '32'])
        print(self.mab.hc1.cdr1.numbering.martin)
        print(self.mab.hc1.ch2.annotation.imgt)
        self.assertAlmostEqual(self.mab.hc1.cdr1.properties.martin.charge_at_ph(6), -2.0050264531514523, places=2)

    def test_light_chain_cdr1(self):
        self.assertIsNotNone(self.mab.lc1)
        self.assertIsNotNone(self.mab.lc1.cdr1)
        self.assertIsNotNone(self.mab.lc1.cdr1.properties)
        self.assertEqual(self.mab.lc1.cdr1.properties.martin.length, 7)
        self.assertEqual(self.mab.lc1.cdr1.sequence.martin, ['S', 'Q', 'G', 'I', 'R', 'N', 'Y'])
        self.assertEqual(self.mab.lc1.cdr1.numbering.martin, ['26', '27', '28', '29', '30', '31', '32'])
        self.assertAlmostEqual(self.mab.lc1.cdr1.properties.martin.charge_at_ph(6), 0.8982973887927282, places=2)

    def test_heavy_chain_germlines(self):
        self.assertIsNotNone(self.mab.hc1)
        self.assertIsNotNone(self.mab.hc1.germlines)
        self.assertTrue(self.mab.hc1.germlines.chain_is_passable_as_human)
        self.assertAlmostEqual(self.mab.hc1.germlines.humanness, -66.35688285061383, places=2)
        self.assertEqual(self.mab.hc1.germlines.nearest_j_genes, ['IGHJ4*01', 'IGHJ4*02', 'IGHJ4*03'])
        self.assertAlmostEqual(self.mab.hc1.germlines.j_gene_percent_id, 92.85714285714286, places=2)
        self.assertEqual(self.mab.hc1.germlines.nearest_v_genes, ['IGHV3-9*01'])
        self.assertAlmostEqual(self.mab.hc1.germlines.v_gene_percent_id, 92.92929292929293, places=2)

    def test_light_chain_germlines(self):
        self.assertIsNotNone(self.mab.lc1)
        self.assertIsNotNone(self.mab.lc1.germlines)
        self.assertTrue(self.mab.lc1.germlines.chain_is_passable_as_human)
        self.assertAlmostEqual(self.mab.lc1.germlines.humanness, -27.962265320963507, places=2)
        self.assertEqual(self.mab.lc1.germlines.nearest_j_genes, ['IGKJ1*01', 'IGKJ2*01'])
        self.assertAlmostEqual(self.mab.lc1.germlines.j_gene_percent_id, 91.66666666666666, places=2)
        self.assertEqual(self.mab.lc1.germlines.nearest_v_genes, ['IGKV1-27*01', 'IGKV1-27*02', 'IGKV1-27*03'])
        self.assertAlmostEqual(self.mab.lc1.germlines.v_gene_percent_id, 96.73913043478261, places=2)

class TestHeavyChain(unittest.TestCase):
    def setUp(self):
        self.hc = HeavyChain(aa_sequence=HC_SEQ)

    def test_heavy_chain_properties(self):
        self.assertIsNotNone(self.hc.full_chain)
        self.assertIsNotNone(self.hc.full_chain.properties)
        self.assertAlmostEqual(self.hc.full_chain.properties.charge_at_ph(6), 7.166314789980255, places=2)

class TestLightChain(unittest.TestCase):
    def setUp(self):
        self.lc = LightChain(aa_sequence=LC_SEQ)

    def test_light_chain_properties(self):
        self.assertIsNotNone(self.lc.full_chain)
        self.assertIsNotNone(self.lc.full_chain.properties)
        self.assertAlmostEqual(self.lc.full_chain.properties.charge_at_ph(6), 5.28901928311387, places=2)
