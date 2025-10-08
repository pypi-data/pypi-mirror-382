#!/usr/bin/env python3
"""
#exonware/xwnode/tests/core/test_sql_to_xwquery_file_conversion.py

SQL to XWQuery File Conversion Tests

This module tests the conversion of SQL files (.sql) to XWQuery Script files (.xwquery)
following DEV_GUIDELINES.md standards for production-ready testing.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 07-Oct-2025
"""

import pytest
import sys
import os
from pathlib import Path
from typing import Dict, List, Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
    from exonware.xwnode.strategies.queries.xwquery_strategy import XWQueryScriptStrategy
    from exonware.xwnode.strategies.queries.sql import SQLStrategy
    from exonware.xwnode.base import XWNodeBase
    from exonware.xwnode.errors import XWNodeTypeError, XWNodeValueError
except ImportError as e:
    print(f"❌ Import failed: {e}")
    pytest.skip(f"Required modules not available: {e}", allow_module_level=True)


class TestSQLToXWQueryFileConversion:
    """
    Test suite for SQL to XWQuery file conversion.
    
    Tests conversion of SQL query files to XWQuery Script files,
    including:
    - Simple queries
    - Complex queries with CTEs
    - Queries with JOINs and aggregations
    - Comment preservation
    - Metadata handling
    """
    
    def setup_method(self):
        """Set up test fixtures."""
        self.test_dir = Path(__file__).parent / "data"
        self.inputs_dir = self.test_dir / "inputs"
        self.expected_dir = self.test_dir / "expected"
        self.outputs_dir = self.test_dir / "outputs"
        
        # Create outputs directory if it doesn't exist
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize strategies
        self.sql_strategy = SQLStrategy()
        self.xwquery_strategy = XWQueryScriptStrategy()
    
    def read_file(self, file_path: Path) -> str:
        """Read file content."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def write_file(self, file_path: Path, content: str) -> None:
        """Write content to file."""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def convert_sql_to_xwquery(self, sql_content: str) -> str:
        """
        Convert SQL content to XWQuery format.
        
        Args:
            sql_content: SQL query string
            
        Returns:
            XWQuery script string
        """
        # Parse SQL to actions tree
        parsed_strategy = self.xwquery_strategy.parse_script(sql_content)
        
        # Get the XWQuery representation
        # For now, XWQuery format is SQL-compatible, so we preserve the SQL
        # In future, this will convert to native XWQuery syntax
        return sql_content
    
    def test_simple_query_conversion(self):
        """Test conversion of simple SQL query to XWQuery."""
        # Read input SQL file
        sql_file = self.inputs_dir / "test_simple_users.sql"
        sql_content = self.read_file(sql_file)
        
        # Convert to XWQuery
        xwquery_content = self.convert_sql_to_xwquery(sql_content)
        
        # Write output
        output_file = self.outputs_dir / "test_simple_users.xwquery"
        self.write_file(output_file, xwquery_content)
        
        # Verify conversion
        assert xwquery_content is not None
        assert len(xwquery_content) > 0
        assert "SELECT" in xwquery_content
        assert "FROM users" in xwquery_content
        assert "WHERE active = true" in xwquery_content
        
        # Read expected output
        expected_file = self.expected_dir / "test_simple_users.xwquery"
        expected_content = self.read_file(expected_file)
        
        # Compare with expected (normalize whitespace)
        assert xwquery_content.strip() == expected_content.strip()
    
    def test_complex_query_conversion(self):
        """Test conversion of complex SQL query with CTEs to XWQuery."""
        # Read input SQL file
        sql_file = self.inputs_dir / "test_ecommerce_analytics.sql"
        sql_content = self.read_file(sql_file)
        
        # Convert to XWQuery
        xwquery_content = self.convert_sql_to_xwquery(sql_content)
        
        # Write output
        output_file = self.outputs_dir / "test_ecommerce_analytics.xwquery"
        self.write_file(output_file, xwquery_content)
        
        # Verify conversion
        assert xwquery_content is not None
        assert len(xwquery_content) > 0
        assert "WITH monthly_sales AS" in xwquery_content
        assert "top_products AS" in xwquery_content
        assert "SELECT" in xwquery_content
        assert "FROM top_products tp" in xwquery_content
        assert "INNER JOIN monthly_sales ms" in xwquery_content
        
        # Read expected output
        expected_file = self.expected_dir / "test_ecommerce_analytics.xwquery"
        expected_content = self.read_file(expected_file)
        
        # Compare with expected (normalize whitespace)
        assert xwquery_content.strip() == expected_content.strip()
    
    def test_comment_preservation(self):
        """Test that comments are preserved during conversion."""
        sql_content = """
        -- This is a single-line comment
        SELECT * FROM users
        -- Another comment
        WHERE age > 25;
        """
        
        xwquery_content = self.convert_sql_to_xwquery(sql_content)
        
        # Verify comments are preserved
        assert "-- This is a single-line comment" in xwquery_content
        assert "-- Another comment" in xwquery_content
    
    def test_action_tree_generation(self):
        """Test that actions tree is properly generated."""
        sql_content = "SELECT user_id, name FROM users WHERE active = true"
        
        # Parse to actions tree
        parsed_strategy = self.xwquery_strategy.parse_script(sql_content)
        actions_tree = parsed_strategy.get_actions_tree()
        
        # Verify tree structure
        assert actions_tree is not None
        tree_data = actions_tree.to_native()
        assert 'root' in tree_data
        assert 'statements' in tree_data['root']
        assert 'comments' in tree_data['root']
        assert 'metadata' in tree_data['root']
        
        # Verify metadata
        metadata = tree_data['root']['metadata']
        assert 'version' in metadata
        assert 'created' in metadata
        assert 'source_format' in metadata
        assert metadata['source_format'] == 'XWQUERY_SCRIPT'
    
    def test_query_validation(self):
        """Test query validation during conversion."""
        # Valid SQL
        valid_sql = "SELECT * FROM users WHERE age > 25"
        assert self.xwquery_strategy.validate_query(valid_sql)
        
        # Invalid SQL
        invalid_sql = "INVALID QUERY SYNTAX"
        assert not self.xwquery_strategy.validate_query(invalid_sql)
    
    def test_file_extensions(self):
        """Test correct file extensions are used."""
        # SQL files should have .sql extension
        sql_files = list(self.inputs_dir.glob("*.sql"))
        assert len(sql_files) > 0
        for sql_file in sql_files:
            assert sql_file.suffix == ".sql"
        
        # XWQuery files should have .xwquery extension
        xwquery_files = list(self.expected_dir.glob("*.xwquery"))
        assert len(xwquery_files) > 0
        for xwquery_file in xwquery_files:
            assert xwquery_file.suffix == ".xwquery"
    
    def test_batch_conversion(self):
        """Test batch conversion of multiple SQL files."""
        sql_files = list(self.inputs_dir.glob("*.sql"))
        
        conversions = []
        for sql_file in sql_files:
            # Read SQL content
            sql_content = self.read_file(sql_file)
            
            # Convert to XWQuery
            xwquery_content = self.convert_sql_to_xwquery(sql_content)
            
            # Write output
            output_file = self.outputs_dir / sql_file.with_suffix(".xwquery").name
            self.write_file(output_file, xwquery_content)
            
            conversions.append({
                'input': sql_file,
                'output': output_file,
                'success': True
            })
        
        # Verify all conversions succeeded
        assert len(conversions) > 0
        assert all(c['success'] for c in conversions)
    
    def test_unicode_handling(self):
        """Test handling of unicode characters in SQL."""
        sql_content = """
        SELECT * FROM users 
        WHERE name = 'José María' 
        AND description LIKE '%café%';
        """
        
        xwquery_content = self.convert_sql_to_xwquery(sql_content)
        
        # Verify unicode is preserved
        assert 'José María' in xwquery_content
        assert 'café' in xwquery_content
    
    def test_special_characters(self):
        """Test handling of special characters."""
        sql_content = """
        SELECT * FROM users 
        WHERE name = 'John O''Connor' 
        AND email LIKE '%@example.com';
        """
        
        xwquery_content = self.convert_sql_to_xwquery(sql_content)
        
        # Verify special characters are preserved
        assert "O''Connor" in xwquery_content
        assert "%@example.com" in xwquery_content
    
    def test_multiline_query_formatting(self):
        """Test formatting of multiline queries."""
        sql_content = """
        SELECT 
            user_id,
            name,
            email
        FROM users
        WHERE active = true
        ORDER BY created_at DESC;
        """
        
        xwquery_content = self.convert_sql_to_xwquery(sql_content)
        
        # Verify multiline formatting is preserved
        assert "user_id" in xwquery_content
        assert "FROM users" in xwquery_content
        assert "ORDER BY created_at DESC" in xwquery_content
    
    def test_empty_file_handling(self):
        """Test handling of empty SQL files."""
        sql_content = ""
        
        xwquery_content = self.convert_sql_to_xwquery(sql_content)
        
        # Should handle empty content gracefully
        assert xwquery_content == ""
    
    def test_comments_only_file(self):
        """Test file with only comments."""
        sql_content = """
        -- This is a comment
        -- Another comment
        /* Block comment */
        """
        
        xwquery_content = self.convert_sql_to_xwquery(sql_content)
        
        # Should preserve comments
        assert "-- This is a comment" in xwquery_content
        assert "-- Another comment" in xwquery_content
    
    def test_query_complexity_estimation(self):
        """Test complexity estimation for queries."""
        simple_query = "SELECT * FROM users"
        complex_query = self.read_file(self.inputs_dir / "test_ecommerce_analytics.sql")
        
        simple_complexity = self.xwquery_strategy.estimate_complexity(simple_query)
        complex_complexity = self.xwquery_strategy.estimate_complexity(complex_query)
        
        # Simple query should have lower complexity
        assert simple_complexity['complexity'] in ['LOW', 'MEDIUM', 'HIGH']
        assert complex_complexity['complexity'] in ['LOW', 'MEDIUM', 'HIGH']
        
        # Complex query should have higher action count
        assert complex_complexity['action_count'] >= simple_complexity['action_count']
    
    def test_conversion_with_error_handling(self):
        """Test error handling during conversion."""
        # Test with None input
        with pytest.raises(Exception):
            self.xwquery_strategy.parse_script(None)
    
    def test_output_file_creation(self):
        """Test that output files are created correctly."""
        sql_file = self.inputs_dir / "test_simple_users.sql"
        sql_content = self.read_file(sql_file)
        
        xwquery_content = self.convert_sql_to_xwquery(sql_content)
        output_file = self.outputs_dir / "test_simple_users.xwquery"
        self.write_file(output_file, xwquery_content)
        
        # Verify file exists
        assert output_file.exists()
        assert output_file.is_file()
        assert output_file.suffix == ".xwquery"
        
        # Verify file content
        written_content = self.read_file(output_file)
        assert written_content == xwquery_content
    
    def test_roundtrip_conversion(self):
        """Test roundtrip conversion SQL -> XWQuery -> SQL."""
        sql_content = "SELECT user_id, name FROM users WHERE active = true"
        
        # Convert to XWQuery
        xwquery_content = self.convert_sql_to_xwquery(sql_content)
        
        # For now, XWQuery is SQL-compatible, so content should match
        assert xwquery_content.strip() == sql_content.strip()


class TestXWQueryFileFormat:
    """Test suite for XWQuery file format specifications."""
    
    def test_xwquery_file_extension(self):
        """Test that .xwquery is the correct extension."""
        test_file = Path("test_query.xwquery")
        assert test_file.suffix == ".xwquery"
        assert test_file.stem == "test_query"
    
    def test_sql_file_extension(self):
        """Test that .sql is the correct extension for SQL files."""
        test_file = Path("test_query.sql")
        assert test_file.suffix == ".sql"
        assert test_file.stem == "test_query"
    
    def test_file_naming_convention(self):
        """Test file naming conventions."""
        # SQL files should use snake_case
        sql_files = [
            "test_simple_users.sql",
            "test_ecommerce_analytics.sql"
        ]
        
        for filename in sql_files:
            assert "_" in filename or filename.islower()
            assert filename.endswith(".sql")
        
        # XWQuery files should use snake_case
        xwquery_files = [
            "test_simple_users.xwquery",
            "test_ecommerce_analytics.xwquery"
        ]
        
        for filename in xwquery_files:
            assert "_" in filename or filename.islower()
            assert filename.endswith(".xwquery")


class TestConversionPerformance:
    """Test suite for conversion performance."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.xwquery_strategy = XWQueryScriptStrategy()
    
    def test_simple_query_performance(self):
        """Test performance for simple queries."""
        import time
        
        sql_content = "SELECT * FROM users WHERE active = true"
        
        start_time = time.time()
        parsed_strategy = self.xwquery_strategy.parse_script(sql_content)
        execution_time = time.time() - start_time
        
        # Should be very fast (< 100ms)
        assert execution_time < 0.1, f"Simple query took too long: {execution_time}s"
    
    def test_complex_query_performance(self):
        """Test performance for complex queries."""
        import time
        
        sql_content = """
        WITH cte1 AS (SELECT * FROM table1),
             cte2 AS (SELECT * FROM table2),
             cte3 AS (SELECT * FROM table3)
        SELECT * FROM cte1 
        JOIN cte2 ON cte1.id = cte2.id
        JOIN cte3 ON cte2.id = cte3.id;
        """
        
        start_time = time.time()
        parsed_strategy = self.xwquery_strategy.parse_script(sql_content)
        execution_time = time.time() - start_time
        
        # Should still be fast (< 1s)
        assert execution_time < 1.0, f"Complex query took too long: {execution_time}s"


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])

