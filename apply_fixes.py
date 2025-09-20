#!/usr/bin/env python3
"""
Apply fixes to rules_engine.py
"""

import shutil
import os

def apply_fixes():
    """Apply the fixes to rules_engine.py"""
    
    print("🔧 Applying fixes to rules_engine.py...")
    
    # Backup original file
    if os.path.exists('app/rules_engine.py'):
        shutil.copy('app/rules_engine.py', 'app/rules_engine_backup.py')
        print("✅ Created backup: app/rules_engine_backup.py")
    
    # Replace with fixed version
    shutil.copy('app/rules_engine_fixed.py', 'app/rules_engine.py')
    print("✅ Applied fixes to app/rules_engine.py")
    
    # Clean up
    os.remove('app/rules_engine_fixed.py')
    print("✅ Cleaned up temporary files")
    
    print("\n🎉 Fixes applied successfully!")
    print("\nFixed issues:")
    print("✅ 'argument of type int is not iterable' error")
    print("✅ Agent asking age twice")
    print("✅ Improved age recognition from birth year")
    print("✅ Added type safety checks")
    
    print("\n🧪 Test the fixes:")
    print("python test_phase2_features.py")

if __name__ == "__main__":
    apply_fixes()

