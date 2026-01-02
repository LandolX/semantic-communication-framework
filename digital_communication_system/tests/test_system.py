#!/usr/bin/env python3
"""
Test script for the 5G Physical Layer Communication System.
"""

import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Now import the module
try:
    from 5g_phy_comm import run_simple_test, create_system
    print("Successfully imported 5g_phy_comm module!")
except ImportError as e:
    print(f"Error importing 5g_phy_comm module: {e}")
    sys.exit(1)


def test_simple_system():
    """Test the simple system (without OFDM)."""
    print("\n=== Testing Simple Communication System ===")
    result = run_simple_test(use_simple=True, modulation_type='qpsk', snr_dB=15, channel_type='awgn')
    return result


def test_full_system():
    """Test the full system (with OFDM)."""
    print("\n=== Testing Full Communication System with OFDM ===")
    result = run_simple_test(use_simple=False, modulation_type='qpsk', snr_dB=15, channel_type='awgn')
    return result


def test_different_modulations():
    """Test the system with different modulation types."""
    print("\n=== Testing Different Modulation Types ===")
    modulation_types = ['bpsk', 'qpsk', '16qam', '64qam']
    
    for mod_type in modulation_types:
        print(f"\nTesting {mod_type.upper()}...")
        result = run_simple_test(use_simple=True, modulation_type=mod_type, snr_dB=20, channel_type='awgn')
    
    return True


def test_different_channels():
    """Test the system with different channel types."""
    print("\n=== Testing Different Channel Types ===")
    channel_types = ['awgn', 'rayleigh', 'rician']
    
    for chan_type in channel_types:
        print(f"\nTesting {chan_type.upper()} channel...")
        result = run_simple_test(use_simple=True, modulation_type='qpsk', snr_dB=15, channel_type=chan_type)
    
    return True


def main():
    """Main test function."""
    print("5G Physical Layer Communication System Tests")
    print("=" * 50)
    
    # Run tests
    test_simple_system()
    test_full_system()
    test_different_modulations()
    test_different_channels()
    
    print("\n" + "=" * 50)
    print("All tests completed successfully!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
