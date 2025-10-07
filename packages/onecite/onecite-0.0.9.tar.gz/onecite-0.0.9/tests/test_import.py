#!/usr/bin/env python3
# Test import script

print("🔍 Testing imports...")

try:
    import streamlit as st
    print("✅ streamlit imported successfully")
except ImportError as e:
    print(f"❌ streamlit import failed: {e}")

try:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from onecite import process_references
    print("✅ onecite imported successfully")
except ImportError as e:
    print(f"❌ onecite import failed: {e}")

print("\n🎯 If you see import failures, run:")
print("pip install streamlit")
print("pip install requests beautifulsoup4 lxml bibtexparser PyYAML thefuzz python-Levenshtein scholarly")
