"""Data compression and streaming protocol optimization for Vizly."""

# Copyright (c) 2025 Infinidatum
# Author: Duraimurugan Rajamanickam
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.



from __future__ import annotations

import numpy as np
import json
import zlib
import struct
import time
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


@dataclass
class CompressionStats:
    """Statistics for compression operations."""
    original_size: int
    compressed_size: int
    compression_ratio: float
    compression_time: float
    decompression_time: float = 0.0

    @property
    def space_savings(self) -> float:
        """Calculate space savings percentage."""
        if self.original_size == 0:
            return 0.0
        return (1.0 - self.compressed_size / self.original_size) * 100.0


class DataCompressor(ABC):
    """Abstract base class for data compression."""

    @abstractmethod
    def compress(self, data: Any) -> Tuple[bytes, CompressionStats]:
        """Compress data and return compressed bytes with stats."""
        pass

    @abstractmethod
    def decompress(self, compressed_data: bytes) -> Tuple[Any, CompressionStats]:
        """Decompress data and return original data with stats."""
        pass


class JsonCompressor(DataCompressor):
    """JSON-based compression with zlib."""

    def __init__(self, compression_level: int = 6):
        self.compression_level = compression_level

    def compress(self, data: Any) -> Tuple[bytes, CompressionStats]:
        """Compress data using JSON + zlib."""
        start_time = time.time()

        # Convert to JSON
        json_str = json.dumps(data, default=self._json_serializer)
        json_bytes = json_str.encode('utf-8')

        # Compress with zlib
        compressed = zlib.compress(json_bytes, self.compression_level)

        compression_time = time.time() - start_time

        stats = CompressionStats(
            original_size=len(json_bytes),
            compressed_size=len(compressed),
            compression_ratio=len(compressed) / len(json_bytes) if json_bytes else 1.0,
            compression_time=compression_time
        )

        return compressed, stats

    def decompress(self, compressed_data: bytes) -> Tuple[Any, CompressionStats]:
        """Decompress zlib + JSON data."""
        start_time = time.time()

        # Decompress with zlib
        json_bytes = zlib.decompress(compressed_data)

        # Parse JSON
        json_str = json_bytes.decode('utf-8')
        data = json.loads(json_str)

        decompression_time = time.time() - start_time

        stats = CompressionStats(
            original_size=len(json_bytes),
            compressed_size=len(compressed_data),
            compression_ratio=len(compressed_data) / len(json_bytes) if json_bytes else 1.0,
            compression_time=0.0,
            decompression_time=decompression_time
        )

        return data, stats

    def _json_serializer(self, obj):
        """Custom JSON serializer for numpy arrays and other types."""
        if isinstance(obj, np.ndarray):
            return {
                '__type__': 'ndarray',
                'data': obj.tolist(),
                'dtype': str(obj.dtype),
                'shape': obj.shape
            }
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.integer):
            return int(obj)
        elif hasattr(obj, 'to_dict'):
            return obj.to_dict()
        else:
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


