import numpy as np


def bitarray2bytes(bitarray):
    """
    Convert a binary array to bytes.
    
    Parameters:
    -----------
    bitarray : 1D ndarray of ints
        Binary array to convert.
    
    Returns:
    --------
    bytes_data : bytes
        Converted bytes.
    """
    # Ensure length is multiple of 8
    remainder = len(bitarray) % 8
    if remainder != 0:
        bitarray = np.pad(bitarray, (0, 8 - remainder), 'constant')
    
    # Reshape and convert to bytes
    return np.packbits(bitarray).tobytes()


def bytes2bitarray(bytes_data):
    """
    Convert bytes to a binary array.
    
    Parameters:
    -----------
    bytes_data : bytes
        Bytes to convert.
    
    Returns:
    --------
    bitarray : 1D ndarray of ints
        Converted binary array.
    """
    return np.unpackbits(np.frombuffer(bytes_data, dtype=np.uint8))


def calculate_ber(transmitted, received):
    """
    Calculate Bit Error Rate (BER) between two byte arrays.
    
    Parameters:
    -----------
    transmitted : bytes
        Original transmitted data.
    
    received : bytes
        Received and recovered data.
    
    Returns:
    --------
    ber : float
        Bit Error Rate.
    """
    # Ensure both data have the same length
    min_length = min(len(transmitted), len(received))
    transmitted = transmitted[:min_length]
    received = received[:min_length]
    
    # Convert to bit arrays
    tx_bits = np.unpackbits(np.frombuffer(transmitted, dtype=np.uint8))
    rx_bits = np.unpackbits(np.frombuffer(received, dtype=np.uint8))
    
    # Calculate bit errors
    num_errors = np.sum(tx_bits != rx_bits)
    total_bits = len(tx_bits)
    
    return num_errors / total_bits if total_bits > 0 else 0.0


def calculate_ser(transmitted_symbols, received_symbols):
    """
    Calculate Symbol Error Rate (SER) between two symbol arrays.
    
    Parameters:
    -----------
    transmitted_symbols : 1D ndarray of complex floats
        Transmitted constellation symbols.
    
    received_symbols : 1D ndarray of complex floats
        Received constellation symbols.
    
    Returns:
    --------
    ser : float
        Symbol Error Rate.
    """
    # Ensure both arrays have the same length
    min_length = min(len(transmitted_symbols), len(received_symbols))
    transmitted_symbols = transmitted_symbols[:min_length]
    received_symbols = received_symbols[:min_length]
    
    # Calculate symbol errors (using closest constellation points)
    # This is a simplified approach, assuming BPSK/QPSK-like constellations
    # For more accurate SER calculation, use the actual constellation mapping
    num_errors = np.sum(np.abs(transmitted_symbols - received_symbols) > 0.5)
    total_symbols = min_length
    
    return num_errors / total_symbols if total_symbols > 0 else 0.0


def generate_random_bits(length):
    """
    Generate random bits.
    
    Parameters:
    -----------
    length : int
        Number of bits to generate.
    
    Returns:
    --------
    bits : 1D ndarray of ints
        Generated random bits.
    """
    return np.random.randint(0, 2, length, dtype=int)


def generate_random_bytes(length):
    """
    Generate random bytes.
    
    Parameters:
    -----------
    length : int
        Number of bytes to generate.
    
    Returns:
    --------
    bytes_data : bytes
        Generated random bytes.
    """
    return np.random.randint(0, 256, length, dtype=np.uint8).tobytes()


def normalize_signal(signal, target_power=1.0):
    """
    Normalize a signal to a target power.
    
    Parameters:
    -----------
    signal : 1D ndarray of complex or float
        Input signal to normalize.
    
    target_power : float, optional
        Target power (default: 1.0).
    
    Returns:
    --------
    normalized_signal : 1D ndarray of complex or float
        Normalized signal.
    """
    current_power = np.mean(np.abs(signal) ** 2)
    scaling_factor = np.sqrt(target_power / current_power)
    return signal * scaling_factor


def add_awgn_noise(signal, snr_dB, signal_power=None):
    """
    Add AWGN noise to a signal with specified SNR in dB.
    
    Parameters:
    -----------
    signal : 1D ndarray of complex or float
        Input signal.
    
    snr_dB : float
        Signal-to-Noise Ratio in dB.
    
    signal_power : float, optional
        Power of the signal. If None, it will be calculated from the signal.
    
    Returns:
    --------
    noisy_signal : 1D ndarray of complex or float
        Signal with added noise.
    
    noise : 1D ndarray of complex or float
        Generated noise.
    """
    if signal_power is None:
        signal_power = np.mean(np.abs(signal) ** 2)
    
    # Calculate noise power
    snr_linear = 10 ** (snr_dB / 10)
    noise_power = signal_power / snr_linear
    noise_std = np.sqrt(noise_power)
    
    # Generate noise
    if isinstance(signal[0], complex):
        # Complex noise
        noise = (np.random.randn(len(signal)) + 1j * np.random.randn(len(signal))) * noise_std * np.sqrt(0.5)
    else:
        # Real noise
        noise = np.random.randn(len(signal)) * noise_std
    
    return signal + noise, noise


def calculate_power(signal):
    """
    Calculate the average power of a signal.
    
    Parameters:
    -----------
    signal : 1D ndarray of complex or float
        Input signal.
    
    Returns:
    --------
    power : float
        Average power of the signal.
    """
    return np.mean(np.abs(signal) ** 2)


def calculate_evm(transmitted_symbols, received_symbols):
    """
    Calculate Error Vector Magnitude (EVM) between transmitted and received symbols.
    
    Parameters:
    -----------
    transmitted_symbols : 1D ndarray of complex floats
        Transmitted constellation symbols.
    
    received_symbols : 1D ndarray of complex floats
        Received constellation symbols.
    
    Returns:
    --------
    evm : float
        Error Vector Magnitude in percentage.
    """
    # Calculate error vectors
    error_vectors = received_symbols - transmitted_symbols
    
    # Calculate EVM
    evm = np.sqrt(np.mean(np.abs(error_vectors) ** 2) / np.mean(np.abs(transmitted_symbols) ** 2)) * 100
    
    return evm


def hex_to_bytes(hex_string):
    """
    Convert a hex string to bytes.
    
    Parameters:
    -----------
    hex_string : str
        Hex string to convert.
    
    Returns:
    --------
    bytes_data : bytes
        Converted bytes.
    """
    return bytes.fromhex(hex_string)


def bytes_to_hex(bytes_data):
    """
    Convert bytes to a hex string.
    
    Parameters:
    -----------
    bytes_data : bytes
        Bytes to convert.
    
    Returns:
    --------
    hex_string : str
        Converted hex string.
    """
    return bytes_data.hex()


def get_modulation_order(modulation_type):
    """
    Get the modulation order (bits per symbol) for a given modulation type.
    
    Parameters:
    -----------
    modulation_type : str
        Modulation type.
    
    Returns:
    --------
    order : int
        Modulation order (bits per symbol).
    """
    modulation_orders = {
        'bpsk': 1,
        'pi/2-bpsk': 1,
        'qpsk': 2,
        '16qam': 4,
        '64qam': 6,
        '256qam': 8
    }
    
    return modulation_orders.get(modulation_type.lower(), 2)  # Default to QPSK
