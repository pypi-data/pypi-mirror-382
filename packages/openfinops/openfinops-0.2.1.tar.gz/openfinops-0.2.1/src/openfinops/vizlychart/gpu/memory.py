"""GPU memory management for Vizly."""

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

import logging
import threading
import weakref
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class MemoryInfo:
    """Memory usage information."""
    total_bytes: int
    used_bytes: int
    free_bytes: int
    device_name: str


class GPUMemoryManager:
    """Manages GPU memory allocation and cleanup."""

    def __init__(self):
        self._allocations: Dict[str, Any] = {}
        self._lock = threading.RLock()
        self.total_allocated = 0

    def allocate(self, size_bytes: int, name: str = "unnamed") -> str:
        """Allocate GPU memory."""
        with self._lock:
            allocation_id = f"alloc_{len(self._allocations)}_{name}"
            self._allocations[allocation_id] = {
                'size': size_bytes,
                'name': name
            }
            self.total_allocated += size_bytes
            logger.debug(f"Allocated {size_bytes} bytes as {allocation_id}")
            return allocation_id

    def deallocate(self, allocation_id: str):
        """Deallocate GPU memory."""
        with self._lock:
            if allocation_id in self._allocations:
                size = self._allocations[allocation_id]['size']
                del self._allocations[allocation_id]
                self.total_allocated -= size
                logger.debug(f"Deallocated {allocation_id} ({size} bytes)")

    def get_memory_info(self) -> MemoryInfo:
        """Get current memory usage information."""
        return MemoryInfo(
            total_bytes=1024 * 1024 * 1024,  # 1GB default
            used_bytes=self.total_allocated,
            free_bytes=1024 * 1024 * 1024 - self.total_allocated,
            device_name="GPU"
        )

    def cleanup(self):
        """Clean up all allocations."""
        with self._lock:
            self._allocations.clear()
            self.total_allocated = 0