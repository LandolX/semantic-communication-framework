import numpy as np
from sympy.combinatorics.graycode import GrayCode


def bitarray2dec(bitarray):
    """Convert a binary array to a decimal number."""
    return int(''.join(map(str, bitarray)), 2)


def dec2bitarray(decimal, length):
    """Convert a decimal number to a binary array of given length."""
    return [int(bit) for bit in np.binary_repr(decimal, length)]


def signal_power(signal):
    """Calculate the average power of a signal."""
    return np.mean(np.abs(signal) ** 2)


class Modem:
    """
    Base class for modems supporting 5G modulation types.
    """
    
    def __init__(self, modulation_type):
        """
        Initialize the modem with a specific modulation type.
        
        Parameters:
        -----------
        modulation_type : str
            Modulation type to use. Supported types: 'pi/2-bpsk', 'bpsk', 'qpsk', '16qam', '64qam', '256qam'
        """
        self.modulation_type = modulation_type.lower()
        self._validate_modulation_type()
        self._setup_modulation_params()
    
    def _validate_modulation_type(self):
        """Validate the modulation type."""
        supported_types = ['pi/2-bpsk', 'bpsk', 'qpsk', '16qam', '64qam', '256qam']
        if self.modulation_type not in supported_types:
            raise ValueError(f"Unsupported modulation type. Supported types: {supported_types}")
    
    def _setup_modulation_params(self):
        """Setup modulation parameters based on modulation type."""
        mod_params = {
            'pi/2-bpsk': {'bits_per_symbol': 1, 'normalization': np.sqrt(2)},
            'bpsk': {'bits_per_symbol': 1, 'normalization': np.sqrt(2)},
            'qpsk': {'bits_per_symbol': 2, 'normalization': np.sqrt(2)},
            '16qam': {'bits_per_symbol': 4, 'normalization': np.sqrt(10)},
            '64qam': {'bits_per_symbol': 6, 'normalization': np.sqrt(42)},
            '256qam': {'bits_per_symbol': 8, 'normalization': np.sqrt(170)}
        }
        
        self.bits_per_symbol = mod_params[self.modulation_type]['bits_per_symbol']
        self.normalization = mod_params[self.modulation_type]['normalization']
    
    def modulate(self, input_bits):
        """
        Modulate (map) an array of bits to constellation symbols.
        
        Parameters:
        -----------
        input_bits : 1D ndarray of ints
            Input bits to be modulated (mapped).
        
        Returns:
        --------
        symbols : 1D ndarray of complex floats
            Modulated complex symbols.
        """
        if len(input_bits) % self.bits_per_symbol != 0:
            raise ValueError(f"Input bits length must be multiple of {self.bits_per_symbol}")
        
        num_symbols = len(input_bits) // self.bits_per_symbol
        symbols = np.zeros(num_symbols, dtype=complex)
        
        # Reshape bits into symbols
        bit_chunks = input_bits.reshape(num_symbols, self.bits_per_symbol)
        
        for i, bits in enumerate(bit_chunks):
            symbols[i] = self._map_bits_to_symbol(bits)
        
        return symbols
    
    def _map_bits_to_symbol(self, bits):
        """
        Map a single chunk of bits to a constellation symbol.
        
        Parameters:
        -----------
        bits : 1D ndarray of ints
            Bits for a single symbol.
        
        Returns:
        --------
        symbol : complex float
            Constellation symbol.
        """
        if self.modulation_type == 'bpsk':
            # BPSK modulation
            real = 1 - 2 * bits[0]
            imag = 0
            symbol = complex(real, imag)
        
        elif self.modulation_type == 'pi/2-bpsk':
            # pi/2-BPSK modulation (rotated BPSK)
            if np.random.rand() > 0.5:
                real = 1 - 2 * bits[0]
                imag = 0
            else:
                real = 0
                imag = 1 - 2 * bits[0]
            symbol = complex(real, imag)
        
        elif self.modulation_type == 'qpsk':
            # QPSK modulation
            real = 1 - 2 * bits[0]
            imag = 1 - 2 * bits[1]
            symbol = complex(real, imag)
        
        elif self.modulation_type == '16qam':
            # 16-QAM modulation
            a = 1 - 2 * bits[0]
            b = 1 - 2 * bits[1]
            c = 1 - 2 * bits[2]
            d = 1 - 2 * bits[3]
            
            real = a * (2 - c)
            imag = b * (2 - d)
            symbol = complex(real, imag)
        
        elif self.modulation_type == '64qam':
            # 64-QAM modulation
            a = 1 - 2 * bits[0]
            b = 1 - 2 * bits[1]
            c = 1 - 2 * bits[2]
            d = 1 - 2 * bits[3]
            e = 1 - 2 * bits[4]
            f = 1 - 2 * bits[5]
            
            real = a * (4 - c * (2 - e))
            imag = b * (4 - d * (2 - f))
            symbol = complex(real, imag)
        
        elif self.modulation_type == '256qam':
            # 256-QAM modulation
            a = 1 - 2 * bits[0]
            b = 1 - 2 * bits[1]
            c = 1 - 2 * bits[2]
            d = 1 - 2 * bits[3]
            e = 1 - 2 * bits[4]
            f = 1 - 2 * bits[5]
            g = 1 - 2 * bits[6]
            h = 1 - 2 * bits[7]
            
            real = a * (8 - c * (4 - e * (2 - g)))
            imag = b * (8 - d * (4 - f * (2 - h)))
            symbol = complex(real, imag)
        
        # Normalize symbol energy
        return symbol / self.normalization
    
    def demodulate(self, symbols, demod_type='hard', noise_var=0):
        """
        Demodulate (map) constellation symbols to bits.
        
        Parameters:
        -----------
        symbols : 1D ndarray of complex floats
            Input symbols to be demodulated.
        
        demod_type : str, optional
            'hard' for hard decision output (bits)
            'soft' for soft decision output (LLRs)
        
        noise_var : float, optional
            AWGN variance. Needed only for 'soft' demodulation.
        
        Returns:
        --------
        bits : 1D ndarray of ints or floats
            Demodulated bits (hard decision) or LLRs (soft decision).
        """
        if demod_type == 'hard':
            return self._hard_demodulate(symbols)
        elif demod_type == 'soft':
            if noise_var <= 0:
                raise ValueError("Noise variance must be positive for soft demodulation")
            return self._soft_demodulate(symbols, noise_var)
        else:
            raise ValueError("demod_type must be 'hard' or 'soft'")
    
    def _hard_demodulate(self, symbols):
        """
        Hard demodulation of symbols to bits.
        
        Parameters:
        -----------
        symbols : 1D ndarray of complex floats
            Input symbols to be demodulated.
        
        Returns:
        --------
        bits : 1D ndarray of ints
            Demodulated bits.
        """
        num_symbols = len(symbols)
        bits = np.zeros(num_symbols * self.bits_per_symbol, dtype=int)
        
        for i, symbol in enumerate(symbols):
            symbol_bits = self._symbol_to_bits_hard(symbol)
            bits[i * self.bits_per_symbol : (i + 1) * self.bits_per_symbol] = symbol_bits
        
        return bits
    
    def _symbol_to_bits_hard(self, symbol):
        """
        Hard demodulate a single symbol to bits.
        
        Parameters:
        -----------
        symbol : complex float
            Input symbol.
        
        Returns:
        --------
        bits : 1D ndarray of ints
            Demodulated bits.
        """
        if self.modulation_type in ['bpsk', 'pi/2-bpsk']:
            # BPSK and pi/2-BPSK hard demodulation
            return np.array([0]) if symbol.real > 0 else np.array([1])
        
        elif self.modulation_type == 'qpsk':
            # QPSK hard demodulation
            bit0 = 0 if symbol.real > 0 else 1
            bit1 = 0 if symbol.imag > 0 else 1
            return np.array([bit0, bit1])
        
        elif self.modulation_type == '16qam':
            # 16-QAM hard demodulation
            scaled_real = symbol.real * self.normalization
            scaled_imag = symbol.imag * self.normalization
            
            bit0 = 0 if scaled_real > 0 else 1
            bit1 = 0 if scaled_imag > 0 else 1
            bit2 = 0 if abs(scaled_real) < 2 else 1
            bit3 = 0 if abs(scaled_imag) < 2 else 1
            
            return np.array([bit0, bit1, bit2, bit3])
        
        elif self.modulation_type == '64qam':
            # 64-QAM hard demodulation
            scaled_real = symbol.real * self.normalization
            scaled_imag = symbol.imag * self.normalization
            
            bit0 = 0 if scaled_real > 0 else 1
            bit1 = 0 if scaled_imag > 0 else 1
            bit2 = 0 if abs(scaled_real) < 4 else 1
            bit3 = 0 if abs(scaled_imag) < 4 else 1
            # 修复bit4和bit5的判决逻辑
            # 64QAM星座点幅度值为±1, ±3, ±5, ±7（归一化前）
            # 当abs(scaled_real) < 2时，幅度为±1 → bit4=1
            # 当2 < abs(scaled_real) < 6时，幅度为±3 → bit4=0
            # 当abs(scaled_real) > 6时，幅度为±5或±7 → bit4=1
            bit4 = 0 if (abs(scaled_real) > 2 and abs(scaled_real) < 6) else 1
            bit5 = 0 if (abs(scaled_imag) > 2 and abs(scaled_imag) < 6) else 1
            
            return np.array([bit0, bit1, bit2, bit3, bit4, bit5])
        
        elif self.modulation_type == '256qam':
            # 256-QAM hard demodulation
            scaled_real = symbol.real * self.normalization
            scaled_imag = symbol.imag * self.normalization
            
            bit0 = 0 if scaled_real > 0 else 1
            bit1 = 0 if scaled_imag > 0 else 1
            bit2 = 0 if abs(scaled_real) < 8 else 1
            bit3 = 0 if abs(scaled_imag) < 8 else 1
            bit4 = 0 if abs(scaled_real) < 4 else 1
            bit5 = 0 if abs(scaled_imag) < 4 else 1
            bit6 = 0 if abs(scaled_real) < 2 else 1
            bit7 = 0 if abs(scaled_imag) < 2 else 1
            
            return np.array([bit0, bit1, bit2, bit3, bit4, bit5, bit6, bit7])
    
    def _soft_demodulate(self, symbols, noise_var):
        """
        Soft demodulation of symbols to LLRs.
        
        Parameters:
        -----------
        symbols : 1D ndarray of complex floats
            Input symbols to be demodulated.
        
        noise_var : float
            AWGN variance.
        
        Returns:
        --------
        llrs : 1D ndarray of floats
            Log-likelihood ratios.
        """
        # For simplicity, we'll implement max-log approximation for soft demodulation
        num_symbols = len(symbols)
        llrs = np.zeros(num_symbols * self.bits_per_symbol, dtype=float)
        
        # Generate all possible constellation points
        constellation, constellation_bits = self._generate_constellation()
        
        for i, symbol in enumerate(symbols):
            # Calculate distances to all constellation points
            distances = np.abs(symbol - constellation) ** 2
            
            # Calculate LLR for each bit
            for bit_pos in range(self.bits_per_symbol):
                # Separate constellation points by bit value at current position
                idx0 = np.where(constellation_bits[:, bit_pos] == 0)[0]
                idx1 = np.where(constellation_bits[:, bit_pos] == 1)[0]
                
                # Max-log approximation
                min_dist0 = np.min(distances[idx0])
                min_dist1 = np.min(distances[idx1])
                
                llr = (min_dist1 - min_dist0) / noise_var
                llrs[i * self.bits_per_symbol + bit_pos] = llr
        
        return llrs
    
    def _generate_constellation(self):
        """
        Generate the constellation points and their corresponding bits.
        
        Returns:
        --------
        constellation : 1D ndarray of complex floats
            Constellation points.
        
        constellation_bits : 2D ndarray of ints
            Bits corresponding to each constellation point.
        """
        num_points = 2 ** self.bits_per_symbol
        constellation = np.zeros(num_points, dtype=complex)
        constellation_bits = np.zeros((num_points, self.bits_per_symbol), dtype=int)
        
        # Generate all possible bit combinations
        for i in range(num_points):
            bits = dec2bitarray(i, self.bits_per_symbol)
            constellation_bits[i] = bits
            constellation[i] = self._map_bits_to_symbol(np.array(bits))
        
        return constellation, constellation_bits
    
    def plot_constellation(self, num_points=1000):
        """
        Plot the constellation diagram.
        
        Parameters:
        -----------
        num_points : int, optional
            Number of points to plot.
        """
        import matplotlib.pyplot as plt
        
        # Generate random bits and modulate
        random_bits = np.random.randint(0, 2, num_points * self.bits_per_symbol)
        symbols = self.modulate(random_bits)
        
        # Plot constellation
        plt.figure(figsize=(8, 8))
        plt.scatter(symbols.real, symbols.imag, s=10, alpha=0.5)
        plt.title(f'{self.modulation_type.upper()} Constellation')
        plt.xlabel('In-phase (I)')
        plt.ylabel('Quadrature (Q)')
        plt.grid(True)
        plt.axis('equal')
        plt.show()


# Predefined modems for convenience
def get_modem(modulation_type):
    """
    Get a modem instance for the specified modulation type.
    
    Parameters:
    -----------
    modulation_type : str
        Modulation type (e.g., 'qpsk', '16qam').
    
    Returns:
    --------
    modem : Modem instance
        Modem for the specified modulation type.
    """
    return Modem(modulation_type)
