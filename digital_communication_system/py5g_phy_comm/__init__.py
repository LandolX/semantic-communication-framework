"""
5G Physical Layer Communication System

This package implements a complete 5G physical layer communication system,
including modulation/demodulation, channel modeling, and OFDM transmission.
"""

__version__ = "0.1.0"
__author__ = "5G Phy Comm Team"

# Import core classes and functions
from .modulation import Modem, get_modem
from .channel import Channel, AWGNChannel, RayleighChannel, RicianChannel, FrequencySelectiveChannel, get_channel
from .transmitter import Transmitter, SimpleTransmitter
from .receiver import Receiver, SimpleReceiver
from .system import CommunicationSystem, create_system, run_simple_test
from .visualization import (
    plot_constellation,
    plot_signal_waveform,
    plot_ber_curve,
    plot_spectrum,
    plot_eye_diagram,
    plot_scatter_comparison
)
from .utils import (
    bitarray2bytes,
    bytes2bitarray,
    calculate_ber,
    calculate_ser,
    generate_random_bits,
    generate_random_bytes,
    normalize_signal,
    add_awgn_noise,
    calculate_power,
    calculate_evm,
    hex_to_bytes,
    bytes_to_hex,
    get_modulation_order
)

# Define __all__ to control what gets imported with "from 5g_phy_comm import *"
__all__ = [
    # Modulation
    'Modem',
    'get_modem',
    
    # Channel
    'Channel',
    'AWGNChannel',
    'RayleighChannel',
    'RicianChannel',
    'FrequencySelectiveChannel',
    'get_channel',
    
    # Transmitter
    'Transmitter',
    'SimpleTransmitter',
    
    # Receiver
    'Receiver',
    'SimpleReceiver',
    
    # System
    'CommunicationSystem',
    'create_system',
    'run_simple_test',
    
    # Visualization
    'plot_constellation',
    'plot_signal_waveform',
    'plot_ber_curve',
    'plot_spectrum',
    'plot_eye_diagram',
    'plot_scatter_comparison',
    
    # Utils
    'bitarray2bytes',
    'bytes2bitarray',
    'calculate_ber',
    'calculate_ser',
    'generate_random_bits',
    'generate_random_bytes',
    'normalize_signal',
    'add_awgn_noise',
    'calculate_power',
    'calculate_evm',
    'hex_to_bytes',
    'bytes_to_hex',
    'get_modulation_order'
]
