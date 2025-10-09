#!/usr/bin/env python3
"""
Runtime fix for xgrammar concurrency bug in vLLM 0.8.5.post1

This script patches the installed vLLM package to fix the token_bitmask
race condition in XGrammarLogitsProcessor.clone()

Usage:
    python fix_xgrammar_concurrency.py

Can be used in Dockerfile or run on deployed systems.
"""

import os
import sys
import glob


def find_xgrammar_decoding_file():
    """Find the xgrammar_decoding.py file in installed packages."""
    # Common installation paths
    possible_paths = [
        "/usr/local/lib/python*/dist-packages/vllm/model_executor/guided_decoding/xgrammar_decoding.py",
        "/usr/lib/python*/dist-packages/vllm/model_executor/guided_decoding/xgrammar_decoding.py",
        "~/.local/lib/python*/site-packages/vllm/model_executor/guided_decoding/xgrammar_decoding.py",
    ]
    
    for pattern in possible_paths:
        expanded = os.path.expanduser(pattern)
        matches = glob.glob(expanded)
        if matches:
            return matches[0]
    
    # Fallback: try to import and find the file
    try:
        import vllm.model_executor.guided_decoding.xgrammar_decoding as xgr_module
        return xgr_module.__file__
    except ImportError:
        pass
    
    return None


def apply_fix(file_path):
    """Apply the concurrency fix to the file."""
    print(f"Applying fix to: {file_path}")
    
    # Read the file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check if already fixed
    if 'xgr.allocate_token_bitmask' in content:
        print("✅ Fix already applied!")
        return True
    
    # The buggy code to replace
    old_code = "new_processor.token_bitmask = self.token_bitmask"
    
    # The fixed code
    new_code = """new_processor.token_bitmask = xgr.allocate_token_bitmask(
                self.batch_size, self.tokenizer_info.vocab_size)"""
    
    # Check if we can find the code to replace
    if old_code not in content:
        print("❌ Could not find code to replace!")
        print("   The file may have already been modified or is a different version.")
        return False
    
    # Apply the fix
    content = content.replace(old_code, new_code)
    
    # Update the comment too
    old_comment = "# Create a new token bitmask with the same size"
    new_comment = """# Allocate a NEW token bitmask for this clone to avoid sharing state
        # between concurrent requests. The previous code had a bug where
        # the bitmask was shared, causing corruption under high concurrency."""
    
    if old_comment in content:
        content = content.replace(old_comment, new_comment)
    
    # Write back
    try:
        with open(file_path, 'w') as f:
            f.write(content)
        print("✅ Fix applied successfully!")
        return True
    except PermissionError:
        print("❌ Permission denied. Run with sudo or appropriate permissions.")
        return False


def verify_fix():
    """Verify the fix is working."""
    try:
        import inspect
        from vllm.model_executor.guided_decoding.xgrammar_decoding import (
            XGrammarLogitsProcessor
        )
        
        source = inspect.getsource(XGrammarLogitsProcessor.clone)
        
        if 'allocate_token_bitmask' in source:
            print("✅ Verification passed: Fix is active")
            return True
        else:
            print("❌ Verification failed: Fix not detected in code")
            return False
    except Exception as e:
        print(f"⚠️  Verification skipped: {e}")
        return False


def main():
    """Main entry point."""
    print("\n" + "="*70)
    print("vLLM XGrammar Concurrency Bug Fix")
    print("="*70 + "\n")
    
    # Find the file
    file_path = find_xgrammar_decoding_file()
    
    if not file_path:
        print("❌ Could not find xgrammar_decoding.py")
        print("   Make sure vLLM is installed: pip install vllm")
        sys.exit(1)
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        sys.exit(1)
    
    # Apply the fix
    success = apply_fix(file_path)
    
    if not success:
        sys.exit(1)
    
    # Verify
    print("\nVerifying fix...")
    verify_fix()
    
    print("\n" + "="*70)
    print("Done! Restart your vLLM service for changes to take effect.")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()

