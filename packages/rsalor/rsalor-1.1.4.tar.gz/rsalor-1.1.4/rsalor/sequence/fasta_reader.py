
# Imports ----------------------------------------------------------------------
import os.path
from typing import List, Union
import gzip
from rsalor.sequence import Sequence


# FastaReader ------------------------------------------------------------------ 
class FastaReader:
    """High level FASTA file reader."""

    @classmethod
    def read_first_sequence(cls, fasta_path: str) -> Sequence:
        """Read first sequence from a FASTA file."""
        fasta_stream = FastaStream(fasta_path)
        sequence = fasta_stream.get_next()
        fasta_stream.close()
        return sequence
    
    @classmethod
    def read_sequences(cls, fasta_path: str) -> List[Sequence]:
        """Read all sequences from a FASTA file."""
        fasta_stream = FastaStream(fasta_path)
        sequences = fasta_stream.get_all()
        fasta_stream.close()
        return sequences
    
    @classmethod
    def count_sequences(cls, fasta_path: str) -> int:
        """Count the number of sequences in a FASTA file (just count the '>')."""

        # Guardians
        assert os.path.isfile(fasta_path), f"ERROR in FastaReader.count_sequences(): fasta_path='{fasta_path}' does not exists."
        if not any([fasta_path.endswith(f".{ext}") for ext in FastaStream.ACCEPTED_EXTENTIONS]):
            raise ValueError(f"ERROR in FastaReader.count_sequences(): fasta_path='{fasta_path}' should end with {FastaStream.ACCEPTED_EXTENTIONS}.")

        # Count
        HEADER_START_CHAR = Sequence.HEADER_START_CHAR
        n = 0
        if fasta_path.endswith(".gz"):
            file = gzip.open(fasta_path, "rt") # gzip.open supports text mode ("rt") to read strings (not bytes)
        else:
            file = open(fasta_path, "r")
        line = file.readline()
        while line:
            if line.startswith(HEADER_START_CHAR):
                n += 1
            line = file.readline()
        return n


# FastaStream ------------------------------------------------------------------
class FastaStream:
    """Low level class to stream sequences from a FASTA file (one by one to avoid loading the whole file in RAM).
    
    WARNING: Please use with caution and do not forget to '.close()'.

    usage:
    
    fasta_stream = FastaStream('./fasta/msa1.fasta') \n
    sequence1 = fasta_stream.get_next() \n
    sequence2 = fasta_stream.get_next() \n
    fasta_stream.close()
    """

    # Constants ----------------------------------------------------------------
    ACCEPTED_EXTENTIONS = ["fasta", "a2m", "fasta.gz", "a2m.gz"]
    HEADER_START_CHAR = Sequence.HEADER_START_CHAR

    # Constructor --------------------------------------------------------------
    def __init__(self, fasta_path: str):

        # Guardians
        assert os.path.isfile(fasta_path), f"ERROR in FastaStream(): fasta_path='{fasta_path}' does not exists."
        if not any([fasta_path.endswith(f".{ext}") for ext in self.ACCEPTED_EXTENTIONS]):
            raise  ValueError(f"ERROR in FastaStream(): fasta_path='{fasta_path}' should end with {self.ACCEPTED_EXTENTIONS}.")

        # Init
        self.fasta_path = fasta_path
        if fasta_path.endswith(".gz"):
            self.file = gzip.open(fasta_path, "rt") # gzip.open supports text mode ("rt") to read strings (not bytes)
        else:
            self.file = open(fasta_path, "r")
        self.current_id = -1
        self.current_line = self._next_line()
        
        # First sequence sanity check
        assert self.current_line is not None, f"ERROR in FastaStream(): no sequences found in file '{fasta_path}'."
        assert self._is_current_line_header(), f"ERROR in FastaStream(): first line of file '{fasta_path}' sould be a fasta header (thus start with '{self.HEADER_START_CHAR}').\nline='{self.current_line}'"

    @property
    def is_open(self) -> bool:
        """Return if current file/stream is still open"""
        return self.current_line is not None

    # Methods ------------------------------------------------------------------
    def close(self) -> None:
        """Close file."""
        self.file.close()
        self.current_line = None

    def get_next(self) -> Union[None, Sequence]:
        """Get next Fasta sequence."""
        if self.current_line is None:
            return None
        self.current_id += 1
        header = self.current_line.removesuffix("\n")
        seq_arr = []
        self.current_line = self._next_line()
        while self.current_line:
            if self._is_current_line_header():
                break
            seq_arr.append(self.current_line.removesuffix("\n"))
            self.current_line = self._next_line()

        seq = "".join(seq_arr)
        return Sequence(header, seq)
    
    def get_all(self) -> List[Sequence]:
        """Get all remaining Fasta sequences."""
        fasta_sequence_list = []
        fasta_sequence = self.get_next()
        while fasta_sequence is not None:
            fasta_sequence_list.append(fasta_sequence)
            fasta_sequence = self.get_next()
        return fasta_sequence_list
    
    # Dependencies -------------------------------------------------------------
    def _next_line(self) -> Union[None, str]:
        line = self.file.readline()
        if line == "":
            self.close()
            return None
        return line
    
    def _is_current_line_header(self) -> bool:
        return self.current_line.startswith(Sequence.HEADER_START_CHAR)
