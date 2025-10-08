# SQL to XWQuery File Conversion Test Data

**Company:** eXonware.com  
**Author:** Eng. Muhammad AlShehri  
**Email:** connect@exonware.com  
**Version:** 0.0.1  
**Generation Date:** 07-Oct-2025

## Overview

This directory contains test data for SQL to XWQuery Script file conversion tests.
The tests verify that SQL queries (.sql files) can be correctly converted to XWQuery Script format (.xwquery files).

## Directory Structure

```
data/
├── inputs/              # Input SQL files for testing
│   ├── test_simple_users.sql
│   └── test_ecommerce_analytics.sql
├── expected/            # Expected XWQuery output files
│   ├── test_simple_users.xwquery
│   └── test_ecommerce_analytics.xwquery
├── outputs/             # Generated output files (created during tests)
│   └── *.xwquery
└── fixtures/            # Additional test fixtures
```

## File Extensions

### SQL Files (.sql)
- **Purpose**: Standard SQL query files
- **Extension**: `.sql`
- **Format**: SQL-92 or later syntax
- **Encoding**: UTF-8
- **Line Endings**: LF (Unix) or CRLF (Windows)

### XWQuery Files (.xwquery)
- **Purpose**: XWQuery Script format files
- **Extension**: `.xwquery`
- **Format**: XWQuery Script syntax (currently SQL-compatible)
- **Encoding**: UTF-8
- **Line Endings**: LF (Unix) or CRLF (Windows)

## Test Files

### test_simple_users.sql / test_simple_users.xwquery
Simple SELECT query demonstrating basic conversion:
- Basic SELECT statement
- WHERE clause with conditions
- ORDER BY and LIMIT clauses
- Comment preservation

### test_ecommerce_analytics.sql / test_ecommerce_analytics.xwquery
Complex analytical query demonstrating advanced conversion:
- Common Table Expressions (CTEs)
- Multiple JOINs
- Aggregation functions (SUM, COUNT, AVG)
- Window functions (ROW_NUMBER, PARTITION BY)
- HAVING clause
- CASE expressions
- Complex WHERE conditions
- Comment preservation

## Conversion Process

The conversion process follows these steps:

1. **Read SQL File**: Load SQL content from .sql file
2. **Parse SQL**: Parse SQL into XWQuery Script actions tree
3. **Generate XWQuery**: Convert actions tree to XWQuery format
4. **Write XWQuery File**: Save XWQuery content to .xwquery file
5. **Validate Output**: Compare with expected output

## XWQuery Script Format

XWQuery Script is a universal query language that supports 50 action types:

### Core Actions
- SELECT, INSERT, UPDATE, DELETE
- CREATE, ALTER, DROP
- MERGE, LOAD, STORE

### Query Operations
- WHERE, FILTER, OPTIONAL, UNION
- BETWEEN, LIKE, IN

### Advanced Operations
- MATCH, JOIN, WITH
- OUT, IN_TRAVERSE, PATH
- RETURN, PROJECT, EXTEND

### Aggregation & Analysis
- GROUP BY, HAVING, SUMMARIZE
- AGGREGATE, WINDOW
- DISTINCT, ORDER BY

### Data Manipulation
- SLICING, INDEXING
- FOREACH, LET, FOR

### Metadata Operations
- DESCRIBE, CONSTRUCT
- ASK, SUBSCRIBE, MUTATION

## Usage

### Running Conversion Tests

```bash
# Run all conversion tests
python -m pytest tests/core/test_sql_to_xwquery_file_conversion.py -v

# Run specific test
python -m pytest tests/core/test_sql_to_xwquery_file_conversion.py::TestSQLToXWQueryFileConversion::test_simple_query_conversion -v

# Run with detailed output
python -m pytest tests/core/test_sql_to_xwquery_file_conversion.py -v --tb=long
```

### Converting SQL Files Manually

```python
from pathlib import Path
from exonware.xwnode.strategies.queries.xwquery_strategy import XWQueryScriptStrategy

# Initialize strategy
xwquery_strategy = XWQueryScriptStrategy()

# Read SQL file
sql_content = Path("input.sql").read_text()

# Convert to XWQuery
xwquery_content = xwquery_strategy.parse_script(sql_content)

# Write XWQuery file
Path("output.xwquery").write_text(xwquery_content)
```

## Test Coverage

The test suite covers:

✅ **Basic Conversions**
- Simple SELECT queries
- INSERT, UPDATE, DELETE statements
- WHERE, ORDER BY, LIMIT clauses

✅ **Advanced SQL Features**
- Common Table Expressions (CTEs)
- JOINs (INNER, LEFT, RIGHT, FULL)
- Aggregation functions
- Window functions
- Subqueries

✅ **Edge Cases**
- Empty files
- Comments-only files
- Unicode characters
- Special characters
- Multiline formatting

✅ **Performance**
- Simple query performance (<100ms)
- Complex query performance (<1s)
- Batch conversion efficiency

✅ **Quality Assurance**
- Comment preservation
- Metadata handling
- Error handling
- File format validation

## Standards Compliance

This test follows DEV_GUIDELINES.md standards:

- ✅ **pytest usage**: All tests use pytest framework
- ✅ **Test organization**: Tests in core/ directory
- ✅ **File naming**: snake_case for all files
- ✅ **Documentation**: Comprehensive docs with WHY explanations
- ✅ **Production-grade**: Enterprise-ready test quality
- ✅ **Error handling**: Comprehensive error scenarios
- ✅ **Performance testing**: Performance benchmarks included

## Future Enhancements

### Phase 1: Enhanced Conversion
- Native XWQuery syntax generation
- Optimization hints preservation
- Query plan generation

### Phase 2: Multi-Format Support
- GraphQL to XWQuery
- Cypher to XWQuery
- SPARQL to XWQuery
- KQL to XWQuery

### Phase 3: Advanced Features
- Query optimization recommendations
- Performance analysis
- Security vulnerability detection
- Automatic migration suggestions

## References

- **XWQuery Script Documentation**: `xwnode/docs/XWQUERY_SCRIPT.md`
- **DEV_GUIDELINES.md**: Project development guidelines
- **Test Implementation**: `test_sql_to_xwquery_file_conversion.py`

---

*This documentation follows eXonware standards for production-grade quality and comprehensive coverage.*

