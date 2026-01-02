import numpy as np
from .modulation import Modem, get_modem


class Receiver:
    """
    5G Physical Layer Receiver.
    
    This class implements the core functionality of a 5G physical layer receiver,
    including OFDM demodulation, demodulation, and data recovery.
    """
    
    def __init__(self, modulation_type='qpsk', nfft=1024, nsc=600, cp_length=144):
        """
        Initialize the receiver.
        
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
        self.rx_signal = None
        self.ofdm_symbols = None
        self.fft_output = None
        self.received_symbols = None
        self.demodulated_bits = None
        self.recovered_data = None
    
    def equalize(self, symbols, channel_gains):
        """
        Perform channel equalization on received symbols.
        
        Parameters:
        -----------
        symbols : 1D ndarray of complex floats
            Received symbols from the channel.
        
        channel_gains : 1D ndarray of complex floats
            Channel gains for each symbol.
        
        Returns:
        --------
        equalized_symbols : 1D ndarray of complex floats
            Equalized symbols.
        """
        if channel_gains is None or len(channel_gains) == 0:
            return symbols
        
        # Ensure channel_gains has the same length as symbols
        if len(channel_gains) != len(symbols):
            if len(channel_gains) == 1:
                channel_gains = np.full(len(symbols), channel_gains[0])
            else:
                print(f"Warning: Channel gains length ({len(channel_gains)}) does not match symbols length ({len(symbols)}). No equalization performed.")
                return symbols
        
        # Zero-forcing equalization: divide by channel gains
        # Avoid division by zero by adding a small epsilon
        epsilon = 1e-10
        equalized_symbols = symbols / (channel_gains + epsilon)
        
        return equalized_symbols
    
    def ofdm_demodulate(self, rx_signal):
        """
        Perform OFDM demodulation on the received signal.
        
        Parameters:
        -----------
        rx_signal : 1D ndarray of complex floats
            Received OFDM signal with cyclic prefix.
        
        Returns:
        --------
        symbols : 1D ndarray of complex floats
            Recovered constellation symbols from the subcarriers.
        """
        # Store received signal for debugging
        self.rx_signal = rx_signal
        
        # Calculate number of OFDM symbols
        symbol_length = self.nfft + self.cp_length
        num_ofdm_symbols = len(rx_signal) // symbol_length
        
        # Reshape signal into OFDM symbols
        rx_signal_reshaped = rx_signal[:num_ofdm_symbols * symbol_length].reshape(num_ofdm_symbols, symbol_length)
        
        # Remove cyclic prefix
        ofdm_symbols = rx_signal_reshaped[:, self.cp_length:]
        self.ofdm_symbols = ofdm_symbols
        
        # Perform FFT to get frequency domain signal
        fft_output = np.fft.fft(ofdm_symbols, axis=1)
        
        # Normalize FFT output
        fft_output *= np.sqrt(self.nsc / self.nfft)  # Scale to match transmitter
        self.fft_output = fft_output
        
        # Extract subcarriers (avoid DC subcarrier)
        # Get symbols from lower and upper subcarriers, skipping DC
        symbols_lower = fft_output[:, -(self.nsc // 2):]
        symbols_upper = fft_output[:, 1:(self.nsc // 2) + 1]
        symbols_matrix = np.concatenate((symbols_lower, symbols_upper), axis=1)
        
        # Flatten to get the recovered symbols
        symbols = symbols_matrix.flatten()
        self.received_symbols = symbols
        
        return symbols
    
    def demodulate(self, symbols, demod_type='hard', noise_var=0):
        """
        Demodulate constellation symbols to bits.
        
        Parameters:
        -----------
        symbols : 1D ndarray of complex floats
            Received constellation symbols.
        
        demod_type : str, optional
            Demodulation type: 'hard' or 'soft' (default: 'hard').
        
        noise_var : float, optional
            Noise variance for soft demodulation (default: 0).
        
        Returns:
        --------
        bits : 1D ndarray of ints or floats
            Demodulated bits (hard decision) or LLRs (soft decision).
        """
        # Demodulate symbols to bits
        bits = self.modem.demodulate(symbols, demod_type, noise_var)
        self.demodulated_bits = bits
        
        return bits
    
    def recover_data(self, bits, original_length=None):
        """
        Recover data from demodulated bits.
        
        Parameters:
        -----------
        bits : 1D ndarray of ints
            Demodulated bits.
        
        original_length : int, optional
            Original length of the data in bytes. If provided, the recovered data
            will be truncated to this length (default: None).
        
        Returns:
        --------
        data : bytes
            Recovered data.
        """
        # Convert bits to bytes
        num_bytes = len(bits) // 8
        bytes_array = np.packbits(bits[:num_bytes * 8]).tobytes()
        
        # Truncate to original length if provided
        if original_length is not None:
            bytes_array = bytes_array[:original_length]
        
        self.recovered_data = bytes_array
        
        return bytes_array
    
    def receive(self, rx_signal, original_length=None, demod_type='hard', noise_var=0, channel_gains=None):
        """
        Complete reception process from received signal to recovered data.
        
        Parameters:
        -----------
        rx_signal : 1D ndarray of complex floats
            Received signal from the channel.
        
        original_length : int, optional
            Original length of the data in bytes. If provided, the recovered data
            will be truncated to this length (default: None).
        
        demod_type : str, optional
            Demodulation type: 'hard' or 'soft' (default: 'hard').
        
        noise_var : float, optional
            Noise variance for soft demodulation (default: 0).
        
        channel_gains : 1D ndarray of complex floats, optional
            Channel gains for equalization (default: None).
        
        Returns:
        --------
        data : bytes
            Recovered data.
        """
        # Step 1: OFDM demodulation
        symbols = self.ofdm_demodulate(rx_signal)
        
        # Step 2: Channel equalization if channel gains are provided
        if channel_gains is not None:
            symbols = self.equalize(symbols, channel_gains)
        
        # Step 3: Demodulate symbols to bits
        bits = self.demodulate(symbols, demod_type, noise_var)
        
        # Step 4: Recover data from bits
        data = self.recover_data(bits, original_length)
        
        return data
    
    def get_debug_info(self):
        """
        Get debugging information about the reception process.
        
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
            'rx_signal': self.rx_signal,
            'ofdm_symbols': self.ofdm_symbols,
            'fft_output': self.fft_output,
            'received_symbols': self.received_symbols,
            'demodulated_bits': self.demodulated_bits,
            'recovered_data': self.recovered_data,
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


