import numpy as np
from .transmitter import Transmitter, SimpleTransmitter
from .receiver import Receiver, SimpleReceiver
from .channel import get_channel
from .visualization import plot_constellation, plot_signal_waveform, plot_ber_curve


class CommunicationSystem:
    """
    Complete 5G Physical Layer Communication System.
    
    This class integrates the transmitter, channel, and receiver into a complete
    communication system, providing a simple API for configuration and operation.
    """
    
    def __init__(self, use_simple=False, **kwargs):
        """
        Initialize the communication system.
        
        Parameters:
        -----------
        use_simple : bool, optional
            Whether to use simplified transmitter/receiver (no OFDM) for testing (default: False).
        
        **kwargs : dict
            Additional parameters for the system components.
            Common parameters:
            - modulation_type: str, modulation type (default: 'qpsk')
            - snr_dB: float, Signal-to-Noise Ratio in dB (default: 10)
            - channel_type: str, channel type (default: 'awgn')
            - nfft: int, FFT size for OFDM (default: 1024)
            - nsc: int, number of subcarriers (default: 600)
            - cp_length: int, cyclic prefix length (default: 144)
        """
        self.use_simple = use_simple
        
        # Extract parameters from kwargs
        modulation_type = kwargs.get('modulation_type', 'qpsk')
        snr_dB = kwargs.get('snr_dB', 10)
        channel_type = kwargs.get('channel_type', 'awgn')
        nfft = kwargs.get('nfft', 1024)
        nsc = kwargs.get('nsc', 600)
        cp_length = kwargs.get('cp_length', 144)
        
        # Initialize system components
        if use_simple:
            self.transmitter = SimpleTransmitter(modulation_type)
            self.receiver = SimpleReceiver(modulation_type)
        else:
            self.transmitter = Transmitter(modulation_type, nfft, nsc, cp_length)
            self.receiver = Receiver(modulation_type, nfft, nsc, cp_length)
        
        self.channel = get_channel(channel_type, snr_dB=snr_dB)
        
        # Store system parameters
        self.modulation_type = modulation_type
        self.snr_dB = snr_dB
        self.channel_type = channel_type
        self.nfft = nfft
        self.nsc = nsc
        self.cp_length = cp_length
        
        # Store results for debugging and visualization
        self.tx_signal = None
        self.channel_output = None
        self.rx_signal = None
        self.transmitted_data = None
        self.received_data = None
        self.error_rate = None
    
    def set_modulation_type(self, modulation_type):
        """
        Set the modulation type for both transmitter and receiver.
        
        Parameters:
        -----------
        modulation_type : str
            Modulation type to use.
        """
        self.modulation_type = modulation_type
        self.transmitter.set_modulation_type(modulation_type)
        self.receiver.set_modulation_type(modulation_type)
    
    def set_snr_dB(self, snr_dB):
        """
        Set the Signal-to-Noise Ratio in dB for the channel.
        
        Parameters:
        -----------
        snr_dB : float
            Signal-to-Noise Ratio in dB.
        """
        self.snr_dB = snr_dB
        self.channel.set_snr_dB(snr_dB)
    
    def set_channel_type(self, channel_type, **channel_params):
        """
        Set the channel type.
        
        Parameters:
        -----------
        channel_type : str
            Channel type to use.
        
        **channel_params : dict
            Additional parameters for the channel.
        """
        self.channel_type = channel_type
        # Preserve SNR setting
        channel_params['snr_dB'] = channel_params.get('snr_dB', self.snr_dB)
        self.channel = get_channel(channel_type, **channel_params)
    
    def transmit_receive(self, input_data):
        """
        Complete transmit-receive process through the communication system.
        
        Parameters:
        -----------
        input_data : bytes
            Input data to transmit.
        
        Returns:
        --------
        received_data : bytes
            Received and recovered data.
        
        error_rate : float
            Bit Error Rate (BER) of the transmission.
        """
        self.transmitted_data = input_data
        
        # Step 1: Transmit data
        tx_signal = self.transmitter.transmit(input_data)
        self.tx_signal = tx_signal
        
        # Step 2: Propagate through channel and get channel information
        channel_output, channel_info = self.channel.propagate_with_channel_info(tx_signal)
        self.channel_output = channel_output
        
        # Step 3: Receive and recover data with channel equalization
        original_length = len(input_data)
        channel_gains = channel_info.get('channel_gains', None)
        received_data = self.receiver.receive(channel_output, original_length, channel_gains=channel_gains)
        self.received_data = received_data
        
        # Calculate error rate
        error_rate = self._calculate_error_rate(input_data, received_data)
        self.error_rate = error_rate
        
        return received_data, error_rate
    
    def _calculate_error_rate(self, transmitted, received):
        """
        Calculate the Bit Error Rate (BER) between transmitted and received data.
        
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
        
        # Calculate bit errors
        transmitted_bits = np.unpackbits(np.frombuffer(transmitted, dtype=np.uint8))
        received_bits = np.unpackbits(np.frombuffer(received, dtype=np.uint8))
        
        num_errors = np.sum(transmitted_bits != received_bits)
        total_bits = len(transmitted_bits)
        
        return num_errors / total_bits if total_bits > 0 else 0.0
    
    def get_debug_info(self):
        """
        Get debugging information from all system components.
        
        Returns:
        --------
        debug_info : dict
            Dictionary containing debugging information from all components.
        """
        debug_info = {
            'system_params': {
                'modulation_type': self.modulation_type,
                'snr_dB': self.snr_dB,
                'channel_type': self.channel_type,
                'use_simple': self.use_simple,
                'nfft': self.nfft,
                'nsc': self.nsc,
                'cp_length': self.cp_length
            },
            'transmitter': self.transmitter.get_debug_info(),
            'channel': {
                'channel_type': self.channel_type,
                'snr_dB': self.snr_dB,
                'noise_std': getattr(self.channel, 'noise_std', None),
                'channel_gains': getattr(self.channel, 'channel_gains', None)
            },
            'receiver': self.receiver.get_debug_info(),
            'results': {
                'transmitted_data': self.transmitted_data,
                'received_data': self.received_data,
                'error_rate': self.error_rate
            }
        }
        
        return debug_info
    
    def visualize_constellation(self, title=None):
        """
        Visualize the constellation diagram of the transmitted and received symbols.
        
        Parameters:
        -----------
        title : str, optional
            Title for the plot.
        """
        if self.use_simple:
            tx_symbols = self.transmitter.modulated_symbols
            rx_symbols = self.receiver.received_symbols
        else:
            tx_symbols = self.transmitter.modulated_symbols
            rx_symbols = self.receiver.received_symbols
        
        if tx_symbols is not None and rx_symbols is not None:
            plot_constellation(tx_symbols, rx_symbols, title)
        else:
            print("No symbols available for visualization. Run transmit_receive first.")
    
    def visualize_signal(self, title=None):
        """
        Visualize the transmitted and received signal waveforms.
        
        Parameters:
        -----------
        title : str, optional
            Title for the plot.
        """
        if self.tx_signal is not None and self.rx_signal is not None:
            plot_signal_waveform(self.tx_signal, self.rx_signal, title)
        else:
            print("No signals available for visualization. Run transmit_receive first.")
    
    def run_ber_simulation(self, data_length=1000, snr_range=None, num_trials=5):
        """
        Run a BER simulation over a range of SNR values.
        
        Parameters:
        -----------
        data_length : int, optional
            Length of data to transmit per trial (default: 1000 bytes).
        
        snr_range : list of float, optional
            Range of SNR values to test (default: 0 to 20 dB in 2 dB steps).
        
        num_trials : int, optional
            Number of trials per SNR value (default: 5).
        
        Returns:
        --------
        snr_values : list of float
            SNR values tested.
        
        ber_values : list of float
            BER values corresponding to each SNR.
        """
        if snr_range is None:
            snr_range = np.arange(0, 21, 2)
        
        ber_values = []
        
        for snr in snr_range:
            print(f"Testing SNR: {snr} dB")
            self.set_snr_dB(snr)
            
            total_ber = 0.0
            for trial in range(num_trials):
                # Generate random data
                input_data = np.random.randint(0, 256, data_length, dtype=np.uint8).tobytes()
                
                # Transmit and receive
                _, ber = self.transmit_receive(input_data)
                total_ber += ber
            
            # Calculate average BER for this SNR
            avg_ber = total_ber / num_trials
            ber_values.append(avg_ber)
            print(f"  Average BER: {avg_ber:.6f}")
        
        # Plot BER curve
        plot_ber_curve(snr_range, ber_values, self.modulation_type, self.channel_type)
        
        return snr_range, ber_values
    
    def reset(self):
        """
        Reset the system components and results.
        """
        # Reinitialize components with current parameters
        if self.use_simple:
            self.transmitter = SimpleTransmitter(self.modulation_type)
            self.receiver = SimpleReceiver(self.modulation_type)
        else:
            self.transmitter = Transmitter(self.modulation_type, self.nfft, self.nsc, self.cp_length)
            self.receiver = Receiver(self.modulation_type, self.nfft, self.nsc, self.cp_length)
        
        self.channel = get_channel(self.channel_type, snr_dB=self.snr_dB)
        
        # Reset results
        self.tx_signal = None
        self.channel_output = None
        self.rx_signal = None
        self.transmitted_data = None
        self.received_data = None
        self.error_rate = None


# Simple API for quick testing
def create_system(use_simple=False, **kwargs):
    """
    Create a communication system instance with the specified parameters.
    
    Parameters:
    -----------
    use_simple : bool, optional
        Whether to use simplified transmitter/receiver (default: False).
    
    **kwargs : dict
        Additional parameters for the system components.
    
    Returns:
    --------
    system : CommunicationSystem
        Communication system instance.
    """
    return CommunicationSystem(use_simple, **kwargs)


def run_simple_test(input_data=None, use_simple=False, **kwargs):
    """
    Run a simple test of the communication system.
    
    Parameters:
    -----------
    input_data : bytes, optional
        Input data to transmit (default: random 100 bytes).
    
    use_simple : bool, optional
        Whether to use simplified transmitter/receiver (default: False).
    
    **kwargs : dict
        Additional parameters for the system.
    
    Returns:
    --------
    result : dict
        Test results including transmitted data, received data, and error rate.
    """
    # Generate random input data if not provided
    if input_data is None:
        input_data = np.random.randint(0, 256, 100, dtype=np.uint8).tobytes()
    
    # Create and configure system
    system = CommunicationSystem(use_simple, **kwargs)
    
    # Run transmit-receive
    received_data, error_rate = system.transmit_receive(input_data)
    
    # Print results
    print("=== Communication System Test Results ===")
    print(f"Modulation: {system.modulation_type}")
    print(f"Channel: {system.channel_type}")
    print(f"SNR: {system.snr_dB} dB")
    print(f"Input data length: {len(input_data)} bytes")
    print(f"Received data length: {len(received_data)} bytes")
    print(f"Bit Error Rate: {error_rate:.6f}")
    print(f"Transmitted: {input_data[:20]}...")
    print(f"Received:    {received_data[:20]}...")
    print(f"Match: {input_data == received_data}")
    print("========================================")
    
    return {
        'transmitted_data': input_data,
        'received_data': received_data,
        'error_rate': error_rate,
        'system': system
    }
