def read_fasta(file_path):
    """Reads a FASTA file and returns a dictionary with headers, and sequences."""
    sequences = []
    with open(file_path, 'r') as f:
        header = None
        sequence = []
        for line in f:
            line = line.strip()
            if line.startswith('>'):
                if header is not None:
                    sequences.append((header, ''.join(sequence)))
                    header = None
                    sequence = []
                header = line[1:]  # Remove '>'
                header = header.split(' ')[0]
            else:
                sequence.append(line)
        if header is not None:  
            sequences.append((header, ''.join(sequence)))
    return sequences

def read_fasta_as_dict(file_path):
    """Reads a FASTA file and returns a dictionary with headers as keys and sequences as values."""
    fasta_dict = {}
    with open(file_path, 'r') as f:
        header = None
        sequence = []
        for line in f:
            line = line.strip()
            if line.startswith('>'):
                if header is not None:
                    fasta_dict[header] = ''.join(sequence)
                    header = None
                    sequence = []
                header = line[1:]
                header = header.split(' ')[0]
            else:
                sequence.append(line)
        if header is not None:  
            fasta_dict[header] = ''.join(sequence)
    return fasta_dict