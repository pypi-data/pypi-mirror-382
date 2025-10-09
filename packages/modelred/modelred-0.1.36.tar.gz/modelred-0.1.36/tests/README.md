# ModelRed SDK Local Testing Suite

Comprehensive test scripts to validate all SDK functionality before publishing.

## 📋 Test Coverage

This test suite covers **every feature** documented in the SDK:

### Test 1: Model Registration (`test_1_model_registration.py`)

- ✅ Register OpenAI GPT-4o-mini model
- ✅ Register Anthropic Claude 3.5 Haiku model
- ✅ Register OpenRouter GPT-4o-mini model
- ✅ List all models with pagination
- ✅ Get specific model by ID
- ✅ Handle ConflictError for duplicate models

### Test 2: Probe Discovery (`test_2_probe_discovery.py`)

- ✅ List all available probes
- ✅ Filter probes by severity (critical, high, medium, low)
- ✅ Filter probes by category (prompt_injection, jailbreaks, etc.)
- ✅ Combine category + severity filters
- ✅ Check available categories and severities

### Test 3: Assessment Creation (`test_3_assessment_creation.py`)

- ✅ Create assessment with preset="quick"
- ✅ Create assessment with preset="standard"
- ✅ Create assessment with category filter
- ✅ Create assessment with severity filter
- ✅ Create assessment with category + severity
- ✅ Create assessment with manual test_types
- ✅ Test validation (mixing selection methods should fail)
- ✅ Get assessment by ID
- ✅ List recent assessments

### Test 4: Assessment Waiting & Results (`test_4_assessment_waiting.py`)

- ✅ Wait for completion with built-in progress_tracker
- ✅ Wait for completion with custom progress callback
- ✅ Check detailed report structure (snake_case fields)
- ✅ Get assessment status without waiting
- ✅ Validate report fields (overall_score, risk_level, etc.)

### Test 5: Helper Functions (`test_5_helper_functions.py`)

- ✅ print_header() - Formatted headers
- ✅ print_model_info() - Model details
- ✅ print_assessment_summary() - Assessment overview
- ✅ print_detailed_report() - Full report display
- ✅ print_assessments_list() - List formatting
- ✅ progress_tracker - Progress callback
- ✅ print_full_results() - Complete results display

### Test 6: Context Managers & Async (`test_6_context_managers_async.py`)

- ✅ Sync context manager (with statement)
- ✅ Async context manager (async with)
- ✅ All async methods (list_models, list_probes, create_assessment, etc.)
- ✅ Async wait_for_completion with callbacks
- ✅ Async model registration
- ✅ Automatic client.close() on context exit

## 🚀 Quick Start

### 1. Setup Environment

First, create a `.env` file in the `tests/` directory:

```bash
cd packages/python/tests
cp .env.example .env  # or create .env from scratch
```

Edit `.env` and add your API keys:

```env
# ModelRed API Key (Required)
MODELRED_API_KEY=mr_your_api_key_here

# OpenAI API Key (for GPT-4o-mini)
OPENAI_API_KEY=sk-your_openai_key_here

# Anthropic API Key (for Claude 3.5 Haiku)
ANTHROPIC_API_KEY=sk-ant-your_anthropic_key_here

# OpenRouter API Key (for GPT-4o-mini via OpenRouter)
OPENROUTER_API_KEY=sk-or-your_openrouter_key_here
```

### 2. Install Dependencies

Install python-dotenv for loading .env files:

```bash
pip install python-dotenv
```

Or use uv:

```bash
uv pip install python-dotenv
```

### 3. Run All Tests

Run the master test script:

```bash
python tests/run_all_tests.py
```

This will run all 6 test scripts in sequence and provide a summary.

### 4. Run Individual Tests

You can also run tests individually:

