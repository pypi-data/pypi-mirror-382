
class Sequence:

    def __init__(self, sequence, id=None, description=None):
        self.sequence = sequence
        self.id = id
        self.description = description
        self.length = len(sequence)

    
    def __str__(self):
        if self.id:
            return f">{self.id} {self.description}\n{self.sequence}"

    def __len__(self):
        return self.length

    def dna_complement(self):
        """Obtain reverse complement for data augmentation purpose."""
        complement_dict = {
            "A":"T", 
            "T":"A", 
            "C":"G",
            "G":"C", 
            # Unclassical IUPAC codes :
            "N":"N",
            "M":"K",
            "K":"M",
            "R":"Y",
            "Y":"R",
            "W":"S",
            "S":"W",
            "H":"D",
            "D":"H",
            "V":"B",
            "B":"V"
        }
        complement = list(map(complement_dict.get, self.sequence))
        complement.reverse()
        return ''.join(complement)


    def generate_kmers(self, k=1000, leap=100):
        """Generate kmers from sequence. 
        Args : 
            k (int): kmer size
            leap (int): size between to kmers
        Returns: 
            Lits[str]: list of the corresponding k-mers
        """
        return [self.sequence[i:i+k] for i in range(0, len(self.sequence)-k+1, leap)]
