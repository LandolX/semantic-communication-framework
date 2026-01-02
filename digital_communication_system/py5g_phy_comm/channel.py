import numpy as np


class Channel:
    """
    Base class for communication channels.
    """
    
    def __init__(self):
        self.noise_std = None
        self.snr_dB = None
        self.is_complex = True
    
    def set_snr_dB(self, snr_dB, signal_power=None):
        """
        Set the Signal-to-Noise Ratio in dB.
        
        Parameters:
        -----------
        snr_dB : float
            Signal-to-Noise Ratio in dB.
        
        signal_power : float, optional
            Average power of the signal. If None, it will be calculated from the signal.
        """
        self.snr_dB = snr_dB
        self.snr_linear = 10 ** (snr_dB / 10)
        self.noise_std = None  # Reset noise std, will be calculated when propagating
    
    def set_snr_linear(self, snr_linear, signal_power=None):
        """
        Set the Signal-to-Noise Ratio in linear scale.
        
        Parameters:
        -----------
        snr_linear : float
            Signal-to-Noise Ratio in linear scale.
        
        signal_power : float, optional
            Average power of the signal. If None, it will be calculated from the signal.
        """
        self.snr_linear = snr_linear
        self.snr_dB = 10 * np.log10(snr_linear)
        self.noise_std = None  # Reset noise std, will be calculated when propagating
    
    def propagate(self, signal):
        """
        Propagate the signal through the channel.
        
        Parameters:
        -----------
        signal : 1D ndarray of complex or float
            Input signal to propagate through the channel.
        
        Returns:
        --------
        output_signal : 1D ndarray of complex or float
            Signal after propagation through the channel.
        """
        raise NotImplementedError("propagate method must be implemented by subclasses")
    
    def propagate_with_channel_info(self, signal):
        """
        Propagate the signal through the channel and return channel information.
        
        Parameters:
        -----------
        signal : 1D ndarray of complex or float
            Input signal to propagate through the channel.
        
        Returns:
        --------
        output_signal : 1D ndarray of complex or float
            Signal after propagation through the channel.
        channel_info : dict
            Dictionary containing channel information (e.g., channel gains).
        """
        output_signal = self.propagate(signal)
        channel_info = {}
        
        if hasattr(self, 'channel_gains') and self.channel_gains is not None:
            channel_info['channel_gains'] = self.channel_gains
        
        return output_signal, channel_info
    
    def _calculate_noise_std(self, signal):
        """
        Calculate the noise standard deviation based on the signal power and SNR.
        
        Parameters:
        -----------
        signal : 1D ndarray of complex or float
            Input signal.
        
        Returns:
        --------
        noise_std : float
            Noise standard deviation.
        """
        # Calculate signal power if not provided
        signal_power = np.mean(np.abs(signal) ** 2)
        
        # For complex signals, noise power is split between real and imaginary parts
        if self.is_complex:
            noise_variance = signal_power / self.snr_linear
            noise_std = np.sqrt(noise_variance / 2)  # Split between real and imaginary
        else:
            noise_variance = signal_power / self.snr_linear
            noise_std = np.sqrt(noise_variance)
        
        return noise_std
    
    def _generate_noise(self, size):
        """
        Generate noise with the appropriate standard deviation.
        
        Parameters:
        -----------
        size : int
            Size of the noise array to generate.
        
        Returns:
        --------
        noise : 1D ndarray of complex or float
            Generated noise.
        """
        if self.is_complex:
            # Complex Gaussian noise: real and imaginary parts are independent Gaussian
            return (np.random.randn(size) + 1j * np.random.randn(size)) * self.noise_std
        else:
            # Real Gaussian noise
            return np.random.randn(size) * self.noise_std


