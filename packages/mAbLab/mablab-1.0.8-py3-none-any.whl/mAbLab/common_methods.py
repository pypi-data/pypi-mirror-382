from Bio import Align
from typing import List, Tuple


def pairwise_sequence_alignment(reference_sequence: str, test_sequence: str) -> Tuple[str, str]:
    '''
    Aligns similarly sized sequences using Biopython's pairwise aligner.
        
    Args: 
        reference_sequence (str): Reference protein amino acid sequence.
        test_sequence (str): Test protein amino acid sequence.
    
    Returns:
        Tuple[str, str]: Aligned reference and test sequences as strings.
    '''
    def _correct_alignment_for_point_mutations(aligned_ref_seq: List[str], aligned_test_seq: List[str]) -> Tuple[str, str]:
        '''
        Corrects alignment for point mutations by removing unnecessary gaps.
        
        Args:
            aligned_ref_seq (List[str]): Aligned reference sequence as a list of characters.
            aligned_test_seq (List[str]): Aligned test sequence as a list of characters.
        
        Returns:
            Tuple[str, str]: Corrected aligned sequences as strings.
        '''
        for i in reversed(range(1, len(aligned_ref_seq))):
            if aligned_ref_seq[i] == '-' and aligned_test_seq[i - 1] == '-':
                del aligned_ref_seq[i]
                del aligned_test_seq[i - 1]
        return ''.join(aligned_ref_seq), ''.join(aligned_test_seq)

    # Initialize the pairwise aligner
    aligner = Align.PairwiseAligner()
    alignments = aligner.align(reference_sequence, test_sequence)

    # Extract the top alignment
    aligned_ref_seq = list(alignments[0][0])
    aligned_test_seq = list(alignments[0][1])

    # Correct alignment for point mutations
    return _correct_alignment_for_point_mutations(aligned_ref_seq, aligned_test_seq)


def calculate_monoisotopic_mass(sequence_list: List[str], reduced: bool = False) -> float:
    '''
    Calculates the monoisotopic mass of a multi-chain protein list.
        
    Args: 
        sequence_list (List[str]): List of amino acid sequences representing protein chains.
        reduced (bool): Indicates the oxidation state of cysteines (default is False).
    
    Returns:
        float: Molecular weight (Da).
    '''
    # Monoisotopic weights of amino acids
    weights = {
        'A': 71.03711, 'C': 103.00919, 'D': 115.02694, 'E': 129.04259,
        'F': 147.06841, 'G': 57.02146, 'H': 137.05891, 'I': 113.08406,
        'K': 128.09496, 'L': 113.08406, 'M': 131.04049, 'N': 114.04293,
        'P': 97.05276, 'Q': 128.05858, 'R': 156.10111, 'S': 87.03203,
        'T': 101.04768, 'V': 99.06841, 'W': 186.07931, 'Y': 163.06333
    }

    # Adjust for disulfide bonds in oxidized state
    if not reduced:
        weights['C'] = 102.001

    total_mass = 0.0
    for sequence in sequence_list:
        sequence = sequence.upper().strip()
        total_mass += sum(weights[aa] for aa in sequence)
        total_mass += 18.0105 # water mass per chain for termini

    return total_mass


def calculate_average_mass(sequence_list: List[str], reduced: bool = False) -> float:
    '''
    Calculates the average mass of a multi-chain protein list.
        
    Args: 
        sequence_list (List[str]): List of amino acid sequences representing protein chains.
        reduced (bool): Indicates the oxidation state of cysteines (default is False).
    
    Returns:
        float: Molecular weight (Da).
    '''
    # Average weights of amino acids
    weights = {
        'A': 71.0788, 'C': 103.1388, 'D': 115.0886, 'E': 129.1155,
        'F': 147.1766, 'G': 57.0519, 'H': 137.1411, 'I': 113.1594,
        'K': 128.1741, 'L': 113.1594, 'M': 131.1926, 'N': 114.1038,
        'P': 97.1167, 'Q': 128.1307, 'R': 156.1875, 'S': 87.0782,
        'T': 101.1051, 'V': 99.1326, 'W': 186.2132, 'Y': 163.176
    }

    # Adjust for disulfide bonds in oxidized state
    if not reduced:
        weights['C'] = 102.131

    total_mass = 0.0
    for sequence in sequence_list:
        sequence = sequence.upper().strip()
        total_mass += sum(weights[aa] for aa in sequence)
        total_mass += 18.01528 # water mass per chain for termini

    return total_mass


def calculate_e_one_percent(molar_ext_co: float, molecular_weight: float) -> float:
    '''
    Calculates E1% (extinction coefficient at 1% concentration).
    
    Args:
        molar_ext_co (float): Molar extinction coefficient (M^-1 cm^-1).
        molecular_weight (float): Molecular weight (Da).
        
    Returns:
        float: E1% value.
    '''
    return (molar_ext_co / (molecular_weight)*10) if molecular_weight else 0.0 