import struct


def read_binary_file(filename):
    """Reads a binary file and returns the bitstream as a string of '0's and '1's."""
    bitstream = ''
    with open(filename, 'rb') as file:
        byte = file.read(1)
        while byte:
            # Unpack the byte as a signed 8-bit integer
            value = struct.unpack('b', byte)[0]
            # Convert the signed integer to an 8-bit binary string
            bits = f'{value & 0xff:08b}'
            bitstream += bits
            byte = file.read(1)
    return bitstream


def read_pseudorandom_sequence(filename):
    """Reads the pseudorandom binary sequence from a text file."""
    with open(filename, 'r') as file:
        sequence = file.read().strip()
    return sequence


def calculate_ber(bitstream, pseudorandom_sequence, preamble):
    """Calculates the Bit Error Rate (BER) based on the pseudorandom sequence and preamble."""
    preamble_index = bitstream.find(preamble)
    if preamble_index == -1:
        raise ValueError("Preamble not found in the bitstream!")

    start_index = preamble_index + len(preamble)
    comparison_length = len(pseudorandom_sequence)
    bitstream_length = len(bitstream)
    if start_index + comparison_length > len(bitstream):
        raise ValueError("Bitstream does not contain enough data after the preamble to perform the test.")

    pseudorandom_sequence_no_preamble = pseudorandom_sequence[len(preamble):]
    bitstream_segment = bitstream[start_index:start_index + len(pseudorandom_sequence_no_preamble)]

    error_bits = sum(b1 != b2 for b1, b2 in zip(bitstream_segment, pseudorandom_sequence_no_preamble))
    ber = error_bits / comparison_length
    return ber


# File names
binary_file = 'backscatterdata_140824_-13dBm_filter8.bin'
pseudorandom_file = 'pseudorandombinarysequence.txt'
preamble = '10101010101010101010101010101010101010101010101010101010101010101010101010101010'

# Read files and calculate BER
bitstream = read_binary_file(binary_file)
pseudorandom_sequence = read_pseudorandom_sequence(pseudorandom_file)
ber = calculate_ber(bitstream, pseudorandom_sequence, preamble)

print(f"Bit Error Rate: {ber}")