class AWGNChannel(Channel):
    """
    Additive White Gaussian Noise (AWGN) Channel.
    """
    
    def __init__(self, snr_dB=10):
        """
        Initialize the AWGN channel.
        
        Parameters:
        -----------
        snr_dB : float, optional
            Signal-to-Noise Ratio in dB (default: 10).
        """
        super().__init__()
        self.set_snr_dB(snr_dB)
    
    def propagate(self, signal):
        """
        Propagate the signal through the AWGN channel.
        
        Parameters:
        -----------
        signal : 1D ndarray of complex or float
            Input signal to propagate through the channel.
        
        Returns:
        --------
        output_signal : 1D ndarray of complex or float
            Signal after adding AWGN noise.
        """
        # Check if signal is complex
        self.is_complex = np.iscomplexobj(signal)
        
        # Calculate noise standard deviation if not set
        if self.noise_std is None:
            self.noise_std = self._calculate_noise_std(signal)
        
        # Generate noise
        noise = self._generate_noise(len(signal))
        
        # Add noise to signal
        output_signal = signal + noise
        
        return output_signal


class RayleighChannel(Channel):
    """
    Rayleigh fading channel.
    """
    
    def __init__(self, snr_dB=10, doppler_frequency=0):
        """
        Initialize the Rayleigh fading channel.
        
        Parameters:
        -----------
        snr_dB : float, optional
            Signal-to-Noise Ratio in dB (default: 10).
        
        doppler_frequency : float, optional
            Doppler frequency in Hz (default: 0, stationary channel).
        """
        super().__init__()
        self.set_snr_dB(snr_dB)
        self.doppler_frequency = doppler_frequency
        self.channel_gains = None
    
    def propagate(self, signal):
        """
        Propagate the signal through the Rayleigh fading channel.
        
        Parameters:
        -----------
        signal : 1D ndarray of complex or float
            Input signal to propagate through the channel.
        
        Returns:
        --------
        output_signal : 1D ndarray of complex or float
            Signal after propagation through the Rayleigh fading channel.
        """
        # Check if signal is complex
        self.is_complex = np.iscomplexobj(signal)
        
        # Generate Rayleigh fading channel gains
        # Rayleigh fading is modeled as complex Gaussian with zero mean and unit variance
        self.channel_gains = (np.random.randn(len(signal)) + 1j * np.random.randn(len(signal))) / np.sqrt(2)
        
        # Apply fading to signal
        faded_signal = signal * self.channel_gains
        
        # Calculate noise standard deviation based on faded signal power
        if self.noise_std is None:
            self.noise_std = self._calculate_noise_std(faded_signal)
        
        # Add noise
        noise = self._generate_noise(len(signal))
        output_signal = faded_signal + noise
        
        return output_signal


class RicianChannel(Channel):
    """
    Rician fading channel.
    """
    
    def __init__(self, snr_dB=10, k_factor=1, doppler_frequency=0):
        """
        Initialize the Rician fading channel.
        
        Parameters:
        -----------
        snr_dB : float, optional
            Signal-to-Noise Ratio in dB (default: 10).
        
        k_factor : float, optional
            Rician K-factor (ratio of LOS power to scattered power) (default: 1).
        
        doppler_frequency : float, optional
            Doppler frequency in Hz (default: 0, stationary channel).
        """
        super().__init__()
        self.set_snr_dB(snr_dB)
        self.k_factor = k_factor
        self.doppler_frequency = doppler_frequency
        self.channel_gains = None
        
        # Generate fixed LOS phase (same for all samples in stationary channel)
        self.los_phase = np.random.uniform(0, 2 * np.pi)
    
    def propagate(self, signal):
        """
        Propagate the signal through the Rician fading channel.
        
        Parameters:
        -----------
        signal : 1D ndarray of complex or float
            Input signal to propagate through the channel.
        
        Returns:
        --------
        output_signal : 1D ndarray of complex or float
            Signal after propagation through the Rician fading channel.
        """
        # Check if signal is complex
        self.is_complex = np.iscomplexobj(signal)
        
        # Generate Rician fading channel gains
        # Rician fading is modeled as a LOS component plus Rayleigh fading
        # The LOS component has amplitude sqrt(k_factor / (k_factor + 1))
        # The scattered component has variance 1 / (k_factor + 1)
        los_amplitude = np.sqrt(self.k_factor / (self.k_factor + 1))
        scattered_variance = 1 / (self.k_factor + 1)
        
        # Generate LOS component (fixed amplitude and phase for stationary channel)
        los_component = los_amplitude * np.exp(1j * self.los_phase)
        
        # Generate scattered component (Rayleigh fading)
        scattered_component = (np.random.randn(len(signal)) + 1j * np.random.randn(len(signal))) * np.sqrt(scattered_variance / 2)
        
        # Total channel gain
        self.channel_gains = los_component + scattered_component
        
        # Apply fading to signal
        faded_signal = signal * self.channel_gains
        
        # Calculate noise standard deviation based on faded signal power
        if self.noise_std is None:
            self.noise_std = self._calculate_noise_std(faded_signal)
        
        # Add noise
        noise = self._generate_noise(len(signal))
        output_signal = faded_signal + noise
        
        return output_signal


