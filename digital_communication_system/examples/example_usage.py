#!/usr/bin/env python3
"""
Example usage of the 5G Physical Layer Communication System.

This script demonstrates how to use the py5g_phy_comm package to create
and test a simple 5G physical layer communication system.
"""

import sys
import os
import numpy as np

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from py5g_phy_comm import create_system, run_simple_test


def example_basic_usage():
    """
    Basic usage example: Create a system and transmit data.
    """
    print("=== Basic Usage Example ===")
    
    # Create a simple communication system with QPSK modulation and AWGN channel
    system = create_system(
        use_simple=True,
        modulation_type='qpsk',
        snr_dB=15,
        channel_type='awgn'
    )
    
    # Test data to transmit
    test_data = b"Hello, 5G Physical Layer Communication System!"
    print(f"Transmitting: {test_data}")
    
    # Transmit and receive data
    received_data, ber = system.transmit_receive(test_data)
    
    # Print results
    print(f"Received:    {received_data}")
    print(f"BER:         {ber:.6f}")
    print(f"Match:       {test_data == received_data}")
    print()


def example_modulation_switching():
    """
    Example: Switch between different modulation types.
    """
    print("=== Modulation Switching Example ===")
    
    # Create a system
    system = create_system(use_simple=True, snr_dB=20, channel_type='awgn')
    
    # Test data
    test_data = b"Testing different modulation types."
    
    # Test with different modulation types
    modulation_types = ['bpsk', 'qpsk', '16qam', '64qam']
    
    for mod_type in modulation_types:
        print(f"\nUsing {mod_type.upper()}:")
        
        # Switch modulation type
        system.set_modulation_type(mod_type)
        
        # Transmit and receive
        received_data, ber = system.transmit_receive(test_data)
        
        print(f"  BER:   {ber:.6f}")
        print(f"  Match: {test_data == received_data}")
    print()


def example_channel_switching():
    """
    Example: Switch between different channel types.
    """
    print("=== Channel Switching Example ===")
    
    # Create a system
    system = create_system(use_simple=True, modulation_type='qpsk', snr_dB=25)
    
    # Test data
    test_data = b"Testing different channel types."
    
    # Test with different channel types
    channel_types = ['awgn', 'rayleigh', 'rician']
    
    for chan_type in channel_types:
        print(f"\nUsing {chan_type.upper()} channel:")
        
        # Switch channel type
        system.set_channel_type(chan_type)
        
        # Transmit and receive
        received_data, ber = system.transmit_receive(test_data)
        
        print(f"  BER:   {ber:.6f}")
        print(f"  Match: {test_data == received_data}")
    print()


def example_snr_impact():
    """
    Example: Show the impact of different SNR values.
    """
    print("=== SNR Impact Example ===")
    
    # Create a system
    system = create_system(use_simple=True, modulation_type='qpsk', channel_type='awgn')
    
    # Test data
    test_data = b"Testing SNR impact on communication."
    
    # Test with different SNR values
    snr_values = [0, 5, 10, 15, 20, 25]
    
    for snr in snr_values:
        print(f"\nUsing SNR = {snr} dB:")
        
        # Set SNR
        system.set_snr_dB(snr)
        
        # Transmit and receive
        received_data, ber = system.transmit_receive(test_data)
        
        print(f"  BER:   {ber:.6f}")
        print(f"  Match: {test_data == received_data}")
    print()


def example_advanced_config():
    """
    Example: Advanced configuration with OFDM.
    """
    print("=== Advanced Configuration Example ===")
    
    # Create a full OFDM system
    system = create_system(
        use_simple=False,          # Use full OFDM system
        modulation_type='qpsk',     # QPSK modulation
        snr_dB=15,                  # SNR = 15 dB
        channel_type='awgn',         # AWGN channel
        nfft=512,                   # FFT size = 512
        nsc=300,                    # 300 subcarriers
        cp_length=64                 # Cyclic prefix length = 64
    )
    
    # Test data
    test_data = b"Advanced OFDM configuration example with custom parameters."
    print(f"Transmitting with OFDM: {test_data}")
    
    # Transmit and receive
    received_data, ber = system.transmit_receive(test_data)
    
    print(f"Received: {received_data}")
    print(f"BER:      {ber:.6f}")
    print(f"Match:    {test_data == received_data}")
    print()


def example_random_data():
    """
    Example: Transmit random binary data.
    """
    print("=== Random Data Transmission Example ===")
    
    # Create a system
    system = create_system(use_simple=True, modulation_type='qpsk', snr_dB=15, channel_type='awgn')
    
    # Generate random data (100 bytes)
    random_data = np.random.randint(0, 256, 100, dtype=np.uint8).tobytes()
    print(f"Generated {len(random_data)} bytes of random data")
    print(f"First 50 bytes: {random_data[:50]}")
    
    # Transmit and receive
    received_data, ber = system.transmit_receive(random_data)
    
    print(f"Received data length: {len(received_data)} bytes")
    print(f"First 50 received bytes: {received_data[:50]}")
    print(f"BER: {ber:.6f}")
    print(f"Match: {random_data == received_data}")
    print()


def main():
    """
    Main example function.
    """
    print("5G Physical Layer Communication System - Example Usage")
    print("=" * 60)
    
    # Run all examples
    example_basic_usage()
    example_modulation_switching()
    example_channel_switching()
    example_snr_impact()
    example_advanced_config()
    example_random_data()
    
    print("=" * 60)
    print("All examples completed! You can modify this script to test different configurations.")


if __name__ == "__main__":
    main()