class SimpleReceiver:
    """
    Simplified 5G Physical Layer Receiver for testing and debugging.
    
    This version skips OFDM demodulation for simpler testing.
    """
    
    def __init__(self, modulation_type='qpsk'):
        """
        Initialize the simple receiver.
        
        Parameters:
        -----------
        modulation_type : str, optional
            Modulation type to use (default: 'qpsk').
        """
        self.modulation_type = modulation_type
        self.modem = get_modem(modulation_type)
        
        # Store intermediate signals for debugging
        self.received_symbols = None
        self.demodulated_bits = None
        self.recovered_data = None
    
    def equalize(self, symbols, channel_gains):
        """
        Perform channel equalization on received symbols.
        
        Parameters:
        -----------
        symbols : 1D ndarray of complex floats
            Received symbols from the channel.
        
        channel_gains : 1D ndarray of complex floats
            Channel gains for each symbol.
        
        Returns:
        --------
        equalized_symbols : 1D ndarray of complex floats
            Equalized symbols.
        """
        if channel_gains is None or len(channel_gains) == 0:
            return symbols
        
        # Ensure channel_gains has the same length as symbols
        if len(channel_gains) != len(symbols):
            if len(channel_gains) == 1:
                channel_gains = np.full(len(symbols), channel_gains[0])
            else:
                print(f"Warning: Channel gains length ({len(channel_gains)}) does not match symbols length ({len(symbols)}). No equalization performed.")
                return symbols
        
        # Zero-forcing equalization: divide by channel gains
        # Avoid division by zero by adding a small epsilon
        epsilon = 1e-10
        equalized_symbols = symbols / (channel_gains + epsilon)
        
        return equalized_symbols
    
    def receive(self, symbols, original_length=None, demod_type='hard', noise_var=0, channel_gains=None):
        """
        Simplified reception process: symbols -> equalization -> demodulation -> bytes.
        
        Parameters:
        -----------
        symbols : 1D ndarray of complex floats
            Received symbols from the channel.
        
        original_length : int, optional
            Original length of the data in bytes. If provided, the recovered data
            will be truncated to this length (default: None).
        
        demod_type : str, optional
            Demodulation type: 'hard' or 'soft' (default: 'hard').
        
        noise_var : float, optional
            Noise variance for soft demodulation (default: 0).
        
        channel_gains : 1D ndarray of complex floats, optional
            Channel gains for equalization (default: None).
        
        Returns:
        --------
        data : bytes
            Recovered data.
        """
        self.received_symbols = symbols
        
        # Perform channel equalization if channel gains are provided
        if channel_gains is not None:
            symbols = self.equalize(symbols, channel_gains)
        
        # Demodulate symbols to bits
        bits = self.modem.demodulate(symbols, demod_type, noise_var)
        self.demodulated_bits = bits
        
        # Convert bits to bytes
        num_bytes = len(bits) // 8
        bytes_array = np.packbits(bits[:num_bytes * 8]).tobytes()
        
        # Truncate to original length if provided
        if original_length is not None:
            bytes_array = bytes_array[:original_length]
        
        self.recovered_data = bytes_array
        
        return bytes_array
    
    def get_debug_info(self):
        """
        Get debugging information about the reception process.
        
        Returns:
        --------
        debug_info : dict
            Dictionary containing intermediate signals and parameters.
        """
        return {
            'modulation_type': self.modulation_type,
            'received_symbols': self.received_symbols,
            'demodulated_bits': self.demodulated_bits,
            'recovered_data': self.recovered_data,
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