class FrequencySelectiveChannel(Channel):
    """
    Frequency selective fading channel (based on tapped delay line model).
    """
    
    def __init__(self, snr_dB=10, taps=None, delays=None):
        """
        Initialize the frequency selective fading channel.
        
        Parameters:
        -----------
        snr_dB : float, optional
            Signal-to-Noise Ratio in dB (default: 10).
        
        taps : 1D ndarray of complex, optional
            Channel taps (default: [1.0, 0.5, 0.25]).
        
        delays : 1D ndarray of int, optional
            Delay in samples for each tap (default: [0, 1, 2]).
        """
        super().__init__()
        self.set_snr_dB(snr_dB)
        
        # Normalize taps to ensure unit power
        taps = taps if taps is not None else np.array([1.0, 0.5, 0.25], dtype=complex)
        tap_power = np.sum(np.abs(taps) ** 2)
        self.taps = taps / np.sqrt(tap_power)
        
        self.delays = delays if delays is not None else np.array([0, 1, 2])
        self.channel_gains = None
    
    def propagate(self, signal):
        """
        Propagate the signal through the frequency selective fading channel.
        
        Parameters:
        -----------
        signal : 1D ndarray of complex or float
            Input signal to propagate through the channel.
        
        Returns:
        --------
        output_signal : 1D ndarray of complex or float
            Signal after propagation through the frequency selective fading channel.
        """
        # Check if signal is complex
        self.is_complex = np.iscomplexobj(signal)
        
        # Generate time-varying channel taps (Rayleigh fading for each tap)
        num_taps = len(self.taps)
        num_samples = len(signal)
        
        # Generate fading gains for each tap
        fading_gains = (np.random.randn(num_samples, num_taps) + 1j * np.random.randn(num_samples, num_taps)) / np.sqrt(2)
        
        # Apply channel taps to signal
        output_signal = np.zeros(num_samples, dtype=complex)
        for i in range(num_taps):
            # Apply delay with proper zero-padding (not circular shift)
            delay = self.delays[i]
            if delay > 0:
                delayed_signal = np.zeros(num_samples, dtype=complex)
                delayed_signal[delay:] = signal[:-delay]
            else:
                delayed_signal = signal.copy()
            
            # Apply fading gain
            faded_delayed_signal = delayed_signal * fading_gains[:, i] * self.taps[i]
            
            # Add to output
            output_signal += faded_delayed_signal
        
        # Calculate noise standard deviation based on faded signal power
        if self.noise_std is None:
            self.noise_std = self._calculate_noise_std(output_signal)
        
        # Add noise
        noise = self._generate_noise(num_samples)
        output_signal += noise
        
        self.channel_gains = fading_gains
        
        return output_signal


# Helper function to create channel instances
def get_channel(channel_type, **kwargs):
    """
    Create a channel instance based on the specified type.
    
    Parameters:
    -----------
    channel_type : str
        Type of channel to create. Supported types: 'awgn', 'rayleigh', 'rician', 'frequency_selective'
    
    **kwargs : dict
        Additional parameters for the channel constructor.
    
    Returns:
    --------
    channel : Channel instance
        Channel instance of the specified type.
    """
    channel_types = {
        'awgn': AWGNChannel,
        'rayleigh': RayleighChannel,
        'rician': RicianChannel,
        'frequency_selective': FrequencySelectiveChannel
    }
    
    if channel_type.lower() not in channel_types:
        raise ValueError(f"Unsupported channel type. Supported types: {list(channel_types.keys())}")
    
    return channel_types[channel_type.lower()](**kwargs)