```bash
# Test model registration
python tests/test_1_model_registration.py

# Test probe discovery
python tests/test_2_probe_discovery.py

# Test assessment creation
python tests/test_3_assessment_creation.py

# Test assessment waiting
python tests/test_4_assessment_waiting.py

# Test helper functions
python tests/test_5_helper_functions.py

# Test async & context managers
python tests/test_6_context_managers_async.py
```

## 📊 Expected Output

### Successful Test Run

```
================================================================================
  ModelRed SDK - Comprehensive Test Suite
================================================================================

This will test all SDK functionality:
  1. Model Registration (OpenAI, Anthropic, OpenRouter)
  2. Probe Discovery (filtering by category/severity)
  3. Assessment Creation (presets, filters, manual)
  4. Assessment Waiting & Results
  5. Helper Functions
  6. Context Managers & Async

Press Enter to start...

================================================================================
  Running: Test 1 Model Registration
================================================================================

✅ API Key loaded: mr_abc123...
✅ ModelRed client initialized
✅ OpenAI model registered: test-gpt4o-mini
✅ Anthropic model registered: test-claude-haiku
✅ OpenRouter model registered: test-openrouter-gpt4o
...
✅ ALL MODEL REGISTRATION TESTS PASSED

================================================================================
  TEST SUMMARY
================================================================================

Total Tests: 6
✅ Passed: 6
❌ Failed: 0

Success Rate: 100.0%

================================================================================
  🎉 ALL TESTS PASSED! 🎉
================================================================================
```

## 🔍 What Each Test Validates

### Documentation Accuracy

- ✅ All code examples from docs work correctly
- ✅ All parameter names match documentation
- ✅ All return types match documentation
- ✅ All helper functions exist and work

### API Correctness

- ✅ All endpoints respond correctly
- ✅ Error handling works as expected
- ✅ Validation prevents invalid usage
- ✅ Context managers close resources properly

### Feature Completeness

- ✅ All three selection methods work (preset, category/severity, manual)
- ✅ All providers can be registered (OpenAI, Anthropic, OpenRouter)
- ✅ All filtering options work (category, severity, combined)
- ✅ Both sync and async clients work identically

## 🐛 Troubleshooting

### "MODELRED_API_KEY not found"

- Make sure `.env` file exists in `tests/` directory
- Check that `MODELRED_API_KEY=...` line is uncommented
- Get your API key from https://app.modelred.ai/api-keys

### "Import dotenv could not be resolved"

```bash
pip install python-dotenv
```

### "Model already exists" warnings

This is normal! The tests use try/except with ConflictError to handle existing models gracefully.

### Assessment timeouts

Assessments can take 5-30 minutes depending on:

- Number of probes selected
- Queue priority (HIGH = faster)
- Server load

The tests use 30-minute timeouts by default.

### "No probes found for category"

- Check your subscription tier - some categories require Pro/Enterprise
- Verify the category name is correct (use test_2 to see available categories)

## 📝 Modifying Tests

### Test Different Models

Edit the model configurations in test files:

```python
# In test_1_model_registration.py
model_name="gpt-4o"  # Change from gpt-4o-mini
```

### Test Different Probes

Change the probe selection in test files:

```python
# In test_3_assessment_creation.py
category="medical_ethics"  # Test Pro+ category
severity="high"  # Test high severity
```

### Adjust Timeouts

For longer/shorter timeouts:

```python
# In test_4_assessment_waiting.py
timeout_minutes=60  # Change from 30
```

## ✅ Success Criteria

All tests should pass before publishing:

- ✅ No import errors
- ✅ No API connection errors
- ✅ All assertions pass
- ✅ No unexpected exceptions
- ✅ Helper functions display correctly
- ✅ Async methods work identically to sync

## 🎯 Next Steps

After all tests pass:

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Build package: `python -m build`
4. Publish to PyPI: `python -m twine upload dist/*`

## 📚 Additional Resources

- [SDK Documentation](../SDK_DOCUMENTATION.md)
- [ModelRed Dashboard](https://app.modelred.ai)
- [API Documentation](https://docs.modelred.ai)
