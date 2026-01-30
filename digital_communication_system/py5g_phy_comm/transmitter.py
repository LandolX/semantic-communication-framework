import numpy as np
from .modulation import Modem, get_modem


class Transmitter:
    """
    5G Physical Layer Transmitter.
    
    This class implements the core functionality of a 5G physical layer transmitter,
    including data processing, modulation, and OFDM modulation.
    """
    
    def __init__(self, modulation_type='qpsk', nfft=1024, nsc=600, cp_length=144):
        """
        Initialize the transmitter.
        
        Parameters:
        -----------
        modulation_type : str, optional
            Modulation type to use (default: 'qpsk').
        
        nfft : int, optional
            FFT size for OFDM (default: 1024).
        
        nsc : int, optional
            Number of subcarriers to use (default: 600).
        
        cp_length : int, optional
            Cyclic prefix length (default: 144).
        """
        self.modulation_type = modulation_type
        self.nfft = nfft
        self.nsc = nsc
        self.cp_length = cp_length
        
        # Initialize modem
        self.modem = get_modem(modulation_type)
        
        # Store intermediate signals for debugging
        self.input_bits = None
        self.modulated_symbols = None
        self.ifft_output = None
        self.ofdm_symbols = None
        self.tx_signal = None
        
    def process_data(self, input_data):
        """
        Process input data (bytes) into bits for transmission.
        
        Parameters:
        -----------
        input_data : bytes
            Input data to transmit.
        
        Returns:
        --------
        bits : 1D ndarray of ints
            Processed bits ready for modulation.
        """
        # Convert bytes to bits and ensure they are integers (not uint8)
        bits = np.unpackbits(np.frombuffer(input_data, dtype=np.uint8)).astype(int)
        
        # Store for debugging
        self.input_bits = bits
        
        return bits
    
    def modulate(self, bits):
        """
        Modulate bits to constellation symbols.
        
        Parameters:
        -----------
        bits : 1D ndarray of ints
            Bits to modulate.
        
        Returns:
        --------
        symbols : 1D ndarray of complex floats
            Modulated constellation symbols.
        """
        # Ensure bits length is multiple of bits per symbol
        remainder = len(bits) % self.modem.bits_per_symbol
        if remainder != 0:
            # Pad with zeros if needed
            bits = np.pad(bits, (0, self.modem.bits_per_symbol - remainder), 'constant')
        
        # Modulate bits to symbols
        symbols = self.modem.modulate(bits)
        
        # Store for debugging
        self.modulated_symbols = symbols
        
        return symbols
    
    def ofdm_modulate(self, symbols):
        """
        Perform OFDM modulation on the symbols.
        
        Parameters:
        -----------
        symbols : 1D ndarray of complex floats
            Modulated symbols to map to OFDM subcarriers.
        
        Returns:
        --------
        tx_signal : 1D ndarray of complex floats
            Transmitted OFDM signal with cyclic prefix.
        """
        # Calculate number of OFDM symbols needed
        num_ofdm_symbols = int(np.ceil(len(symbols) / self.nsc))
        
        # Pad symbols if needed
        padded_symbols = np.pad(symbols, (0, num_ofdm_symbols * self.nsc - len(symbols)), 'constant')
        
        # Reshape symbols into OFDM symbols
        symbols_matrix = padded_symbols.reshape(num_ofdm_symbols, self.nsc)
        
        # Initialize OFDM symbols in frequency domain
        ofdm_sym_freq = np.zeros((num_ofdm_symbols, self.nfft), dtype=complex)
        
        # Map symbols to subcarriers (avoid DC subcarrier)
        # Place symbols in the lower and upper subcarriers, skipping DC
        ofdm_sym_freq[:, 1:(self.nsc // 2) + 1] = symbols_matrix[:, self.nsc // 2:]
        ofdm_sym_freq[:, -(self.nsc // 2):] = symbols_matrix[:, :self.nsc // 2]
        
        # Perform IFFT to get time domain signal
        ifft_output = np.fft.ifft(ofdm_sym_freq, axis=1)
        
        # Normalize IFFT output
        ifft_output *= np.sqrt(self.nfft / self.nsc)  # Scale for unit power per subcarrier
        
        # Add cyclic prefix
        cp = ifft_output[:, -self.cp_length:]
        ofdm_symbols = np.concatenate((cp, ifft_output), axis=1)
        
        # Flatten to get the final transmit signal
        tx_signal = ofdm_symbols.flatten()
        
        # Store intermediate signals for debugging
        self.ifft_output = ifft_output
        self.ofdm_symbols = ofdm_symbols
        self.tx_signal = tx_signal
        
        return tx_signal
    
    def transmit(self, input_data):
        """
        Complete transmission process from input data to OFDM signal.
        
        Parameters:
        -----------
        input_data : bytes
            Input data to transmit.
        
        Returns:
        --------
        tx_signal : 1D ndarray of complex floats
            Transmitted OFDM signal.
        """
        # Step 1: Process input data into bits
        bits = self.process_data(input_data)
        
        # Step 2: Modulate bits to symbols
        symbols = self.modulate(bits)
        
        # Step 3: Perform OFDM modulation
        tx_signal = self.ofdm_modulate(symbols)
        
        return tx_signal
    
    def get_debug_info(self):
        """
        Get debugging information about the transmission process.
        
        Returns:
        --------
        debug_info : dict
            Dictionary containing intermediate signals and parameters.
        """
        return {
            'modulation_type': self.modulation_type,
            'nfft': self.nfft,
            'nsc': self.nsc,
            'cp_length': self.cp_length,
            'input_bits': self.input_bits,
            'modulated_symbols': self.modulated_symbols,
            'ifft_output': self.ifft_output,
            'ofdm_symbols': self.ofdm_symbols,
            'tx_signal': self.tx_signal,
            'bits_per_symbol': self.modem.bits_per_symbol
        }
    
    def set_modulation_type(self, modulation_type):
        """
        Set the modulation type.
        
        Parameters:
        -----------
        modulation_type : str
            New modulation type to use.
        """
        self.modulation_type = modulation_type
        self.modem = get_modem(modulation_type)
    
    def set_ofdm_parameters(self, nfft=None, nsc=None, cp_length=None):
        """
        Set OFDM parameters.
        
        Parameters:
        -----------
        nfft : int, optional
            New FFT size.
        
        nsc : int, optional
            New number of subcarriers.
        
        cp_length : int, optional
            New cyclic prefix length.
        """
        if nfft is not None:
            self.nfft = nfft
        if nsc is not None:
            self.nsc = nsc
        if cp_length is not None:
            self.cp_length = cp_length


class SimpleTransmitter:
    """
    Simplified 5G Physical Layer Transmitter for testing and debugging.
    
    This version skips OFDM modulation for simpler testing.
    """
    
    def __init__(self, modulation_type='qpsk'):
        """
        Initialize the simple transmitter.
        
        Parameters:
        -----------
        modulation_type : str, optional
            Modulation type to use (default: 'qpsk').
        """
        self.modulation_type = modulation_type
        self.modem = get_modem(modulation_type)
        
        # Store intermediate signals for debugging
        self.input_bits = None
        self.modulated_symbols = None
    
    def transmit(self, input_data):
        """
        Simplified transmission process: bytes -> bits -> modulation.
        
        Parameters:
        -----------
        input_data : bytes
            Input data to transmit.
        
        Returns:
        --------
        symbols : 1D ndarray of complex floats
            Modulated symbols ready for channel propagation.
        """
        # Convert bytes to bits and ensure they are integers (not uint8)
        bits = np.unpackbits(np.frombuffer(input_data, dtype=np.uint8)).astype(int)
        self.input_bits = bits
        
        # Ensure bits length is multiple of bits per symbol
        remainder = len(bits) % self.modem.bits_per_symbol
        if remainder != 0:
            bits = np.pad(bits, (0, self.modem.bits_per_symbol - remainder), 'constant')
        
        # Modulate bits to symbols
        symbols = self.modem.modulate(bits)
        self.modulated_symbols = symbols
        
        return symbols
    
    def get_debug_info(self):
        """
        Get debugging information about the transmission process.
        
        Returns:
        --------
        debug_info : dict
            Dictionary containing intermediate signals and parameters.
        """
        return {
            'modulation_type': self.modulation_type,
            'input_bits': self.input_bits,
            'modulated_symbols': self.modulated_symbols,
            'bits_per_symbol': self.modem.bits_per_symbol
        }
    
    def set_modulation_type(self, modulation_type):
        """
        Set the modulation type.
        
        Parameters:
        -----------
        modulation_type : str
            New modulation type to use.
        """
        self.modulation_type = modulation_type
        self.modem = get_modem(modulation_type)
