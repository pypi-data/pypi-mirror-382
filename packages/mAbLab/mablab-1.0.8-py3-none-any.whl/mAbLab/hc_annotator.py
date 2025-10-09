from antpack import SingleChainAnnotator, VJGeneTool, SequenceScoringTool
import Levenshtein
import copy
from . import fc_constants as Fc
from . import fc_align_and_annotate as fc_annotate
from . import common_methods as cm

class AnnotateHC:
    """
    A class to annotate heavy chains (HC) of antibodies.

    Attributes:
        input_aa (str): Input amino acid sequence.
        germlines (_InferGermline): Germline inference results.
        analysis_results (_HC): Heavy chain analysis results.
    """

    def __init__(self, aa_sequence: str = None) -> None:
        """
        Initialize the AnnotateHC object with an amino acid sequence.

        Args:
            aa_sequence (str): Amino acid sequence of the heavy chain.
        """
        self.input_aa = aa_sequence
        self.germlines = self._InferGermline(self.input_aa)
        self.analysis_results = self._HC(self.input_aa)

    class _HC:
        """
        A class to analyze the heavy chain (HC) of an antibody.

        Attributes:
            isotype (str): Isotype of the antibody.
            allotype (str): Allotype of the antibody.
            subclass (str): Subclass of the antibody.
            hc (_DomainObj): Heavy chain domain object.
            fc (_DomainObj): Fc domain object.
            fd (_DomainObj): Fd domain object.
            hinge (_DomainObj): Hinge domain object.
            vh (_DomainObj): Variable heavy chain domain object.
            ch1 (_DomainObj): CH1 domain object.
            ch2 (_DomainObj): CH2 domain object.
            ch3 (_DomainObj): CH3 domain object.
            cdr1 (_CDRObj): CDR1 object.
            cdr2 (_CDRObj): CDR2 object.
            cdr3 (_CDRObj): CDR3 object.
            input_hc_sequence (str): Input heavy chain sequence.
            reference_fc_sequence (str): Reference Fc sequence.
            aligned_reference_fc_sequence (str): Aligned reference Fc sequence.
            aligned_input_fc_sequence (str): Aligned input Fc sequence.
            levenshtein_ratio (float): Levenshtein ratio for sequence alignment.
            inferred_chain_type (str): Inferred chain type.
            inferred_chain_percent_id (float): Inferred chain percent identity.
            analysis_errors (str): Analysis errors.
            fc_mutations (_MutationObj): Fc mutations.
            hinge_is_modified (bool): Whether the hinge is modified.
        """

        def __init__(self, aa_sequence: str = None) -> None:
            """
            Initialize the _HC object with an amino acid sequence.

            Args:
                aa_sequence (str): Amino acid sequence of the heavy chain.
            """
            self.isotype = str
            self.allotype = str
            self.subclass = str
            self.hc = self._DomainObj()
            self.fc = self._DomainObj()
            self.fd = self._DomainObj()
            self.hinge = self._DomainObj()
            self.vh = self._DomainObj()
            self.ch1 = self._DomainObj()
            self.ch2 = self._DomainObj()
            self.ch3 = self._DomainObj()
            self.cdr1 = self._CDRObj()
            self.cdr2 = self._CDRObj()
            self.cdr3 = self._CDRObj()
            self.input_hc_sequence = aa_sequence
            self.reference_fc_sequence = str
            self.aligned_reference_fc_sequence = str
            self.aligned_input_fc_sequence = str
            self.levenshtein_ratio = float
            self.inferred_chain_type = str
            self.inferred_chain_percent_id = float
            self.analysis_errors = str
            self.fc_mutations = self._MutationObj()
            self.hinge_is_modified = False
            self._reference_hinge_len = int
            self._ch1_hinge_ch2_ch3_annotation, self.isotype = fc_annotate.annotate_isotype_and_constant_regions(aa_sequence)
            self._align_to_nearest_reference_fc()
            self._number_and_annotate_hc()
        class _MutationObj:
            """
            A class to represent mutations in the Fc region.

            Attributes:
                deletion (_MutationSystemObj): Deletions in the Fc region.
                insertion (_MutationSystemObj): Insertions in the Fc region.
                mutation (_MutationSystemObj): Point mutations in the Fc region.
            """

            def __init__(self) -> None:
                """
                Initialize the _MutationObj object.
                """
                self.deletion = self._MutationSystemObj()
                self.insertion = self._MutationSystemObj()
                self.mutation = self._MutationSystemObj()

            class _MutationSystemObj:
                """
                A class to represent a mutation system object.

                Attributes:
                    imgt (list): IMGT numbering for mutations.
                    imgt_unique (list): Unique IMGT numbering for mutations.
                    eu (list): EU numbering for mutations.
                    kabat (list): Kabat numbering for mutations.
                    martin (list): Martin numbering for mutations.
                    aho (list): AHO numbering for mutations.
                """

                def __init__(self) -> None:
                    """
                    Initialize the _MutationSystemObj object.
                    """
                    self.imgt = []
                    self.imgt_unique = []
                    self.eu = []
                    self.kabat = []
                    self.martin = []
                    self.aho = []

                def __len__(self) -> int:
                    """
                    Get the length of the mutation system object.

                    Returns:
                        int: Maximum length of the mutation lists.
                    """
                    return max(len(self.imgt), len(self.eu), len(self.kabat), len(self.martin), len(self.aho))

        class _DomainObj:
            """
            A class to represent a domain object.

            Attributes:
                sequence (str): Sequence of the domain.
                numbering (_NumberingSystemObj): Numbering system object.
                annotation (_NumberingSystemObj): Annotation system object.
            """

            def __init__(self) -> None:
                """
                Initialize the _DomainObj object.
                """
                self.sequence = str
                self.numbering = self._NumberingSystemObj()
                self.annotation = self._NumberingSystemObj()

            class _NumberingSystemObj:
                """
                A class to represent a numbering system object.

                Attributes:
                    imgt (list): IMGT numbering.
                    imgt_unique (list): Unique IMGT numbering.
                    eu (list): EU numbering.
                    kabat (list): Kabat numbering.
                    martin (list): Martin numbering.
                    aho (list): AHO numbering.
                """

                def __init__(self) -> None:
                    """
                    Initialize the _NumberingSystemObj object.
                    """
                    self.imgt = []
                    self.imgt_unique = []
                    self.eu = []
                    self.kabat = []
                    self.martin = []
                    self.aho = []

            def collapse_aa_sequence_numbering_and_annotation(self):
                if self.sequence is None or len(self.sequence) < 1:
                    return
                
                del_idx = [index for index, value in enumerate(self.sequence) if value == '-']
                
                def _remove_by_index(item_lst):
                    if item_lst is None:
                        return item_lst
                    
                    for idx in reversed(del_idx):
                        if len(item_lst) >= idx:
                            del item_lst[idx]
                    return item_lst
                
                self.sequence = ''.join(_remove_by_index(list(self.sequence)))
                self.numbering.imgt = _remove_by_index(self.numbering.imgt )
                self.numbering.eu = _remove_by_index(self.numbering.eu)
                self.numbering.kabat = _remove_by_index(self.numbering.kabat)
                self.numbering.martin = _remove_by_index(self.numbering.martin)
                self.numbering.aho = _remove_by_index(self.numbering.aho)
                self.annotation.imgt = _remove_by_index(self.annotation.imgt)
                self.annotation.eu = _remove_by_index(self.annotation.eu)
                self.annotation.kabat = _remove_by_index(self.annotation.kabat)
                self.annotation.martin = _remove_by_index(self.annotation.martin)
                self.annotation.aho = _remove_by_index(self.annotation.aho)
                return
            

        class _CDRObj(_DomainObj):
            """
            A class to represent a CDR object.

            Attributes:
                sequence (_CDRSchemeObj): CDR scheme object.
            """

            def __init__(self) -> None:
                """
                Initialize the _CDRObj object.
                """
                super().__init__()
                self.sequence = self._CDRSchemeObj()

            class _CDRSchemeObj:
                """
                A class to represent a CDR scheme object.

                Attributes:
                    imgt (list): IMGT CDR scheme.
                    eu (list): EU CDR scheme.
                    kabat (list): Kabat CDR scheme.
                    martin (list): Martin CDR scheme.
                    aho (list): AHO CDR scheme.
                """

                def __init__(self) -> None:
                    """
                    Initialize the _CDRSchemeObj object.
                    """
                    self.imgt = []
                    self.eu = []
                    self.kabat = []
                    self.martin = []
                    self.aho = []

        def _align_to_nearest_reference_fc(self) -> None:
            """
            Align the input heavy chain to the nearest Fc reference sequence.
            Defines object properties such as isotype, subclass, and Fc alignment.
            """
            
            def _isotype_by_hinge_match(hc_sequence: str) -> None:
                '''match hinge sequence to identify isotype.  This is the preferred method to capture the hinge start index'''

                # Match Full Hinge
                for hinge in Fc.hinge:
                    if hinge['sequence'] in hc_sequence:
                        self.isotype = hinge['name']
                        self.hinge_is_modified = False
                        return
                # Else Match 7-mer of hinge
                for hinge in Fc.hinge:
                    for i in range(0, len(hinge['sequence'])-7):
                        segment = hinge['sequence'][i:i+7]
                        if segment in hc_sequence:
                            self.isotype = hinge['name']
                            self.hinge_is_modified = True
                            return
                self.isotype = self._ch1_hinge_ch2_ch3_annotation['isotype']
                self.hinge_is_modified = None
                return
            
            def _find_nearest_fc_reference_match_by_alignment(hc_sequence: str) -> None:
                '''Find Nearest Fc Reference Sequence. If hinge is modified this method requires blind truncation and may lead to errors if the Fc has c-terminal fusions or significant modifications'''
                
                def _truncate_input_sequence(hc_sequence: str) -> str:
                    '''truncate HC to Fc by hinge match or by max reference FC length'''
                    if self.hinge_is_modified is False:
                        for hinge in Fc.hinge:
                            if hinge['name'] == self.isotype:
                                return  hc_sequence[hc_sequence.index(hinge['sequence']):]
                    else:
                        max_len = 0
                        for seq in Fc.sequences:
                            fc_seq = seq['sequence']
                            max_len = len(fc_seq) if len(fc_seq) > max_len else max_len
                        max_len += 10
                        return hc_sequence[-1*max_len:] if max_len <= len(hc_sequence) else hc_sequence
                    return
                
                def _get_reference_sequence_by_levenshtein_ratio(truncated_input_sequence: str) -> str:
                    '''Calculate levenshtein ratio and select nearest Fc match'''
                    ratios = []
                    all_fc_seq_dicts = []
                    # Calc Levenshtein ratios
                    for seq in Fc.sequences:
                        ratios.append(Levenshtein.ratio(seq['sequence'], truncated_input_sequence))
                        all_fc_seq_dicts.append(seq)
                    # Identify best Fc Match and add calculated ratio to object
                    max_idx = ratios.index(max(ratios))
                    reference_fc_dict = all_fc_seq_dicts[max_idx]
                    self.levenshtein_ratio = ratios[max_idx]
                    # Prepare Reference Fc for alignment
                    hinge_start_idx = reference_fc_dict['hinge_start_idx']
                    self.isotype = reference_fc_dict['isotype']
                    self.allotype = reference_fc_dict['allotype']
                    self.subclass = reference_fc_dict['subclass']
                    self._reference_hinge_len = reference_fc_dict['hinge_len']
                    self.reference_fc_sequence = reference_fc_dict['sequence'][hinge_start_idx:]
                    return self.reference_fc_sequence
                
                def _align_input_fc_to_reference_fc(truncated_input_sequence: str, truncated_reference_sequence: str) -> None:
                    '''aligns similarly sized sequences via biopython pairwise aligner'''
                    # Align input sequence to top matched reference sequence
                    aligned_ref_seq, aligned_input_seq = cm.pairwise_sequence_alignment(truncated_reference_sequence, truncated_input_sequence)
                    # Trim Aligned Sequences to begin at first Hinge residue
                    ref_start_idx = aligned_ref_seq.index(truncated_reference_sequence[0])
                    self.aligned_reference_fc_sequence = aligned_ref_seq[ref_start_idx:]
                    self.aligned_input_fc_sequence = aligned_input_seq[ref_start_idx:] 
                    return
                    
                # Entry Point
                truncated_input_sequence = _truncate_input_sequence(hc_sequence)
                truncated_reference_sequence = _get_reference_sequence_by_levenshtein_ratio(truncated_input_sequence)
                _align_input_fc_to_reference_fc(truncated_input_sequence, truncated_reference_sequence)
                return
            
            # Entry Point
            _isotype_by_hinge_match(self.input_hc_sequence)
            _find_nearest_fc_reference_match_by_alignment(self.input_hc_sequence)
            return
            
    
        def _number_and_annotate_hc(self) -> None:
            """
            Number and annotate the heavy chain.
            This version uses a master annotation list to explicitly construct the hinge
            and other constant domains, with robust numbering for modification sites.
            """
            
            def _get_input_vh():
                """
                Number and annotate the variable heavy chain (VH).
                """
                def _calculate(scheme):
                    aligner = SingleChainAnnotator(scheme=scheme)
                    annotation = aligner.analyze_seq(self.input_hc_sequence)
                    numbering, self.inferred_chain_percent_id, chain, self.analysis_errors = annotation
                    self.inferred_chain_percent_id = self.inferred_chain_percent_id * 100
                    chain = chain.upper()
                    self.inferred_chain_type = 'HC' if chain == 'H' else 'Kappa LC' if chain == 'K' else 'Lambda LC' if chain == 'L' else 'unknown'
                    annotation = aligner.assign_cdr_labels(annotation)
                    vh_last_idx = len(annotation) - annotation[::-1].index('fmwk4') - 1
                    return ([str(n) for n in numbering[:vh_last_idx]], [d + ' [VH]' for d in annotation[:vh_last_idx]])

                self.vh.numbering.imgt, self.vh.annotation.imgt = _calculate('imgt')
                self.vh.numbering.eu, self.vh.annotation.eu = _calculate('imgt')
                self.vh.numbering.kabat, self.vh.annotation.kabat = _calculate('kabat')
                self.vh.numbering.martin, self.vh.annotation.martin = _calculate('martin')
                self.vh.numbering.aho, self.vh.annotation.aho = _calculate('aho')
                self.vh.sequence = self.input_hc_sequence[:len(self.vh.numbering.imgt)]
                self.vh.numbering.imgt_unique = copy.deepcopy(self.vh.numbering.imgt)
                return
                
            def _annotate_hinge():
                """
                Explicitly constructs the Hinge domain object from the master annotation list.
                """
                annotation_data = self._ch1_hinge_ch2_ch3_annotation
                domain_obj = self.hinge

                # Ensure all hinge attributes are lists before appending
                domain_obj.sequence = []
                domain_obj.numbering.eu = []
                domain_obj.numbering.kabat = []
                domain_obj.numbering.imgt = []
                domain_obj.numbering.imgt_unique = []
                domain_obj.annotation.eu = []
                domain_obj.annotation.kabat = []
                domain_obj.annotation.imgt = []
                domain_obj.annotation.imgt_unique = []

                for idx, item in enumerate(annotation_data):
                    if 'hinge' not in item.get('domain', '').lower():
                        continue  # Only process hinge residues

                    aa_char = item.get('AA', item.get('aa'))
                    note = item.get('note', '')

                    # Mutations/insertions/deletions logic (unchanged)
                    if note.startswith('deletion'):
                        try:
                            ref_aa = note[note.find('(') + 1:note.find(')')].strip()
                        except IndexError:
                            ref_aa = '?'
                        self.fc_mutations.deletion.eu.append({'name': f"{item['eu']}{ref_aa}", 'position': f"{item['eu']}", 'amino_acid': ref_aa})
                        self.fc_mutations.deletion.imgt.append({'name': f"{item['imgt']}{ref_aa}", 'position': f"{item['imgt']}", 'amino_acid': ref_aa})
                        self.fc_mutations.deletion.kabat.append({'name': f"{item['kabat']}{ref_aa}", 'position': f"{item['kabat']}", 'amino_acid': ref_aa})
                        self.fc_mutations.deletion.imgt_unique.append({'name': f"{item['imgt-unique']}{ref_aa}", 'position': f"{item['imgt-unique']}", 'amino_acid': ref_aa})
                        continue
                    
                    elif note == 'insertion':
                        prev_item_context = None
                        for k in range(idx - 1, -1, -1):
                            if annotation_data[k].get('note', '') != 'insertion':
                                prev_item_context = annotation_data[k]
                                break
                        if not prev_item_context: continue
                        
                        insertion_count = 0
                        for j in range(idx, -1, -1):
                            if annotation_data[j].get('note', '') == 'insertion': insertion_count += 1
                            else: break
                        suffix = chr(64 + insertion_count)

                        pos_eu = f"{prev_item_context['eu']}{suffix}"
                        pos_kabat = f"{prev_item_context['kabat']}{suffix}"
                        pos_imgt = f"{prev_item_context['imgt']}{suffix}"
                        pos_imgt_unique = f"{prev_item_context['imgt-unique']}{suffix}"
                        
                        self.fc_mutations.insertion.eu.append({'name': f"{pos_eu}{aa_char}", 'position': pos_eu, 'amino_acid': aa_char})
                        self.fc_mutations.insertion.imgt.append({'name': f"{pos_imgt}{aa_char}", 'position': pos_imgt, 'amino_acid': aa_char})
                        self.fc_mutations.insertion.kabat.append({'name': f"{pos_kabat}{aa_char}", 'position': pos_kabat, 'amino_acid': aa_char})
                        self.fc_mutations.insertion.imgt_unique.append({'name': f"{pos_imgt_unique}{aa_char}", 'position': pos_imgt_unique, 'amino_acid': aa_char})

                    elif note.startswith('mutation'):
                        try:
                            ref_aa, mut_aa = [x.strip() for x in note[note.find('(') + 1:note.find(')')].split('->')]
                        except (IndexError, ValueError):
                            ref_aa, mut_aa = '?', aa_char
                        self.fc_mutations.mutation.eu.append({'name': f"{ref_aa}{item['eu']}{mut_aa}", 'position': f"{item['eu']}", 'reference_amino_acid': ref_aa, 'mutant_amino_acid': mut_aa})
                        self.fc_mutations.mutation.imgt.append({'name': f"{ref_aa}{item['imgt']}{mut_aa}", 'position': f"{item['imgt']}", 'reference_amino_acid': ref_aa, 'mutant_amino_acid': mut_aa})
                        self.fc_mutations.mutation.kabat.append({'name': f"{ref_aa}{item['kabat']}{mut_aa}", 'position': f"{item['kabat']}", 'reference_amino_acid': ref_aa, 'mutant_amino_acid': mut_aa})
                        self.fc_mutations.mutation.imgt_unique.append({'name': f"{ref_aa}{item['imgt-unique']}{mut_aa}", 'position': f"{item['imgt-unique']}", 'reference_amino_acid': ref_aa, 'mutant_amino_acid': mut_aa})
                        continue

                    # Append data to the hinge object
                    domain_obj.sequence.append(aa_char)
                    domain_obj.numbering.eu.append(str(item.get('eu', '-')))
                    domain_obj.numbering.kabat.append(str(item.get('kabat', '-')))
                    domain_obj.numbering.imgt.append(str(item.get('imgt', '-')))
                    domain_obj.numbering.imgt_unique.append(str(item.get('imgt-unique', '-')))
                    annotation_text = f"{item.get('structure', 'Hinge')} [Hinge]"
                    domain_obj.annotation.eu.append(annotation_text)
                    domain_obj.annotation.kabat.append(annotation_text)
                    domain_obj.annotation.imgt.append(annotation_text)
                    domain_obj.annotation.imgt_unique.append(annotation_text)

                # Join sequence list to string after population
                if isinstance(domain_obj.sequence, list):
                    domain_obj.sequence = "".join(domain_obj.sequence)
                return

            def _process_constant_regions_and_mutations():
                """
                Annotates CH1, CH2, and CH3 domains from the master annotation list.
                """
                annotation_data = self._ch1_hinge_ch2_ch3_annotation
                domain_map = {'CH1': self.ch1, 'Hinge': self.hinge, 'CH2': self.ch2, 'CH3': self.ch3}

                # Ensure all .sequence and .numbering/.annotation attributes are lists before appending
                for domain_obj in domain_map.values():
                    domain_obj.sequence = []
                    domain_obj.numbering.eu = []
                    domain_obj.numbering.kabat = []
                    domain_obj.numbering.imgt = []
                    domain_obj.numbering.imgt_unique = []
                    domain_obj.annotation.eu = []
                    domain_obj.annotation.kabat = []
                    domain_obj.annotation.imgt = []
                    domain_obj.annotation.imgt_unique = []

                for idx, item in enumerate(annotation_data):
                    domain_name = item.get('domain')
                    
                    if 'hinge' in domain_name.lower():
                        domain_obj = self.hinge
                    elif domain_name in domain_map:
                        domain_obj = domain_map[domain_name]
                    else:
                        continue # Skip non-target domains

                    aa_char = item.get('AA', item.get('aa'))
                    note = item.get('note', '')

                    if note.startswith('deletion'):
                        if domain_name in ['CH2', 'CH3']:
                            try:
                                ref_aa = note[note.find('(') + 1:note.find(')')].strip()
                            except IndexError: ref_aa = '?'
                            self.fc_mutations.deletion.eu.append({'name': f"{item['eu']}{ref_aa}", 'position': f"{item['eu']}", 'amino_acid': ref_aa})
                            self.fc_mutations.deletion.imgt.append({'name': f"{item['imgt']}{ref_aa}", 'position': f"{item['imgt']}", 'amino_acid': ref_aa})
                            self.fc_mutations.deletion.kabat.append({'name': f"{item['kabat']}{ref_aa}", 'position': f"{item['kabat']}", 'amino_acid': ref_aa})
                            self.fc_mutations.deletion.imgt_unique.append({'name': f"{item['imgt-unique']}{ref_aa}", 'position': f"{item['imgt-unique']}", 'amino_acid': ref_aa})
                        continue

                    elif note.startswith('mutation'):
                        if domain_name in ['CH2', 'CH3']:
                            try:
                                ref_aa, mut_aa = [x.strip() for x in note[note.find('(') + 1:note.find(')')].split('->')]
                            except (IndexError, ValueError): ref_aa, mut_aa = '?', aa_char
                            self.fc_mutations.mutation.eu.append({'name': f"{ref_aa}{item['eu']}{mut_aa}", 'position': f"{item['eu']}", 'reference_amino_acid': ref_aa, 'mutant_amino_acid': mut_aa})
                            self.fc_mutations.mutation.imgt.append({'name': f"{ref_aa}{item['imgt']}{mut_aa}", 'position': f"{item['imgt']}", 'reference_amino_acid': ref_aa, 'mutant_amino_acid': mut_aa})
                            self.fc_mutations.mutation.kabat.append({'name': f"{ref_aa}{item['kabat']}{mut_aa}", 'position': f"{item['kabat']}", 'reference_amino_acid': ref_aa, 'mutant_amino_acid': mut_aa})
                            self.fc_mutations.mutation.imgt_unique.append({'name': f"{ref_aa}{item['imgt-unique']}{mut_aa}", 'position': f"{item['imgt-unique']}", 'reference_amino_acid': ref_aa, 'mutant_amino_acid': mut_aa})
                    
                    domain_obj.sequence.append(aa_char)
                    domain_obj.numbering.eu.append(str(item['eu']))
                    domain_obj.numbering.kabat.append(str(item['kabat']))
                    domain_obj.numbering.imgt.append(str(item['imgt']))
                    domain_obj.numbering.imgt_unique.append(str(item['imgt-unique']))
                    annotation_text = f"{item.get('structure', '-')} [{domain_name}]"
                    domain_obj.annotation.eu.append(annotation_text)
                    domain_obj.annotation.kabat.append(annotation_text)
                    domain_obj.annotation.imgt.append(annotation_text)
                    domain_obj.annotation.imgt_unique.append(annotation_text)
                for domain_name, domain_obj in domain_map.items():
                    # Only join if .sequence is a list (avoid error if already a string)
                    if isinstance(domain_obj.sequence, list):
                        domain_obj.sequence = "".join(domain_obj.sequence)
                return

            def _construct_fc_obj():
                """Constructs the Fc object by combining CH2 and CH3."""
                if self.ch2.sequence is None or self.ch3.sequence is None: return
                self.fc.sequence = self.ch2.sequence + self.ch3.sequence
                self.fc.annotation.imgt = self.ch2.annotation.imgt + self.ch3.annotation.imgt
                self.fc.annotation.eu = self.ch2.annotation.eu + self.ch3.annotation.eu
                self.fc.annotation.kabat = self.ch2.annotation.kabat + self.ch3.annotation.kabat
                self.fc.numbering.eu = self.ch2.numbering.eu + self.ch3.numbering.eu
                self.fc.numbering.imgt = self.ch2.numbering.imgt + self.ch3.numbering.imgt
                self.fc.numbering.kabat = self.ch2.numbering.kabat + self.ch3.numbering.kabat
                self.fc.numbering.imgt_unique = self.ch2.numbering.imgt_unique + self.ch3.numbering.imgt_unique
                return

            def _construct_fd_obj():
                """Constructs the Fd object by combining VH and CH1."""
                if self.vh.sequence is None or self.ch1.sequence is None: return
                self.fd.sequence = self.vh.sequence + self.ch1.sequence
                self.fd.annotation.imgt = self.vh.annotation.imgt + self.ch1.annotation.imgt
                self.fd.annotation.eu = self.vh.annotation.eu + self.ch1.annotation.eu
                self.fd.annotation.kabat = self.vh.annotation.kabat + self.ch1.annotation.kabat
                self.fd.annotation.martin = (self.vh.annotation.martin or []) + ['-'] * len(self.ch1.sequence)
                self.fd.annotation.aho = (self.vh.annotation.aho or []) + ['-'] * len(self.ch1.sequence)
                self.fd.numbering.eu = self.vh.numbering.eu + self.ch1.numbering.eu
                self.fd.numbering.imgt = self.vh.numbering.imgt + self.ch1.numbering.imgt
                self.fd.numbering.kabat = self.vh.numbering.kabat + self.ch1.numbering.kabat
                self.fd.numbering.martin = (self.vh.numbering.martin or []) + ['-'] * len(self.ch1.sequence)
                self.fd.numbering.aho = (self.vh.numbering.aho or []) + ['-'] * len(self.ch1.sequence)
                self.fd.numbering.imgt_unique = (self.vh.numbering.imgt_unique or []) + self.ch1.numbering.imgt_unique
                return
            
            def _construct_hc_obj():
                """Constructs the full Heavy Chain object from its constituent parts."""
                if self.fd.sequence is None or self.hinge.sequence is None or self.fc.sequence is None: return
                self.hc.sequence = self.fd.sequence + self.hinge.sequence + self.fc.sequence
                self.hc.annotation.imgt = self.fd.annotation.imgt + self.hinge.annotation.imgt + self.fc.annotation.imgt
                self.hc.annotation.eu = self.fd.annotation.eu + self.hinge.annotation.eu + self.fc.annotation.eu
                self.hc.annotation.kabat = self.fd.annotation.kabat + self.hinge.annotation.kabat + self.fc.annotation.kabat
                padding = ['-'] * len(self.hinge.sequence) + ['-'] * len(self.fc.sequence)
                self.hc.annotation.martin = self.fd.annotation.martin + padding
                self.hc.annotation.aho = self.fd.annotation.aho + padding
                self.hc.numbering.eu = self.fd.numbering.eu + self.hinge.numbering.eu + self.fc.numbering.eu
                self.hc.numbering.imgt = self.fd.numbering.imgt + self.hinge.numbering.imgt + self.fc.numbering.imgt
                self.hc.numbering.kabat = self.fd.numbering.kabat + self.hinge.numbering.kabat + self.fc.numbering.kabat
                self.hc.numbering.martin = self.fd.numbering.martin + padding
                self.hc.numbering.aho = self.fd.numbering.aho + padding
                self.hc.numbering.imgt_unique = self.fd.numbering.imgt_unique + self.hinge.numbering.imgt_unique + self.fc.numbering.imgt_unique
                return
            
            def _construct_cdr_obj():
                """Constructs CDR objects from the annotated VH domain."""
                if self.vh.numbering.imgt is None: return
                schemes = [{'name': 'imgt', 'vh_numbering': self.vh.numbering.imgt, 'vh_annotation': self.vh.annotation.imgt},
                        {'name': 'eu', 'vh_numbering': self.vh.numbering.imgt, 'vh_annotation': self.vh.annotation.imgt},
                        {'name': 'martin', 'vh_numbering': self.vh.numbering.martin, 'vh_annotation': self.vh.annotation.martin},
                        {'name': 'kabat', 'vh_numbering': self.vh.numbering.kabat, 'vh_annotation': self.vh.annotation.kabat},
                        {'name': 'aho', 'vh_numbering': self.vh.numbering.aho, 'vh_annotation': self.vh.annotation.aho}]
                for s in schemes:
                    seq1, num1, annote1, seq2, num2, annote2, seq3, num3, annote3 = [], [], [], [], [], [], [], [], []
                    annotation, numbering = s['vh_annotation'], s['vh_numbering']
                    if annotation is None or numbering is None: continue
                    for i in range(len(self.vh.sequence)):
                        if 'cdr1' in annotation[i]:
                            seq1.append(self.vh.sequence[i]); num1.append(numbering[i]); annote1.append(annotation[i])
                        elif 'cdr2' in annotation[i]:
                            seq2.append(self.vh.sequence[i]); num2.append(numbering[i]); annote2.append(annotation[i])
                        elif 'cdr3' in annotation[i]:
                            seq3.append(self.vh.sequence[i]); num3.append(numbering[i]); annote3.append(annotation[i])
                    cdr1_obj, cdr2_obj, cdr3_obj = getattr(self, 'cdr1'), getattr(self, 'cdr2'), getattr(self, 'cdr3')
                    setattr(cdr1_obj.sequence, s['name'], "".join(seq1)); setattr(cdr1_obj.annotation, s['name'], annote1); setattr(cdr1_obj.numbering, s['name'], num1)
                    setattr(cdr2_obj.sequence, s['name'], "".join(seq2)); setattr(cdr2_obj.annotation, s['name'], annote2); setattr(cdr2_obj.numbering, s['name'], num2)
                    setattr(cdr3_obj.sequence, s['name'], "".join(seq3)); setattr(cdr3_obj.annotation, s['name'], annote3); setattr(cdr3_obj.numbering, s['name'], num3)
                return

            # --- Main Execution Flow ---
            _get_input_vh()
            _annotate_hinge()
            _process_constant_regions_and_mutations()
            _construct_fc_obj()
            _construct_fd_obj()
            _construct_hc_obj()
            _construct_cdr_obj()
            return
        
    class _InferGermline:
        """
        A class to infer the germline of an antibody.

        Attributes:
            humanness (float): Humanness score.
            nearest_v_genes (list): Nearest V genes.
            v_gene_percent_id (float): V gene percent identity.
            nearest_j_genes (list): Nearest J genes.
            j_gene_percent_id (float): J gene percent identity.
            chain_is_passable_as_human (bool): Whether the chain is passable as human.
        """

        def __init__(self, aa_sequence: str = None) -> None:
            """
            Initialize the _InferGermline object with an amino acid sequence.

            Args:
                aa_sequence (str): Amino acid sequence of the heavy chain.
            """
            self.humanness = float
            self.nearest_v_genes = list
            self.v_gene_percent_id = float
            self.nearest_j_genes = list
            self.j_gene_percent_id = float
            self.chain_is_passable_as_human = bool
            self._calculate_germline(aa_sequence)

        def _calculate_germline(self, aa_sequence: str = None) -> None:
            """
            Calculate the germline of the heavy chain.

            Args:
                aa_sequence (str): Amino acid sequence of the heavy chain.
            """
            aligner = SingleChainAnnotator(scheme= 'imgt')
            annotation = aligner.analyze_seq(aa_sequence)
            
            vj_tool = VJGeneTool(database='imgt', scheme='imgt')
            self.nearest_v_genes, self.nearest_j_genes, self.v_gene_percent_id, self.j_gene_percent_id = vj_tool.assign_vj_genes(annotation, aa_sequence, "human", "identity")
            self.nearest_v_genes= self.nearest_v_genes.split('_')
            self.nearest_j_genes= self.nearest_j_genes.split('_')
            self.v_gene_percent_id = self.v_gene_percent_id * 100
            self.j_gene_percent_id = self.j_gene_percent_id * 100
                
            scoring_tool = SequenceScoringTool(offer_classifier_option = False, normalization = "none")
            humanness = scoring_tool.score_seqs(seq_list=[aa_sequence])
            self.humanness = float(humanness[0])
            self.chain_is_passable_as_human = True if humanness >=-100 else False
            return