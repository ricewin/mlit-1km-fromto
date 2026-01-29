# Test Strategy

This document outlines the testing strategy for the mlit-1km-fromto project.

## Overview

This project is a Streamlit application for visualizing human flow data based on open data from Japan's Ministry of Land, Infrastructure, Transport and Tourism (MLIT). The testing strategy focuses on ensuring the reliability and correctness of core functionality while accommodating the interactive nature of Streamlit applications.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures and configuration
├── unit/                    # Unit tests
│   ├── __init__.py
│   ├── test_utils.py       # Tests for common/utils.py
│   └── test_region_builder.py  # Tests for common/region_builder.py
└── integration/             # Integration tests (future)
    └── __init__.py
```

## Test Levels

### Unit Tests

Unit tests focus on testing individual functions and methods in isolation. These tests:

- **Target pure functions** without external dependencies (APIs, file I/O, Streamlit state)
- **Test data transformation logic** (coordinate conversions, dataframe operations)
- **Validate edge cases** (empty inputs, boundary conditions, invalid data)

**Current Coverage:**
- `app/common/utils.py`: Functions for data manipulation and geometry creation
  - `lonlat_to_polygon()`: Creating polygons from coordinates
  - `merge_df()`: Merging DataFrames with custom logic
  - `make_polygons()`: Converting coordinate data to GeoDataFrames
- `app/common/region_builder.py`: Region data handling
  - `prefcode_to_name()`: Prefecture and city code lookups

### Integration Tests

Integration tests (to be implemented in the future) would test:
- Interaction between multiple modules
- Data flow through the application
- Map rendering and visualization components

### Streamlit-Specific Considerations

**Not Tested:**
The following components are not covered by automated tests due to the interactive nature of Streamlit:
- Streamlit UI components (`st.pills`, `st.expander`, etc.)
- Session state management
- Page navigation and routing
- Interactive map rendering
- User input handling

**Rationale:**
- Streamlit applications are primarily interactive and visual
- Testing UI components requires complex mocking or end-to-end testing frameworks
- Core business logic is separated and tested independently
- Manual testing and visual inspection are more appropriate for UI verification

## Running Tests

### Run all tests:
```bash
pytest
```

### Run unit tests only:
```bash
pytest tests/unit/
```

### Run with verbose output:
```bash
pytest -v
```

### Run specific test markers:
```bash
pytest -m unit          # Run only unit tests
pytest -m integration   # Run only integration tests (when available)
pytest -m "not slow"    # Skip slow tests
```

### Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

## Test Fixtures

Common test fixtures are defined in `conftest.py`:
- `sample_dataframe`: Standard DataFrame with coordinate and value data
- `sample_geodataframe`: GeoDataFrame with geometry objects
- `sample_coordinates`: List of coordinate tuples for testing

## Test Markers

Tests are marked with pytest markers for categorization:
- `@pytest.mark.unit`: Unit tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.slow`: Tests that take significant time to run

## Dependencies

Testing dependencies (defined in `pyproject.toml`):
- `pytest`: Testing framework
- Additional dependencies inherited from main application (pandas, geopandas, shapely)

## Future Enhancements

### Potential Additions:
1. **Integration Tests**
   - Test data fetching and caching mechanisms
   - Test complete data processing pipelines
   
2. **Property-Based Testing**
   - Use `hypothesis` for testing with generated data
   - Validate invariants in coordinate transformations

3. **Performance Tests**
   - Benchmark critical operations
   - Test with large datasets

4. **Mock Testing**
   - Mock Streamlit session state for component testing
   - Mock external API calls (if any)

5. **End-to-End Tests**
   - Use tools like Selenium or Playwright for UI testing
   - Verify complete user workflows

## Best Practices

1. **Test Isolation**: Each test should be independent and not rely on others
2. **Clear Naming**: Test names should clearly describe what is being tested
3. **AAA Pattern**: Arrange, Act, Assert structure in tests
4. **Edge Cases**: Test boundary conditions and error cases
5. **Fast Tests**: Keep unit tests fast to encourage frequent execution
6. **Documentation**: Document complex test scenarios and fixtures

## Continuous Integration

To integrate with CI/CD:

1. **GitHub Actions** (recommended):
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install poetry
          poetry install
      - name: Run tests
        run: poetry run pytest
```

2. **Pre-commit Hooks**:
   - Run tests before commits
   - Enforce code quality standards

## Maintenance

- **Update tests** when adding new features or fixing bugs
- **Review test coverage** regularly to identify gaps
- **Refactor tests** to maintain clarity and reduce duplication
- **Remove obsolete tests** when functionality changes

## Contact

For questions about testing strategy or to report issues:
- Create an issue in the GitHub repository
- Refer to project documentation in `/docs`
