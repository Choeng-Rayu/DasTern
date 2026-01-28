#!/bin/bash
# Final Cleanup Script - Run this to complete reorganization

echo "🧹 Finalizing ai-llm-service organization..."
echo ""

cd "$(dirname "$0")"

# Move tools
echo "📦 Moving tools..."
[ -f "add_training_simple.py" ] && mv add_training_simple.py tools/ && echo "  ✓ add_training_simple.py → tools/"
[ -f "process_with_corrections.py" ] && mv process_with_corrections.py tools/ && echo "  ✓ process_with_corrections.py → tools/"

# Move tests
echo "🧪 Moving tests..."
[ -f "test_phase2.py" ] && mv test_phase2.py tests/ && echo "  ✓ test_phase2.py → tests/"
[ -f "test_real_ocr_data.py" ] && mv test_real_ocr_data.py tests/ && echo "  ✓ test_real_ocr_data.py → tests/"
[ -f "test_simple.py" ] && mv test_simple.py tests/ && echo "  ✓ test_simple.py → tests/"
[ -f "demo_showcase.sh" ] && mv demo_showcase.sh tests/ && echo "  ✓ demo_showcase.sh → tests/"

# Move documentation
echo "📚 Moving documentation..."
[ -f "QUICK_REFERENCE.md" ] && mv QUICK_REFERENCE.md docs/ && echo "  ✓ QUICK_REFERENCE.md → docs/"
[ -f "TESTING_GUIDE.md" ] && mv TESTING_GUIDE.md docs/ && echo "  ✓ TESTING_GUIDE.md → docs/"
[ -f "DAILY_PROGRESS_SHOWCASE.md" ] && mv DAILY_PROGRESS_SHOWCASE.md docs/ && echo "  ✓ DAILY_PROGRESS_SHOWCASE.md → docs/"

# Move reports
echo "📊 Moving reports..."
for file in correction_report*.json test_result*.json; do
    [ -f "$file" ] && mv "$file" reports/ && echo "  ✓ $file → reports/"
done

# Remove old files
echo "🗑️  Removing unused files..."
[ -f "add_training_example.py" ] && rm add_training_example.py && echo "  ✓ Removed add_training_example.py"
[ -f "cleanup_and_reorganize.sh" ] && rm cleanup_and_reorganize.sh && echo "  ✓ Removed cleanup_and_reorganize.sh"

# Create gitignore for reports
cat > reports/.gitignore << 'EOF'
# Ignore all generated reports
*
!.gitignore
!README.md
EOF

# Create reports README
cat > reports/README.md << 'EOF'
# Reports Directory

This folder contains auto-generated correction reports and test results.

## Files Generated Here:
- `correction_report_YYYYMMDD_HHMMSS.json` - Detailed correction analysis
- `test_result_YYYYMMDD_HHMMSS.json` - Test outputs

## Note:
These files are temporary and regenerated each time you run the tools.
They are gitignored to keep the repository clean.

## View Reports:
```bash
# List all reports
ls -lth reports/

# View latest report
cat reports/correction_report_*.json | jq

# Count corrections in latest report
cat reports/correction_report_*.json | jq '.corrections_made.total_corrections'
```
EOF

echo ""
echo "✅ Reorganization complete!"
echo ""
echo "📁 New Structure:"
echo "   tools/     - User-facing scripts (add_training, process_corrections)"
echo "   tests/     - Test scripts and demos"
echo "   docs/      - Documentation and guides"
echo "   reports/   - Generated outputs (gitignored)"
echo "   app/       - Core application code"
echo "   prompts/   - AI system prompts"
echo "   data/      - Training data and OCR files"
echo ""
echo "📖 See README.md for usage instructions"
echo ""
echo "🚀 Quick start:"
echo "   source venv/bin/activate"
echo "   python3 tools/add_training_simple.py data/ocr.json"
echo "   python3 tools/process_with_corrections.py data/ocr.json"
