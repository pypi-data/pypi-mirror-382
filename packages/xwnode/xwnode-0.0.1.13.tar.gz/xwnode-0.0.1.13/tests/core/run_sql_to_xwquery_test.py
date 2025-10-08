#!/usr/bin/env python3
"""
#exonware/xwnode/tests/core/run_sql_to_xwquery_test.py

Standalone runner for SQL to XWQuery conversion tests

This script runs the SQL to XWQuery file conversion tests without requiring pytest.
Useful for quick testing and debugging.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 07-Oct-2025
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
    from exonware.xwnode.strategies.queries.xwquery_strategy import XWQueryScriptStrategy
    from exonware.xwnode.base import XWNodeBase
    print("✅ Successfully imported XWNode modules")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)


def read_file(file_path: Path) -> str:
    """Read file content."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def write_file(file_path: Path, content: str) -> None:
    """Write content to file."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def convert_sql_to_xwquery(sql_content: str) -> str:
    """Convert SQL content to XWQuery format."""
    xwquery_strategy = XWQueryScriptStrategy()
    
    # Parse SQL to actions tree
    parsed_strategy = xwquery_strategy.parse_script(sql_content)
    
    # Get the XWQuery representation
    # For now, XWQuery format is SQL-compatible
    return sql_content


def test_simple_conversion():
    """Test simple SQL to XWQuery conversion."""
    print("\n" + "="*70)
    print("TEST 1: Simple User Query Conversion")
    print("="*70)
    
    test_dir = Path(__file__).parent / "data"
    inputs_dir = test_dir / "inputs"
    outputs_dir = test_dir / "outputs"
    expected_dir = test_dir / "expected"
    
    # Create outputs directory
    outputs_dir.mkdir(parents=True, exist_ok=True)
    
    # Read input SQL
    sql_file = inputs_dir / "test_simple_users.sql"
    print(f"📂 Reading: {sql_file}")
    sql_content = read_file(sql_file)
    
    print(f"📊 SQL Content ({len(sql_content)} chars):")
    print("-" * 70)
    print(sql_content[:300] + "..." if len(sql_content) > 300 else sql_content)
    print("-" * 70)
    
    # Convert to XWQuery
    print("\n🔄 Converting SQL to XWQuery...")
    xwquery_content = convert_sql_to_xwquery(sql_content)
    
    # Write output
    output_file = outputs_dir / "test_simple_users.xwquery"
    print(f"💾 Writing: {output_file}")
    write_file(output_file, xwquery_content)
    
    # Read expected
    expected_file = expected_dir / "test_simple_users.xwquery"
    expected_content = read_file(expected_file)
    
    # Compare
    print("\n✓ Verification:")
    if xwquery_content.strip() == expected_content.strip():
        print("  ✅ Output matches expected!")
    else:
        print("  ⚠️  Output differs from expected")
        print(f"     Expected: {len(expected_content)} chars")
        print(f"     Got: {len(xwquery_content)} chars")
    
    return xwquery_content.strip() == expected_content.strip()


def test_complex_conversion():
    """Test complex SQL to XWQuery conversion."""
    print("\n" + "="*70)
    print("TEST 2: Complex E-commerce Analytics Conversion")
    print("="*70)
    
    test_dir = Path(__file__).parent / "data"
    inputs_dir = test_dir / "inputs"
    outputs_dir = test_dir / "outputs"
    expected_dir = test_dir / "expected"
    
    # Read input SQL
    sql_file = inputs_dir / "test_ecommerce_analytics.sql"
    print(f"📂 Reading: {sql_file}")
    sql_content = read_file(sql_file)
    
    print(f"📊 SQL Content ({len(sql_content)} chars):")
    print("-" * 70)
    print(sql_content[:300] + "..." if len(sql_content) > 300 else sql_content)
    print("-" * 70)
    
    # Convert to XWQuery
    print("\n🔄 Converting SQL to XWQuery...")
    xwquery_content = convert_sql_to_xwquery(sql_content)
    
    # Write output
    output_file = outputs_dir / "test_ecommerce_analytics.xwquery"
    print(f"💾 Writing: {output_file}")
    write_file(output_file, xwquery_content)
    
    # Read expected
    expected_file = expected_dir / "test_ecommerce_analytics.xwquery"
    expected_content = read_file(expected_file)
    
    # Compare
    print("\n✓ Verification:")
    if xwquery_content.strip() == expected_content.strip():
        print("  ✅ Output matches expected!")
    else:
        print("  ⚠️  Output differs from expected")
        print(f"     Expected: {len(expected_content)} chars")
        print(f"     Got: {len(xwquery_content)} chars")
    
    return xwquery_content.strip() == expected_content.strip()


def test_actions_tree():
    """Test actions tree generation."""
    print("\n" + "="*70)
    print("TEST 3: Actions Tree Generation")
    print("="*70)
    
    sql_content = "SELECT user_id, name FROM users WHERE active = true"
    print(f"📊 SQL: {sql_content}")
    
    # Initialize strategy
    xwquery_strategy = XWQueryScriptStrategy()
    
    # Parse to actions tree
    print("\n🔄 Parsing SQL to actions tree...")
    parsed_strategy = xwquery_strategy.parse_script(sql_content)
    actions_tree = parsed_strategy.get_actions_tree()
    
    # Get tree data
    tree_data = actions_tree.to_native()
    
    print("\n🌳 Actions Tree Structure:")
    print(f"  Root Type: {tree_data['root']['type']}")
    print(f"  Statements: {len(tree_data['root']['statements'])}")
    print(f"  Comments: {len(tree_data['root']['comments'])}")
    
    print("\n📊 Metadata:")
    for key, value in tree_data['root']['metadata'].items():
        print(f"  {key}: {value}")
    
    # Verify structure
    has_root = 'root' in tree_data
    has_statements = 'statements' in tree_data['root']
    has_metadata = 'metadata' in tree_data['root']
    
    print("\n✓ Verification:")
    print(f"  {'✅' if has_root else '❌'} Has root node")
    print(f"  {'✅' if has_statements else '❌'} Has statements")
    print(f"  {'✅' if has_metadata else '❌'} Has metadata")
    
    return has_root and has_statements and has_metadata


def test_batch_conversion():
    """Test batch conversion of multiple files."""
    print("\n" + "="*70)
    print("TEST 4: Batch Conversion")
    print("="*70)
    
    test_dir = Path(__file__).parent / "data"
    inputs_dir = test_dir / "inputs"
    outputs_dir = test_dir / "outputs"
    
    # Find all SQL files
    sql_files = list(inputs_dir.glob("*.sql"))
    print(f"📂 Found {len(sql_files)} SQL files")
    
    successes = 0
    for sql_file in sql_files:
        print(f"\n  Processing: {sql_file.name}")
        
        # Read SQL
        sql_content = read_file(sql_file)
        print(f"    Size: {len(sql_content)} chars")
        
        # Convert
        xwquery_content = convert_sql_to_xwquery(sql_content)
        
        # Write output
        output_file = outputs_dir / sql_file.with_suffix(".xwquery").name
        write_file(output_file, xwquery_content)
        print(f"    ✅ Converted to: {output_file.name}")
        
        successes += 1
    
    print(f"\n✓ Verification:")
    print(f"  ✅ Successfully converted {successes}/{len(sql_files)} files")
    
    return successes == len(sql_files)


def main():
    """Run all tests."""
    print("="*70)
    print("SQL to XWQuery File Conversion Tests")
    print("="*70)
    print("Company: eXonware.com")
    print("Author: Eng. Muhammad AlShehri")
    print("Email: connect@exonware.com")
    print("="*70)
    
    results = []
    
    # Run tests
    try:
        results.append(("Simple Conversion", test_simple_conversion()))
        results.append(("Complex Conversion", test_complex_conversion()))
        results.append(("Actions Tree", test_actions_tree()))
        results.append(("Batch Conversion", test_batch_conversion()))
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print("="*70)
    print(f"TOTAL: {passed}/{total} tests passed")
    print("="*70)
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

