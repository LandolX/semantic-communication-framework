import matplotlib.pyplot as plt
import numpy as np


def plot_constellation(tx_symbols, rx_symbols, title=None):
    """
    Plot constellation diagrams for transmitted and received symbols.
    
    Parameters:
    -----------
    tx_symbols : 1D ndarray of complex floats
        Transmitted constellation symbols.
    
    rx_symbols : 1D ndarray of complex floats
        Received constellation symbols.
    
    title : str, optional
        Title for the plot.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    
    # Plot transmitted symbols
    ax1.scatter(tx_symbols.real, tx_symbols.imag, s=10, alpha=0.5, color='blue')
    ax1.set_title('Transmitted Constellation')
    ax1.set_xlabel('In-phase (I)')
    ax1.set_ylabel('Quadrature (Q)')
    ax1.grid(True)
    ax1.axis('equal')
    
    # Plot received symbols
    ax2.scatter(rx_symbols.real, rx_symbols.imag, s=10, alpha=0.5, color='red')
    ax2.set_title('Received Constellation')
    ax2.set_xlabel('In-phase (I)')
    ax2.set_ylabel('Quadrature (Q)')
    ax2.grid(True)
    ax2.axis('equal')
    
    if title:
        fig.suptitle(title, fontsize=14)
    
    plt.tight_layout()
    plt.show()


def plot_signal_waveform(tx_signal, rx_signal, title=None, num_samples=1000):
    """
    Plot the waveform of transmitted and received signals.
    
    Parameters:
    -----------
    tx_signal : 1D ndarray of complex floats
        Transmitted signal.
    
    rx_signal : 1D ndarray of complex floats
        Received signal.
    
    title : str, optional
        Title for the plot.
    
    num_samples : int, optional
        Number of samples to plot (default: 1000).
    """
    # Limit the number of samples for better visualization
    tx_signal = tx_signal[:num_samples]
    rx_signal = rx_signal[:num_samples]
    
    time = np.arange(len(tx_signal))
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # Plot transmitted signal
    ax1.plot(time, tx_signal.real, label='I (Real)', color='blue')
    ax1.plot(time, tx_signal.imag, label='Q (Imaginary)', color='red')
    ax1.set_title('Transmitted Signal Waveform')
    ax1.set_xlabel('Sample Index')
    ax1.set_ylabel('Amplitude')
    ax1.grid(True)
    ax1.legend()
    
    # Plot received signal
    ax2.plot(time, rx_signal.real, label='I (Real)', color='blue')
    ax2.plot(time, rx_signal.imag, label='Q (Imaginary)', color='red')
    ax2.set_title('Received Signal Waveform')
    ax2.set_xlabel('Sample Index')
    ax2.set_ylabel('Amplitude')
    ax2.grid(True)
    ax2.legend()
    
    if title:
        fig.suptitle(title, fontsize=14)
    
    plt.tight_layout()
    plt.show()


def plot_ber_curve(snr_values, ber_values, modulation_type, channel_type, title=None):
    """
    Plot the Bit Error Rate (BER) curve against SNR.
    
    Parameters:
    -----------
    snr_values : list of float
        SNR values in dB.
    
    ber_values : list of float
        BER values corresponding to each SNR.
    
    modulation_type : str
        Modulation type used.
    
    channel_type : str
        Channel type used.
    
    title : str, optional
        Title for the plot.
    """
    plt.figure(figsize=(10, 6))
    
    # Plot BER curve
    plt.semilogy(snr_values, ber_values, marker='o', linestyle='-', linewidth=2, markersize=8)
    
    plt.title(title if title else f'BER Curve - {modulation_type.upper()} over {channel_type.upper()}', fontsize=14)
    plt.xlabel('SNR (dB)', fontsize=12)
    plt.ylabel('Bit Error Rate (BER)', fontsize=12)
    plt.grid(True, which='both')
    plt.xlim(min(snr_values) - 1, max(snr_values) + 1)
    plt.ylim(1e-6, 1)
    
    # Add annotations for BER values
    for snr, ber in zip(snr_values, ber_values):
        plt.annotate(f'{ber:.2e}', (snr, ber), xytext=(5, 5), textcoords='offset points')
    
    plt.tight_layout()
    plt.show()


def plot_spectrum(signal, fs=1.0, title=None):
    """
    Plot the frequency spectrum of a signal.
    
    Parameters:
    -----------
    signal : 1D ndarray of complex floats
        Input signal.
    
    fs : float, optional
        Sampling frequency (default: 1.0).
    
    title : str, optional
        Title for the plot.
    """
    # Compute FFT
    n = len(signal)
    fft_output = np.fft.fft(signal)
    fft_output = np.fft.fftshift(fft_output)
    
    # Compute frequency axis
    freq = np.fft.fftfreq(n, 1/fs)
    freq = np.fft.fftshift(freq)
    
    # Compute magnitude spectrum in dB
    magnitude = np.abs(fft_output) / n
    magnitude_dB = 20 * np.log10(magnitude + 1e-10)  # Add small offset to avoid log(0)
    
    plt.figure(figsize=(10, 6))
    plt.plot(freq, magnitude_dB)
    plt.title(title if title else 'Signal Spectrum', fontsize=14)
    plt.xlabel('Frequency (Hz)', fontsize=12)
    plt.ylabel('Magnitude (dB)', fontsize=12)
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def plot_eye_diagram(signal, symbol_period, num_periods=10, title=None):
    """
    Plot an eye diagram for the given signal.
    
    Parameters:
    -----------
    signal : 1D ndarray of complex floats
        Input signal.
    
    symbol_period : int
        Number of samples per symbol.
    
    num_periods : int, optional
        Number of symbol periods to display (default: 10).
    
    title : str, optional
        Title for the plot.
    """
    # Extract real part for eye diagram
    real_signal = np.real(signal)
    
    # Calculate number of samples to display
    display_samples = symbol_period * num_periods
    
    # Create time axis for one symbol period
    time_axis = np.arange(symbol_period) / symbol_period
    
    plt.figure(figsize=(10, 6))
    
    # Plot multiple symbol periods
    for i in range(num_periods):
        start_idx = i * symbol_period
        end_idx = start_idx + symbol_period
        
        if end_idx > len(real_signal):
            break
        
        plt.plot(time_axis, real_signal[start_idx:end_idx], alpha=0.5)
    
    plt.title(title if title else 'Eye Diagram', fontsize=14)
    plt.xlabel('Symbol Period', fontsize=12)
    plt.ylabel('Amplitude', fontsize=12)
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def plot_scatter_comparison(tx_symbols, rx_symbols, title=None):
    """
    Plot a scatter comparison of transmitted and received symbols.
    
    Parameters:
    -----------
    tx_symbols : 1D ndarray of complex floats
        Transmitted constellation symbols.
    
    rx_symbols : 1D ndarray of complex floats
        Received constellation symbols.
    
    title : str, optional
        Title for the plot.
    """
    plt.figure(figsize=(8, 8))
    
    # Plot transmitted symbols as blue crosses
    plt.scatter(tx_symbols.real, tx_symbols.imag, s=50, marker='x', color='blue', label='Transmitted')
    
    # Plot received symbols as red dots
    plt.scatter(rx_symbols.real, rx_symbols.imag, s=20, marker='o', color='red', alpha=0.5, label='Received')
    
    plt.title(title if title else 'Transmitted vs Received Symbols', fontsize=14)
    plt.xlabel('In-phase (I)', fontsize=12)
    plt.ylabel('Quadrature (Q)', fontsize=12)
    plt.grid(True)
    plt.axis('equal')
    plt.legend()
    plt.tight_layout()
    plt.show()
