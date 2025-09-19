#!/usr/bin/env python3
"""
Comprehensive Import Hack Remover for TalkBridge
===============================================

This script removes all sys.path.append() hacks and replaces them with clean
package imports for all Python files in the project.
"""

import os
import re
import sys
from pathlib import Path

def fix_import_hacks():
    """Fix import hacks in all problematic files."""
    
    # Read the files with syntax errors
    error_files = []
    error_file_path = "syntax_errors.txt"
    
    if os.path.exists(error_file_path):
        with open(error_file_path, 'r') as f:
            error_files = [line.strip() for line in f if line.strip()]
    
    if not error_files:
        print("No error files found in syntax_errors.txt")
        return
    
    print(f"🔧 Fixing import hacks in {len(error_files)} files...")
    
    # Common patterns to remove/fix
    patterns_to_remove = [
        # Path manipulation lines
        re.compile(r'.*sys\.path\.append.*'),
        re.compile(r'.*Path\(__file__\).*\.parent.*'),
        re.compile(r'^\s*\)\)\s*$'),                    # Orphaned closing parens
        re.compile(r'^\s*\.parent\)\s*$'),              # Orphaned .parent)
        re.compile(r'^\s*\.parent\.parent.*\)\s*$'),    # Orphaned .parent.parent...)
        re.compile(r'.*from pathlib import Path.*'),    # Remove pathlib import if used for path hacks
    ]
    
    # Import replacements
    import_fixes = {
        # Demo files
        'src/talkbridge/demo/animation_demo.py': [
            'from talkbridge.animation import AudioVisualizer, LoadingAnimation, InteractiveAnimations',
            'from talkbridge.animation.loading_animation import SpinnerAnimation, ProgressBar, PulseAnimation, WaveAnimation',
            'from talkbridge.animation.interactive_animations import ParticleSystem, GeometricAnimation, WaveformAnimation'
        ],
        'src/talkbridge/demo/animation_example.py': [
            'from talkbridge.animation import FaceSync'
        ],
        'src/talkbridge/demo/audio_demo.py': [
            'from talkbridge.audio import AudioGenerator, AudioSynthesizer, AudioEffects, AudioPlayer',
            'from talkbridge.audio.capture import AudioCapture'
        ],
        'src/talkbridge/demo/face_sync_demo.py': [
            'from talkbridge.animation.face_sync import FaceSync',
            'from talkbridge.audio.capture import AudioCapture'
        ],
        'src/talkbridge/demo/ollama_demo.py': [
            'from talkbridge.ollama import OllamaClient'
        ],
        'src/talkbridge/demo/tts_example.py': [
            'from talkbridge.tts import VoiceCloner, TTSEngine'
        ],
        # Test files
        'test/__init__.py': [
            '# Test package initialization',
            'import sys',
            'from pathlib import Path',
            '',
            '# Add src to path for testing',
            'src_path = Path(__file__).parent.parent / "src"',
            'if str(src_path) not in sys.path:',
            '    sys.path.insert(0, str(src_path))'
        ],
        'test/test_animations.py': [
            'import pytest',
            'from talkbridge.animation import AudioVisualizer, LoadingAnimation'
        ],
        'test/test_demo.py': [
            'import pytest',
            'from talkbridge.demo import animation_demo'
        ],
        'test/test_stt_module.py': [
            'import pytest',
            'from talkbridge.stt import STTEngine'
        ],
        'test/test_tts.py': [
            'import pytest',
            'from talkbridge.tts import TTSEngine'
        ],
        'test/test_error_handling.py': [
            'import pytest',
            'from talkbridge.errors import ErrorCategory, handle_user_facing_error'
        ],
        # Special cases
        'src/talkbridge/web/test/test_whisper.py': [
            'import pytest',
            'from talkbridge.stt.whisper_engine import WhisperEngine'
        ]
    }
    
    fixed_count = 0
    
    for file_path in error_files:
        if not os.path.exists(file_path):
            print(f"⚠️  File not found: {file_path}")
            continue
        
        print(f"🔧 Fixing: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"❌ Cannot read {file_path}: {e}")
            continue
        
        # Remove problematic lines
        new_lines = []
        removed_lines = []
        
        for i, line in enumerate(lines):
            should_remove = False
            
            for pattern in patterns_to_remove:
                if pattern.match(line):
                    should_remove = True
                    removed_lines.append(f"Line {i+1}: {line.strip()}")
                    break
            
            if not should_remove:
                new_lines.append(line)
        
        # Add proper imports if defined
        if file_path in import_fixes:
            # Find a good place to add imports (after existing imports or docstring)
            insert_idx = 0
            
            # Skip shebang and docstring
            for i, line in enumerate(new_lines):
                if line.strip().startswith('"""') and '"""' in line[3:]:
                    insert_idx = i + 1
                    break
                elif line.strip().startswith('"""'):
                    # Multi-line docstring, find the end
                    for j in range(i + 1, len(new_lines)):
                        if '"""' in new_lines[j]:
                            insert_idx = j + 1
                            break
                    break
                elif line.strip() and not line.startswith('#') and not line.startswith('"""'):
                    insert_idx = i
                    break
            
            # Insert new imports
            new_import_lines = []
            for import_line in import_fixes[file_path]:
                new_import_lines.append(import_line + '\n')
            
            new_import_lines.append('\n')  # Add blank line after imports
            
            new_lines = new_lines[:insert_idx] + new_import_lines + new_lines[insert_idx:]
        
        # Write the fixed file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            
            if removed_lines:
                print(f"  ✅ Removed {len(removed_lines)} problematic lines")
                for line in removed_lines:
                    print(f"    - {line}")
            
            if file_path in import_fixes:
                print(f"  ✅ Added {len(import_fixes[file_path])} clean imports")
            
            fixed_count += 1
            
        except Exception as e:
            print(f"❌ Cannot write {file_path}: {e}")
    
    print(f"\n📊 Summary: Fixed {fixed_count} files")
    return fixed_count

if __name__ == "__main__":
    fix_import_hacks()