import numpy as np
from antpack import SingleChainAnnotator
from .properties import ProteinProperties
import mAbLab.fc_constants as Fc
import mAbLab.hc_annotator as HCAnnotator
import mAbLab.common_methods as cm


class HeavyChain:
    """
    A class to represent a heavy chain (HC) of an antibody.

    Attributes:
        input_aa (str): Input amino acid sequence.
        germlines (AnnotateHC._InferGermline): Germline inference results.
        isotype (str): Isotype of the antibody.
        allotype (str): Allotype of the antibody.
        subclass (str): Subclass of the antibody.
        full_chain (_DomainObj): Full heavy chain domain object.
        vh (_DomainObj): Variable heavy chain domain object.
        ch1 (_DomainObj): CH1 domain object.
        ch2 (_DomainObj): CH2 domain object.
        ch3 (_DomainObj): CH3 domain object.
        cdr1 (_CdrObj): CDR1 object.
        cdr2 (_CdrObj): CDR2 object.
        cdr3 (_CdrObj): CDR3 object.
        hinge (_DomainObj): Hinge domain object.
        fc (_DomainObj): Fc domain object.
        fd (_DomainObj): Fd domain object.
        fc_mutations (AnnotateHC._HC._MutationObj): Fc mutations.
        hinge_is_modified (bool): Whether the hinge is modified.
    """

    def __init__(self, aa_sequence: str = None) -> None:
        """
        Initialize the HeavyChain object with an amino acid sequence.

        Args:
            aa_sequence (str): Amino acid sequence of the heavy chain.
        """
        self.input_aa = self._validate_input(aa_sequence)
        self._annotation = HCAnnotator.AnnotateHC(self.input_aa)
        self.germlines = self._annotation.germlines
        self.isotype = self._annotation.analysis_results.isotype
        self.allotype = self._annotation.analysis_results.allotype
        self.subclass = self._annotation.analysis_results.subclass
        self.full_chain = self._DomainObj(self._annotation.analysis_results.hc)
        self.vh = self._DomainObj(self._annotation.analysis_results.vh)
        self.ch1 = self._DomainObj(self._annotation.analysis_results.ch1)
        self.ch2 = self._DomainObj(self._annotation.analysis_results.ch2)
        self.ch3 = self._DomainObj(self._annotation.analysis_results.ch3)
        self.cdr1 = self._CdrObj(self._annotation.analysis_results.cdr1)
        self.cdr2 = self._CdrObj(self._annotation.analysis_results.cdr2)
        self.cdr3 = self._CdrObj(self._annotation.analysis_results.cdr3)
        self.hinge = self._DomainObj(self._annotation.analysis_results.hinge)
        self.fc = self._DomainObj(self._annotation.analysis_results.fc)
        self.fd = self._DomainObj(self._annotation.analysis_results.fd)
        self.fc_mutations = self._annotation.analysis_results.fc_mutations
        self.hinge_is_modified = self._annotation.analysis_results.hinge_is_modified

    def _validate_input(self, aa_seq: str = None) -> str:
        """
        Validate the input amino acid sequence.

        Args:
            aa_seq (str): Amino acid sequence.

        Returns:
            str: Validated amino acid sequence.

        Raises:
            ValueError: If invalid amino acids are detected or the sequence is not a heavy chain.
        """
        def _char_check(aa_seq: str) -> bool:
            all_aa = ['A', 'R', 'N', 'D', 'C', 'Q', 'E', 'G', 'H', 'I', 'L', 'K', 'M', 'F', 'P', 'S', 'T', 'V', 'W', 'Y', 'X']
            invalid_aa = [aa for aa in aa_seq if aa not in all_aa]
            if invalid_aa:
                raise ValueError(f"Invalid amino acid codes detected! Identified errors: {list(set(invalid_aa))}")
            return True

        def _is_heavy_chain(aa_seq: str) -> bool:
            aligner = SingleChainAnnotator(scheme='martin')
            annotation = aligner.analyze_seq(aa_seq)
            _, _, chain, errors = annotation
            if chain.upper() != 'H':
                raise ValueError(f"Provided amino acid sequence is not a heavy chain! Errors: {errors}")
            return True

        aa_seq = aa_seq.upper()
        if _char_check(aa_seq) and _is_heavy_chain(aa_seq):
            return aa_seq
        return False

    class _DomainObj:
        """
        A class to represent a domain object.

        Attributes:
            sequence (str): Sequence of the domain.
            numbering (_NumberingSystemObj): Numbering system object.
            annotation (_NumberingSystemObj): Annotation system object.
            properties (ProteinProperties): Protein properties of the domain.
        """

        def __init__(self, annotated_obj) -> None:
            """
            Initialize the _DomainObj object.

            Args:
                annotated_obj: Annotated object containing sequence, numbering, and annotation.
            """
            self.sequence = str
            self.numbering = self._NumberingSystemObj()
            self.annotation = self._NumberingSystemObj()
            self._set_values(annotated_obj)
            self.properties = ProteinProperties(self.sequence) if self.sequence and len(self.sequence) > 1 else None

        def _set_values(self, annotated_obj) -> None:
            """
            Set values for the domain object.

            Args:
                annotated_obj: Annotated object containing sequence, numbering, and annotation.
            """
            self.sequence = annotated_obj.sequence if annotated_obj.sequence and len(annotated_obj.sequence) > 1 else None
            self.numbering = annotated_obj.numbering
            self.annotation = annotated_obj.annotation

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
                self.imgt = None
                self.eu = None
                self.kabat = None
                self.martin = None
                self.aho = None

    class _CdrObj:
        """
        A class to represent a CDR object.

        Attributes:
            numbering (_NumberingSystemObj): Numbering system object.
            annotation (_NumberingSystemObj): Annotation system object.
            sequence (_NumberingSystemObj): Sequence system object.
            properties (_CDRSchemeObj): CDR scheme object.
        """

        def __init__(self, annotated_obj) -> None:
            """
            Initialize the _CdrObj object.

            Args:
                annotated_obj: Annotated object containing sequence, numbering, and annotation.
            """
            self.numbering = self._NumberingSystemObj()
            self.annotation = self._NumberingSystemObj()
            self.sequence = self._NumberingSystemObj()
            self._set_values(annotated_obj)
            self.properties = self._CDRSchemeObj(self.sequence)

        def _set_values(self, annotated_obj) -> None:
            """
            Set values for the CDR object.

            Args:
                annotated_obj: Annotated object containing sequence, numbering, and annotation.
            """
            self.sequence = annotated_obj.sequence
            self.numbering = annotated_obj.numbering
            self.annotation = annotated_obj.annotation

        class _CDRSchemeObj:
            """
            A class to represent a CDR scheme object.

            Attributes:
                imgt (ProteinProperties): IMGT CDR scheme properties.
                eu (ProteinProperties): EU CDR scheme properties.
                kabat (ProteinProperties): Kabat CDR scheme properties.
                martin (ProteinProperties): Martin CDR scheme properties.
                aho (ProteinProperties): AHO CDR scheme properties.
            """

            def __init__(self, sequence) -> None:
                """
                Initialize the _CDRSchemeObj object.

                Args:
                    sequence: Sequence object containing CDR schemes.
                """
                self.imgt = ProteinProperties(sequence.imgt) if sequence.imgt and len(sequence.imgt) > 1 else None
                self.eu = ProteinProperties(sequence.eu) if sequence.eu and len(sequence.eu) > 1 else None
                self.kabat = ProteinProperties(sequence.kabat) if sequence.kabat and len(sequence.kabat) > 1 else None
                self.martin = ProteinProperties(sequence.martin) if sequence.martin and len(sequence.martin) > 1 else None
                self.aho = ProteinProperties(sequence.aho) if sequence.aho and len(sequence.aho) > 1 else None

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
                self.imgt = None
                self.eu = None
                self.kabat = None
                self.martin = None
                self.aho = None

    def to_dict(self):
        def serialize(obj, seen=None):
            if seen is None:
                seen = set()
            obj_id = id(obj)
            if obj_id in seen:
                return None
            seen.add(obj_id)
            if obj is None:
                return None
            if isinstance(obj, (str, int, float, bool)):
                return obj
            if isinstance(obj, list):
                return [serialize(i, seen) for i in obj]
            if isinstance(obj, dict):
                return {k: serialize(v, seen) for k, v in obj.items()}
            # For annotation/numbering objects, serialize __dict__ directly (do not call to_dict)
            if hasattr(obj, "__dict__"):
                d = {}
                for k, v in obj.__dict__.items():
                    if not k.startswith("_"):
                        # If v is a list and not None, keep as is
                        if isinstance(v, list) and v is not None:
                            # If the list is all None, but the original attribute is not None, use the original attribute
                            orig = getattr(obj, k, None)
                            if isinstance(orig, list) and any(x is not None for x in orig):
                                d[k] = orig
                            else:
                                d[k] = v
                        else:
                            d[k] = serialize(v, seen)
                return d
            return str(obj)
        return serialize(self)