class BinaryCompressor(DataCompressor):
    """Binary compression for numerical data."""

    def __init__(self, use_delta_encoding: bool = True):
        self.use_delta_encoding = use_delta_encoding

    def compress(self, data: Any) -> Tuple[bytes, CompressionStats]:
        """Compress numerical data using binary encoding."""
        start_time = time.time()

        if isinstance(data, dict):
            compressed_data = self._compress_dict(data)
        elif isinstance(data, (list, np.ndarray)):
            compressed_data = self._compress_array(data)
        else:
            # Fallback to JSON compression
            json_compressor = JsonCompressor()
            return json_compressor.compress(data)

        compression_time = time.time() - start_time

        # Estimate original size (simplified)
        original_size = len(json.dumps(data, default=str).encode('utf-8'))

        stats = CompressionStats(
            original_size=original_size,
            compressed_size=len(compressed_data),
            compression_ratio=len(compressed_data) / original_size if original_size else 1.0,
            compression_time=compression_time
        )

        return compressed_data, stats

    def decompress(self, compressed_data: bytes) -> Tuple[Any, CompressionStats]:
        """Decompress binary data."""
        start_time = time.time()

        try:
            data = self._decompress_binary(compressed_data)
        except Exception as e:
            logger.warning(f"Binary decompression failed, trying JSON fallback: {e}")
            json_compressor = JsonCompressor()
            return json_compressor.decompress(compressed_data)

        decompression_time = time.time() - start_time

        # Estimate sizes
        original_size = len(json.dumps(data, default=str).encode('utf-8'))

        stats = CompressionStats(
            original_size=original_size,
            compressed_size=len(compressed_data),
            compression_ratio=len(compressed_data) / original_size if original_size else 1.0,
            compression_time=0.0,
            decompression_time=decompression_time
        )

        return data, stats

    def _compress_array(self, array: Union[List, np.ndarray]) -> bytes:
        """Compress numerical array."""
        if not isinstance(array, np.ndarray):
            array = np.array(array)

        # Header: magic number, shape, dtype
        header = struct.pack('<I', 0xFEEDFACE)  # Magic number
        header += struct.pack('<I', len(array.shape))
        for dim in array.shape:
            header += struct.pack('<I', dim)
        header += struct.pack('<I', len(array.dtype.str))
        header += array.dtype.str.encode('ascii')

        # Data compression
        if self.use_delta_encoding and array.dtype.kind in 'fi':
            # Delta encoding for numeric data
            if len(array.shape) == 1:
                deltas = np.diff(array, prepend=array[0])
                data_bytes = deltas.astype(np.float32).tobytes()
            else:
                # Flatten for multi-dimensional arrays
                flat_array = array.flatten()
                deltas = np.diff(flat_array, prepend=flat_array[0])
                data_bytes = deltas.astype(np.float32).tobytes()
        else:
            data_bytes = array.tobytes()

        # Compress data
        compressed_data = zlib.compress(data_bytes)

        return header + struct.pack('<I', len(compressed_data)) + compressed_data

    def _compress_dict(self, data: Dict) -> bytes:
        """Compress dictionary with mixed data types."""
        # For simplicity, fall back to JSON compression for dicts
        json_compressor = JsonCompressor()
        compressed, _ = json_compressor.compress(data)
        return compressed

    def _decompress_binary(self, data: bytes) -> Any:
        """Decompress binary array data."""
        offset = 0

        # Check magic number
        magic = struct.unpack('<I', data[offset:offset+4])[0]
        offset += 4

        if magic != 0xFEEDFACE:
            raise ValueError("Invalid magic number")

        # Read shape
        ndims = struct.unpack('<I', data[offset:offset+4])[0]
        offset += 4

        shape = []
        for _ in range(ndims):
            dim = struct.unpack('<I', data[offset:offset+4])[0]
            shape.append(dim)
            offset += 4

        # Read dtype
        dtype_len = struct.unpack('<I', data[offset:offset+4])[0]
        offset += 4

        dtype_str = data[offset:offset+dtype_len].decode('ascii')
        offset += dtype_len

        # Read compressed data length
        compressed_len = struct.unpack('<I', data[offset:offset+4])[0]
        offset += 4

        # Decompress data
        compressed_data = data[offset:offset+compressed_len]
        data_bytes = zlib.decompress(compressed_data)

        # Reconstruct array
        if self.use_delta_encoding:
            # Reconstruct from deltas
            deltas = np.frombuffer(data_bytes, dtype=np.float32)
            array = np.cumsum(deltas).astype(dtype_str)
        else:
            array = np.frombuffer(data_bytes, dtype=dtype_str)

        return array.reshape(shape)


