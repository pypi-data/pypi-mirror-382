from antpack import SingleChainAnnotator, VJGeneTool, SequenceScoringTool

class AnnotateLC:
    """
    A class to annotate light chains (LC) of antibodies.

    Attributes:
        input_aa (str): Input amino acid sequence.
        germlines (_InferGermline): Germline inference results.
        analysis_results (_LC): Light chain analysis results.
    """

    def __init__(self, aa_sequence: str = None) -> None:
        """
        Initialize the AnnotateLC object with an amino acid sequence.

        Args:
            aa_sequence (str): Amino acid sequence of the light chain.
        """
        self.input_aa = aa_sequence
        self.germlines = self._InferGermline(self.input_aa)
        self.analysis_results = self._LC(self.input_aa)

    class _LC:
        """
        A class to analyze the light chain (LC) of an antibody.

        Attributes:
            isotype (str): Isotype of the antibody.
            allotype (str): Allotype of the antibody.
            subclass (str): Subclass of the antibody.
            lc (_DomainObj): Light chain domain object.
            vl (_DomainObj): Variable light chain domain object.
            cl (_DomainObj): Constant light chain domain object.
            cdr1 (_CDRObj): CDR1 object.
            cdr2 (_CDRObj): CDR2 object.
            cdr3 (_CDRObj): CDR3 object.
            inferred_chain_type (str): Inferred chain type.
            inferred_chain_percent_id (float): Inferred chain percent identity.
            analysis_errors (str): Analysis errors.
            input_lc_sequence (str): Input light chain sequence.
        """

        def __init__(self, aa_sequence: str = None) -> None:
            """
            Initialize the _LC object with an amino acid sequence.

            Args:
                aa_sequence (str): Amino acid sequence of the light chain.
            """
            self.isotype = str
            self.allotype = str
            self.subclass = str
            self.lc = self._DomainObj()
            self.vl = self._DomainObj()
            self.cl = self._DomainObj()
            self.cdr1 = self._CDRObj()
            self.cdr2 = self._CDRObj()
            self.cdr3 = self._CDRObj()
            self.inferred_chain_type = str
            self.inferred_chain_percent_id = float
            self.analysis_errors = str
            self.input_lc_sequence = aa_sequence
            self._number_and_annotate_lc()

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
                    self.eu = []
                    self.kabat = []
                    self.martin = []
                    self.aho = []

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

        def _number_and_annotate_lc(self) -> None:
            """
            Number and annotate the light chain.
            """

            def _calculate(scheme: str):
                aligner = SingleChainAnnotator(scheme=scheme)
                annotation = aligner.analyze_seq(self.input_lc_sequence)
                numbering, self.inferred_chain_percent_id, chain, self.analysis_errors = annotation
                self.inferred_chain_percent_id = self.inferred_chain_percent_id * 100
                chain = chain.upper()
                self.inferred_chain_type = 'HC' if chain == 'H' else 'Kappa LC' if chain == 'K' else 'Lambda LC' if chain == 'L' else 'unknown'
                annotation = aligner.assign_cdr_labels(annotation)
                vl_last_idx = len(annotation) - annotation[::-1].index('fmwk4') - 1
                return ([str(n) for n in numbering[:vl_last_idx]], [d + ' [VL]' for d in annotation[:vl_last_idx]], [str(int(numbering[vl_last_idx]) + n) for n in range(len(numbering[vl_last_idx:]))], ['[CL]' for d in annotation[vl_last_idx:]])

            def _construct_cdr_obj():
                scheme = [{'name': 'imgt', 'vl_numbering': self.vl.numbering.imgt, 'vl_annotation': self.vl.annotation.imgt},
                          {'name': 'eu', 'vl_numbering': self.vl.numbering.imgt, 'vl_annotation': self.vl.annotation.imgt},
                          {'name': 'martin', 'vl_numbering': self.vl.numbering.martin, 'vl_annotation': self.vl.annotation.martin},
                          {'name': 'kabat', 'vl_numbering': self.vl.numbering.kabat, 'vl_annotation': self.vl.annotation.kabat},
                          {'name': 'aho', 'vl_numbering': self.vl.numbering.aho, 'vl_annotation': self.vl.annotation.aho}]

                for s in scheme:
                    seq1 = []
                    num1 = []
                    annote1 = []
                    seq2 = []
                    num2 = []
                    annote2 = []
                    seq3 = []
                    num3 = []
                    annote3 = []
                    annotation = s['vl_annotation']
                    numbering = s['vl_numbering']
                    for i in range(len(self.vl.sequence)):
                        if 'cdr1' in annotation[i]:
                            seq1.append(self.vl.sequence[i])
                            num1.append(numbering[i])
                            annote1.append(annotation[i])
                        elif 'cdr2' in annotation[i]:
                            seq2.append(self.vl.sequence[i])
                            num2.append(numbering[i])
                            annote2.append(annotation[i])
                        elif 'cdr3' in annotation[i]:
                            seq3.append(self.vl.sequence[i])
                            num3.append(numbering[i])
                            annote3.append(annotation[i])
                    if s['name'] == 'imgt':
                        self.cdr1.sequence.imgt = seq1
                        self.cdr1.annotation.imgt = annote1
                        self.cdr1.numbering.imgt = num1
                        self.cdr2.sequence.imgt = seq2
                        self.cdr2.annotation.imgt = annote2
                        self.cdr2.numbering.imgt = num2
                        self.cdr3.sequence.imgt = seq3
                        self.cdr3.annotation.imgt = annote3
                        self.cdr3.numbering.imgt = num3
                    if s['name'] == 'eu':
                        self.cdr1.sequence.eu = seq1
                        self.cdr1.annotation.eu = annote1
                        self.cdr1.numbering.eu = num1
                        self.cdr2.sequence.eu = seq2
                        self.cdr2.annotation.eu = annote2
                        self.cdr2.numbering.eu = num2
                        self.cdr3.sequence.eu = seq3
                        self.cdr3.annotation.eu = annote3
                        self.cdr3.numbering.eu = num3
                    if s['name'] == 'kabat':
                        self.cdr1.sequence.kabat = seq1
                        self.cdr1.annotation.kabat = annote1
                        self.cdr1.numbering.kabat = num1
                        self.cdr2.sequence.kabat = seq2
                        self.cdr2.annotation.kabat = annote2
                        self.cdr2.numbering.kabat = num2
                        self.cdr3.sequence.kabat = seq3
                        self.cdr3.annotation.kabat = annote3
                        self.cdr3.numbering.kabat = num3
                    if s['name'] == 'martin':
                        self.cdr1.sequence.martin = seq1
                        self.cdr1.annotation.martin = annote1
                        self.cdr1.numbering.martin = num1
                        self.cdr2.sequence.martin = seq2
                        self.cdr2.annotation.martin = annote2
                        self.cdr2.numbering.martin = num2
                        self.cdr3.sequence.martin = seq3
                        self.cdr3.annotation.martin = annote3
                        self.cdr3.numbering.martin = num3
                    if s['name'] == 'aho':
                        self.cdr1.sequence.aho = seq1
                        self.cdr1.annotation.aho = annote1
                        self.cdr1.numbering.aho = num1
                        self.cdr2.sequence.aho = seq2
                        self.cdr2.annotation.aho = annote2
                        self.cdr2.numbering.aho = num2
                        self.cdr3.sequence.aho = seq3
                        self.cdr3.annotation.aho = annote3
                        self.cdr3.numbering.aho = num3
                return

            # Entry Point
            self.vl.numbering.imgt, self.vl.annotation.imgt, self.cl.numbering.imgt, self.cl.annotation.imgt = _calculate('imgt')
            self.vl.numbering.eu, self.vl.annotation.eu, self.cl.numbering.eu, self.cl.annotation.eu = _calculate('imgt')
            self.vl.numbering.kabat, self.vl.annotation.kabat, self.cl.numbering.kabat, self.cl.annotation.kabat = _calculate('kabat')
            self.vl.numbering.martin, self.vl.annotation.martin, self.cl.numbering.martin, self.cl.annotation.martin = _calculate('martin')
            self.vl.numbering.aho, self.vl.annotation.aho, self.cl.numbering.aho, self.cl.annotation.aho = _calculate('aho')
            self.vl.sequence = self.input_lc_sequence[:len(self.vl.numbering.imgt)]
            self.cl.sequence = self.input_lc_sequence[len(self.vl.numbering.imgt):]
            self.lc.sequence = self.input_lc_sequence
            self.lc.numbering.imgt, self.lc.annotation.imgt = (self.vl.numbering.imgt + self.cl.numbering.imgt, self.vl.annotation.imgt + self.cl.annotation.imgt)
            self.lc.numbering.eu, self.lc.annotation.eu = (self.vl.numbering.eu + self.cl.numbering.eu, self.vl.annotation.eu + self.cl.annotation.eu)
            self.lc.numbering.kabat, self.lc.annotation.kabat = (self.vl.numbering.kabat + self.cl.numbering.kabat, self.vl.annotation.kabat + self.cl.annotation.kabat)
            self.lc.numbering.martin, self.lc.annotation.martin = (self.vl.numbering.martin + self.cl.numbering.martin, self.vl.annotation.martin + self.cl.annotation.martin)
            self.lc.numbering.aho, self.lc.annotation.aho = (self.vl.numbering.aho + self.cl.numbering.aho, self.vl.annotation.aho + self.cl.annotation.aho)
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
                aa_sequence (str): Amino acid sequence of the light chain.
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
            Calculate the germline of the light chain.

            Args:
                aa_sequence (str): Amino acid sequence of the light chain.
            """
            aligner = SingleChainAnnotator(scheme='imgt')
            annotation = aligner.analyze_seq(aa_sequence)

            vj_tool = VJGeneTool(database='imgt', scheme='imgt')
            self.nearest_v_genes, self.nearest_j_genes, self.v_gene_percent_id, self.j_gene_percent_id = vj_tool.assign_vj_genes(annotation, aa_sequence, "human", "identity")
            self.nearest_v_genes = self.nearest_v_genes.split('_')
            self.nearest_j_genes = self.nearest_j_genes.split('_')
            self.v_gene_percent_id = self.v_gene_percent_id * 100
            self.j_gene_percent_id = self.j_gene_percent_id * 100

            scoring_tool = SequenceScoringTool(offer_classifier_option=False, normalization="none")
            humanness = scoring_tool.score_seqs(seq_list=[aa_sequence])
            self.humanness = float(humanness[0])
            self.chain_is_passable_as_human = True if humanness >= -100 else False
            return