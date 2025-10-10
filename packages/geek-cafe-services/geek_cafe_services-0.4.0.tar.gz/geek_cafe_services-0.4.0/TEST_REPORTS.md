# Test Reports

This project generates comprehensive HTML reports for unit tests and code coverage, with detailed coverage analysis in the terminal and **automatic README.md updates**.

## Running Tests with Reports

Execute the test script to generate both test results and coverage reports:

```bash
./run_unit_tests.sh
```

This will:
1. ✅ Run all 492 tests
2. 📊 Generate coverage reports (HTML, JSON)
3. 📋 Generate test report (HTML)
4. 📝 **Automatically update README.md with coverage badges**

## Automatic README Updates

The test script automatically updates `README.md` with:

### 📊 Coverage Badges
- **Tests badge** - Shows number of passing tests
- **Coverage badge** - Shows overall coverage percentage with color coding

### 📈 Coverage Summary Table
- Total statements
- Covered statements
- Missing statements
- Coverage percentage
- Test count and status

### 📉 Files Needing Attention
- Lists files with < 80% coverage
- Shows missing line counts
- Helps prioritize testing efforts

### Example README Section
```markdown
## Test Coverage

![Tests](https://img.shields.io/badge/tests-492%20passed-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-83.5%25-green)

**Overall Coverage:** 83.5% (3483/4172 statements)

| Coverage | Missing Lines | File |
|----------|---------------|------|
| 0.0% | 9 | `core/audit_mixin.py` |
| 47.9% | 160 | `utilities/lambda_event_utility.py` |
...
```

## Manual README Update

To manually update the README without running tests:

```bash
python3 update_readme_badges.py
```

This requires that tests have been run at least once to generate `reports/coverage.json`.

## Terminal Coverage Summary

After running tests, you'll see a detailed coverage summary in the terminal:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 COVERAGE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 Overall Coverage: 83.5%

📉 Files with LOWEST coverage (< 80%):
--------------------------------------------------------------------------------
    0.0% -   9 lines missing - core/audit_mixin.py
   47.9% - 160 lines missing - utilities/lambda_event_utility.py
   54.5% -  20 lines missing - core/service_result.py
   ...

📈 Files with HIGHEST coverage (>= 95%):
--------------------------------------------------------------------------------
  100.0% - utilities/response.py
  100.0% - utilities/http_status_code.py
  100.0% - models/website_analytics_summary.py
   ...
```

This summary helps you quickly identify:
- **Overall coverage percentage**
- **Files needing more test coverage** (< 80%)
- **Well-tested files** (>= 95%)
- **Number of missing lines** for each file

## Generated Reports

After running tests, the following reports are available:

### 📋 Test Report
- **Location:** `reports/test-report.html`
- **Contents:**
  - Complete test execution results
  - Pass/fail status for each test
  - Test execution time
  - Error details and stack traces
  - Test metadata and environment info

### 📊 Coverage Report (HTML)
- **Location:** `reports/coverage/index.html`
- **Contents:**
  - Overall code coverage percentage (currently 83%)
  - Per-file coverage breakdown
  - Line-by-line coverage visualization
  - Missing coverage highlights
  - Function and class coverage details

### 📈 Coverage Report (JSON)
- **Location:** `reports/coverage.json`
- **Contents:**
  - Machine-readable coverage data
  - Per-file statistics
  - Line-level coverage information
  - Useful for CI/CD integration and custom analysis

## Viewing Reports

### Terminal Summary
The coverage summary is automatically displayed after test execution.

### HTML Reports
Open the reports in your browser:

```bash
# Open test report
open reports/test-report.html

# Open coverage report (interactive)
open reports/coverage/index.html
```

Or navigate to the files directly in your file browser.

## Understanding Coverage Metrics

### Coverage Percentages
- **100%** - Fully covered (green) ✅
- **95-99%** - Excellent coverage (green) ✅
- **80-94%** - Good coverage (yellow) ⚠️
- **< 80%** - Needs improvement (red) ❌

### What the Numbers Mean
- **Percent Covered** - Percentage of executable lines that were run during tests
- **Lines Missing** - Number of lines not executed during tests
- **Statements** - Individual code statements
- **Branches** - Decision points (if/else, loops)

### Files Needing Attention
The terminal summary highlights files with < 80% coverage:
- `core/audit_mixin.py` - 0% (unused mixin)
- `utilities/lambda_event_utility.py` - 48% (160 lines missing)
- `core/service_result.py` - 55% (20 lines missing)

## Report Features

### Test Report Features:
- ✅ **Self-contained HTML** - No external dependencies
- 📊 **Summary statistics** - Total tests, passed, failed, skipped
- ⏱️ **Execution times** - Performance metrics for each test
- 🔍 **Detailed failures** - Full stack traces and error messages
- 🏷️ **Test metadata** - Test markers, fixtures, and parameters

### Coverage Report Features:
- 📈 **Interactive navigation** - Click through files and functions
- 🎨 **Color-coded lines** - Green (covered), red (missed), yellow (partial)
- 📊 **Coverage metrics** - Statements, branches, functions
- 🔍 **Search functionality** - Find specific files or functions
- 📱 **Responsive design** - Works on desktop and mobile
- 📉 **Sortable tables** - Sort by coverage percentage, file name, etc.

## CI/CD Integration

The test script can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run tests with coverage
  run: ./run_unit_tests.sh

- name: Upload coverage report
  uses: actions/upload-artifact@v3
  with:
    name: coverage-report
    path: reports/coverage/

- name: Upload test report
  uses: actions/upload-artifact@v3
  with:
    name: test-report
    path: reports/test-report.html

- name: Check coverage threshold
  run: |
    COVERAGE=$(python3 -c "import json; print(json.load(open('reports/coverage.json'))['totals']['percent_covered'])")
    if (( $(echo "$COVERAGE < 80" | bc -l) )); then
      echo "Coverage $COVERAGE% is below 80% threshold"
      exit 1
    fi
```

## Report Directory Structure

```
reports/
├── test-report.html          # Main test results report
├── coverage.json             # Coverage data (JSON format)
└── coverage/                 # Coverage report directory
    ├── index.html           # Coverage summary
    ├── class_index.html     # Class coverage index
    ├── function_index.html  # Function coverage index
    ├── status.json          # Coverage data (JSON)
    └── [source files].html  # Individual file coverage
```

## Customization

To modify report generation, edit `run_unit_tests.sh`:

```bash
# Add custom pytest options
python -m pytest tests/ -v --tb=short \
    --cov=geek_cafe_services \
    --cov-report=term-missing \
    --cov-report=html:reports/coverage \
    --cov-report=json:reports/coverage.json \
    --html=reports/test-report.html \
    --self-contained-html \
    --cov-fail-under=80  # Set minimum coverage threshold
```

### Coverage Threshold
To enforce a minimum coverage percentage:
```bash
--cov-fail-under=80  # Fail if coverage < 80%
```

### Additional Report Formats
```bash
--cov-report=xml:reports/coverage.xml  # XML format for SonarQube
--cov-report=lcov:reports/coverage.lcov  # LCOV format for Codecov
```

## Dependencies

The following packages are required for report generation:
- `pytest-cov` - Coverage reporting
- `pytest-html` - HTML test reports

These are automatically installed in the virtual environment.

## Notes

- Reports are excluded from version control (`.gitignore`)
- Reports are regenerated on each test run
- Coverage data is cumulative within a single run
- Self-contained HTML reports can be shared via email or file sharing
- JSON coverage data can be parsed for custom analysis or dashboards
