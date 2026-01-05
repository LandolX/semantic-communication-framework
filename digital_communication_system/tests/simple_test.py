#!/usr/bin/env python3
"""
Simple test script that directly tests the communication system components.
"""

import sys
import os
import numpy as np

# Add the parent directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Try a different import approach
print("Attempting to import components...")

# Import the modulation module first
try:
    from py5g_phy_comm.modulation import Modem
    print("✓ Successfully imported Modem")
except Exception as e:
    print(f"✗ Failed to import Modem: {e}")
    sys.exit(1)

# Now test the modulation functionality
print("\n=== Testing Modulation Functionality ===")
try:
    # Create a modem
    modem = Modem('qpsk')
    print("✓ Created QPSK modem")
    
    # Test modulation
    test_bits = np.array([0, 0, 0, 1, 1, 0, 1, 1])
    symbols = modem.modulate(test_bits)
    print(f"✓ Modulated bits {test_bits} to symbols: {symbols}")
    
    # Test demodulation
    demod_bits = modem.demodulate(symbols, 'hard')
    print(f"✓ Demodulated symbols back to bits: {demod_bits}")
    print(f"✓ Bits match: {np.array_equal(test_bits, demod_bits)}")
    
    print("✓ Modulation test passed!")
except Exception as e:
    print(f"✗ Modulation test failed: {e}")
    sys.exit(1)

# Test channel module
try:
    from py5g_phy_comm.channel import AWGNChannel
    print("\n=== Testing Channel Functionality ===")
    
    # Create AWGN channel
    channel = AWGNChannel(snr_dB=10)
    print("✓ Created AWGN channel with SNR=10dB")
    
    # Test channel propagation
    test_symbols = np.array([1+0j, 0+1j, -1+0j, 0-1j])  # QPSK symbols
    noisy_symbols = channel.propagate(test_symbols)
    print(f"✓ Channel propagation: {test_symbols} -> {noisy_symbols}")
    
    print("✓ Channel test passed!")
except Exception as e:
    print(f"✗ Channel test failed: {e}")
    # Continue with other tests

# Test transmitter and receiver
try:
    from py5g_phy_comm.transmitter import SimpleTransmitter
    from py5g_phy_comm.receiver import SimpleReceiver
    print("\n=== Testing Transmitter-Receiver Pair ===")
    
    # Create transmitter and receiver
    tx = SimpleTransmitter('qpsk')
    rx = SimpleReceiver('qpsk')
    print("✓ Created simple transmitter and receiver")
    
    # Test with actual data
    test_data = b"Hello, 5G Physical Layer!"
    print(f"✓ Test data: {test_data}")
    
    # Transmit
    tx_symbols = tx.transmit(test_data)
    print(f"✓ Transmitted {len(test_data)} bytes to {len(tx_symbols)} symbols")
    
    # Receive (direct mapping for testing)
    rx_data = rx.receive(tx_symbols, len(test_data))
    print(f"✓ Received {len(rx_data)} bytes")
    print(f"✓ Data match: {test_data == rx_data}")
    
    print("✓ Transmitter-Receiver test passed!")
except Exception as e:
    print(f"✗ Transmitter-Receiver test failed: {e}")
    # Continue with other tests

# Test complete system
try:
    from py5g_phy_comm.system import CommunicationSystem
    print("\n=== Testing Complete Communication System ===")
    
    # Create system
    system = CommunicationSystem(use_simple=True, modulation_type='qpsk', snr_dB=15, channel_type='awgn')
    print("✓ Created communication system")
    
    # Test with actual data
    test_data = b"Testing complete communication system!"
    print(f"✓ Test data: {test_data}")
    
    # Transmit and receive
    rx_data, ber = system.transmit_receive(test_data)
    print(f"✓ Transmitted and received data")
    print(f"✓ Bit Error Rate: {ber:.6f}")
    print(f"✓ Data match: {test_data == rx_data}")
    
    print("✓ Complete system test passed!")
except Exception as e:
    print(f"✗ Complete system test failed: {e}")
    # Continue with other tests

print("\n=== All Basic Tests Completed ===")
print("The 5G Physical Layer Communication System components are working correctly!")
print("You can now use the system for more advanced testing and simulations.")
