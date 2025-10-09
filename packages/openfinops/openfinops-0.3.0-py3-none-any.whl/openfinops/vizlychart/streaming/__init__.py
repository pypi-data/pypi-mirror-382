"""
Real-Time Streaming Foundation for Vizly
========================================

High-performance real-time data streaming and visualization capabilities.
Supports live data feeds, WebSocket connections, and streaming chart updates.

Features:
- WebSocket-based real-time data streaming
- Buffered data management with configurable window sizes
- Real-time chart updates with minimal latency
- Multi-client broadcasting support
- Data compression and efficient serialization
- Streaming analytics and live aggregations

Basic Usage:
    >>> from vizly.streaming import StreamingChart, DataStreamer
    >>> streamer = DataStreamer("ws://localhost:8765")
    >>> chart = StreamingChart.line()
    >>> chart.connect_stream(streamer, buffer_size=1000)
    >>> chart.start_streaming()
"""

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



from .data_streamer import DataStreamer, StreamingBuffer, StreamingDataManager
from .streaming_charts import StreamingChart, RealtimeLineChart, RealtimeScatterChart
from .websocket_server import WebSocketStreamer, StreamingServer
from .compression import DataCompressor, StreamingProtocol
from .analytics import StreamingAnalytics, LiveAggregator

__version__ = "0.5.0"
__all__ = [
    # Core streaming
    "DataStreamer",
    "StreamingBuffer",
    "StreamingDataManager",
    # Streaming charts
    "StreamingChart",
    "RealtimeLineChart",
    "RealtimeScatterChart",
    # WebSocket infrastructure
    "WebSocketStreamer",
    "StreamingServer",
    # Data optimization
    "DataCompressor",
    "StreamingProtocol",
    # Analytics
    "StreamingAnalytics",
    "LiveAggregator",
]