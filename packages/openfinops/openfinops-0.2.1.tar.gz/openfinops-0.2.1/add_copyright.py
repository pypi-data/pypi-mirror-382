#!/usr/bin/env python3
"""Script to add copyright headers to all Python files."""

import os
import sys
from pathlib import Path

COPYRIGHT_HEADER = '''# Copyright (c) 2025 Infinidatum
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

'''

def add_copyright_to_file(filepath):
    """Add copyright header to a Python file if not already present."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if copyright already exists
    if 'Copyright' in content or 'Infinidatum' in content:
        print(f"  Skipped (already has copyright): {filepath}")
        return False
    
    # Handle files starting with shebang
    if content.startswith('#!'):
        lines = content.split('\n', 1)
        if len(lines) == 2:
            new_content = lines[0] + '\n' + COPYRIGHT_HEADER + lines[1]
        else:
            new_content = lines[0] + '\n' + COPYRIGHT_HEADER
    # Handle files starting with docstring
    elif content.startswith('"""') or content.startswith("'''"):
        # Find end of docstring
        if content.startswith('"""'):
            end_idx = content.find('"""', 3) + 3
        else:
            end_idx = content.find("'''", 3) + 3
        
        if end_idx > 2:
            new_content = content[:end_idx] + '\n\n' + COPYRIGHT_HEADER + content[end_idx:]
        else:
            new_content = COPYRIGHT_HEADER + content
    else:
        new_content = COPYRIGHT_HEADER + content
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"  Added copyright to: {filepath}")
    return True

def main():
    # Find all Python files
    count = 0
    for root, dirs, files in os.walk('src'):
        # Skip __pycache__ directories
        dirs[:] = [d for d in dirs if d != '__pycache__']
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                if add_copyright_to_file(filepath):
                    count += 1
    
    # Add to agents directory
    if os.path.exists('agents'):
        for file in os.listdir('agents'):
            if file.endswith('.py'):
                filepath = os.path.join('agents', file)
                if add_copyright_to_file(filepath):
                    count += 1
    
    print(f"\n✅ Added copyright to {count} files")

if __name__ == '__main__':
    main()
