#!/usr/bin/env python3
"""Reorganize ai-llm-service folder"""
import os
import shutil
from pathlib import Path

# Create directories
dirs = ['tools', 'tests', 'docs', 'reports']
for d in dirs:
    Path(d).mkdir(exist_ok=True)
    print(f"✅ Created {d}/")

# Move files
moves = {
    'tools': ['add_training_simple.py', 'process_with_corrections.py'],
    'tests': ['test_phase2.py', 'test_real_ocr_data.py', 'test_simple.py', 'demo_showcase.sh'],
    'docs': ['QUICK_REFERENCE.md', 'TESTING_GUIDE.md', 'DAILY_PROGRESS_SHOWCASE.md'],
    'reports': ['correction_report_20260128_204805.json', 'test_result.json']
}

for dest, files in moves.items():
    for f in files:
        if os.path.exists(f):
            shutil.move(f, f'{dest}/{f}')
            print(f"📦 Moved {f} → {dest}/")

# Remove unused files
unused = ['add_training_example.py', 'cleanup_and_reorganize.sh']
for f in unused:
    if os.path.exists(f):
        os.remove(f)
        print(f"🗑️  Removed {f}")

# Create gitignore for reports
with open('reports/.gitignore', 'w') as f:
    f.write('# Ignore generated reports\n*\n!.gitignore\n')

print("\n✅ Reorganization complete!")
