#!/usr/bin/env python3
"""
Basic example script demonstrating the 5G Physical Layer Communication System.

This script shows the basic usage of the py5g_phy_comm package, including:
1. Creating a communication system
2. Transmitting data
3. Receiving data
4. Calculating BER (Bit Error Rate)
5. Switching modulation types
6. Switching channel models
"""

# Add the current directory to Python path so we can import the package
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the create_system function from the py5g_phy_comm package
from py5g_phy_comm import create_system


def basic_example():
    """
    Basic example showing how to create a system and transmit data.
    """
    print("=== Basic Communication Example ===")
    
    # Step 1: Create a communication system
    # We're using the simplified version (no OFDM) with QPSK modulation and AWGN channel
    system = create_system(
        use_simple=True,        # Use simplified version (no OFDM)
        modulation_type='qpsk',  # Use QPSK modulation
        snr_dB=15,               # Set SNR to 15 dB
        channel_type='awgn'      # Use AWGN channel
    )
    
    # Step 2: Define the data to transmit
    # The system accepts binary bytes as input
    test_data = b"Hello, 5G Physical Layer!"
    print(f"Original data: {test_data}")
    
    # Step 3: Transmit and receive the data
    # The transmit_receive method returns the received data and Bit Error Rate (BER)
    received_data, ber = system.transmit_receive(test_data)
    
    # Step 4: Display the results
    print(f"Received data: {received_data}")
    print(f"Bit Error Rate: {ber:.6f}")
    print(f"Data correctly received: {test_data == received_data}")
    print()


def modulation_example():
    """
    Example showing how to switch between different modulation types.
    """
    print("=== Modulation Type Example ===")
    
    # Create a system with default parameters
    system = create_system(use_simple=True, snr_dB=20, channel_type='awgn')
    
    # Test data
    test_data = b"Testing modulation types"
    
    # List of modulation types to test
    modulation_types = ['bpsk', 'qpsk', '16qam', '64qam']
    
    for mod_type in modulation_types:
        # Switch to the current modulation type
        system.set_modulation_type(mod_type)
        
        # Transmit and receive
        received_data, ber = system.transmit_receive(test_data)
        
        # Display results
        print(f"{mod_type.upper()}:")
        print(f"  BER: {ber:.6f}")
        print(f"  Data match: {test_data == received_data}")
    print()


def channel_example():
    """
    Example showing how to switch between different channel models.
    """
    print("=== Channel Model Example ===")
    
    # Create a system with default parameters
    system = create_system(use_simple=True, modulation_type='qpsk', snr_dB=25)
    
    # Test data
    test_data = b"Testing channel models"
    
    # List of channel types to test
    channel_types = ['awgn', 'rayleigh', 'rician']
    
    for chan_type in channel_types:
        # Switch to the current channel type
        system.set_channel_type(chan_type)
        
        # Transmit and receive
        received_data, ber = system.transmit_receive(test_data)
        
        # Display results
        print(f"{chan_type.upper()} channel:")
        print(f"  BER: {ber:.6f}")
        print(f"  Data match: {test_data == received_data}")
    print()


def snr_example():
    """
    Example showing how to change SNR values.
    """
    print("=== SNR Variation Example ===")
    
    # Create a system with default parameters
    system = create_system(use_simple=True, modulation_type='qpsk', channel_type='awgn')
    
    # Test data
    test_data = b"Testing SNR values"
    
    # List of SNR values to test
    snr_values = [0, 5, 10, 15, 20]
    
    for snr in snr_values:
        # Set the current SNR value
        system.set_snr_dB(snr)
        
        # Transmit and receive
        received_data, ber = system.transmit_receive(test_data)
        
        # Display results
        print(f"SNR = {snr} dB:")
        print(f"  BER: {ber:.6f}")
        print(f"  Data match: {test_data == received_data}")
    print()


# Run all examples
if __name__ == "__main__":
    basic_example()
    modulation_example()
    channel_example()
    snr_example()
    print("=== Example Completed! ===")
    print("You can modify this script to test different configurations.")