class StreamingProtocol:
    """Protocol handler for streaming data with compression."""

    def __init__(self, compression_type: str = 'json', compression_level: int = 6):
        self.compression_type = compression_type

        if compression_type == 'json':
            self.compressor = JsonCompressor(compression_level)
        elif compression_type == 'binary':
            self.compressor = BinaryCompressor()
        else:
            raise ValueError(f"Unknown compression type: {compression_type}")

        # Statistics
        self.total_messages = 0
        self.total_original_bytes = 0
        self.total_compressed_bytes = 0
        self.total_compression_time = 0.0
        self.total_decompression_time = 0.0

    def encode_message(self, message_type: str, data: Any,
                      metadata: Optional[Dict] = None) -> bytes:
        """Encode message with compression."""
        # Create message envelope
        envelope = {
            'type': message_type,
            'data': data,
            'timestamp': time.time(),
            'metadata': metadata or {}
        }

        # Compress
        compressed_data, stats = self.compressor.compress(envelope)

        # Update statistics
        self.total_messages += 1
        self.total_original_bytes += stats.original_size
        self.total_compressed_bytes += stats.compressed_size
        self.total_compression_time += stats.compression_time

        # Add protocol header
        header = struct.pack('<II', len(compressed_data),
                           hash(self.compression_type) & 0xFFFFFFFF)

        return header + compressed_data

    def decode_message(self, data: bytes) -> Tuple[str, Any, Optional[Dict]]:
        """Decode compressed message."""
        # Read header
        if len(data) < 8:
            raise ValueError("Invalid message: too short")

        data_len, compression_hash = struct.unpack('<II', data[:8])
        compressed_data = data[8:8+data_len]

        if len(compressed_data) != data_len:
            raise ValueError("Invalid message: data length mismatch")

        # Decompress
        envelope, stats = self.compressor.decompress(compressed_data)

        # Update statistics
        self.total_decompression_time += stats.decompression_time

        return envelope['type'], envelope['data'], envelope.get('metadata')

    def get_compression_stats(self) -> Dict[str, Any]:
        """Get compression statistics."""
        if self.total_messages == 0:
            return {
                'messages': 0,
                'compression_ratio': 1.0,
                'space_savings': 0.0,
                'avg_compression_time': 0.0,
                'avg_decompression_time': 0.0
            }

        compression_ratio = (self.total_compressed_bytes / self.total_original_bytes
                           if self.total_original_bytes > 0 else 1.0)

        space_savings = (1.0 - compression_ratio) * 100.0

        return {
            'messages': self.total_messages,
            'total_original_bytes': self.total_original_bytes,
            'total_compressed_bytes': self.total_compressed_bytes,
            'compression_ratio': compression_ratio,
            'space_savings': space_savings,
            'avg_compression_time': self.total_compression_time / self.total_messages,
            'avg_decompression_time': self.total_decompression_time / self.total_messages,
            'compression_type': self.compression_type
        }


class AdaptiveCompressor:
    """Adaptive compressor that chooses best compression strategy."""

    def __init__(self):
        self.compressors = {
            'json': JsonCompressor(),
            'binary': BinaryCompressor(),
        }

        # Performance history
        self.performance_history: Dict[str, List[float]] = {
            name: [] for name in self.compressors.keys()
        }

    def compress(self, data: Any) -> Tuple[bytes, str, CompressionStats]:
        """Compress using best available method."""
        best_compressor = None
        best_result = None
        best_stats = None
        best_name = None

        for name, compressor in self.compressors.items():
            try:
                result, stats = compressor.compress(data)

                # Score based on compression ratio and speed
                score = stats.compression_ratio + (stats.compression_time * 0.1)

                if best_result is None or score < best_stats.compression_ratio:
                    best_compressor = compressor
                    best_result = result
                    best_stats = stats
                    best_name = name

            except Exception as e:
                logger.warning(f"Compression with {name} failed: {e}")

        if best_result is None:
            raise RuntimeError("All compression methods failed")

        # Update performance history
        self.performance_history[best_name].append(best_stats.compression_ratio)
        if len(self.performance_history[best_name]) > 100:
            self.performance_history[best_name] = self.performance_history[best_name][-100:]

        return best_result, best_name, best_stats

    def decompress(self, data: bytes, compressor_name: str) -> Tuple[Any, CompressionStats]:
        """Decompress using specified method."""
        if compressor_name not in self.compressors:
            raise ValueError(f"Unknown compressor: {compressor_name}")

        return self.compressors[compressor_name].decompress(data)

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for all compressors."""
        summary = {}

        for name, history in self.performance_history.items():
            if history:
                summary[name] = {
                    'avg_compression_ratio': np.mean(history),
                    'min_compression_ratio': np.min(history),
                    'max_compression_ratio': np.max(history),
                    'sample_count': len(history)
                }
            else:
                summary[name] = {
                    'avg_compression_ratio': 1.0,
                    'min_compression_ratio': 1.0,
                    'max_compression_ratio': 1.0,
                    'sample_count': 0
                }

        return summary