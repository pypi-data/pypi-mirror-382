#!/usr/bin/env python3
"""
Transducer module for parsing database schemas and mappings using rapt.

This module reads and parses three files:
- source.txt: Source database schema (Person_URA) with constraints
- target.txt: Target database schema (normalized tables) with constraints  
- mappings.txt: Transformation mappings between source and target schemas
"""

import os
from pprint import pprint
from typing import Dict, List, Any

from src.rapt2.rapt import Rapt


class Transducer:
    """A transducer for parsing database schemas and mappings using rapt."""
    
    def __init__(self):
        """
        Initialize the transducer with a specific grammar.
        
        Args:
            grammar: The grammar to use for parsing (default: "Dependency Grammar")
        """
        self.rapt = Rapt(grammar="Dependency Grammar")
        self.source_schema = {}
        self.target_schema = {}
        self.mappings = []
        
    def read_file(self, filepath: str) -> str:
        """Read a file and return its contents."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except FileNotFoundError:
            print(f"Error: File {filepath} not found")
            return ""
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return ""
    
    def parse_schema_definition(self, content: str) -> Dict[str, List[str]]:
        """
        Parse schema definitions from content.
        Extracts relation names and their attributes from lines like:
        Person(ssn, name)
        """
        schema = {}
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            # Handle different formats
            if '(' in line and ')' in line:  # Standard format
                rel_name = line.split('(')[0].strip()
                attrs_str = line.split('(')[1].split(')')[0].strip()
            else:
                continue
                
            if attrs_str:
                # Parse attributes, handling both comma and space separation
                attrs = [attr.strip() for attr in attrs_str.replace(',', ' ').split()]
                schema[rel_name] = attrs
                
        return schema
    
    def parse_source_schema(self, filepath: str = "source.txt") -> Dict[str, Any]:
        """Parse the source database schema and constraints."""
        print(f"Parsing source schema from {filepath}...")
        content = self.read_file(filepath)
        if not content:
            return {}
            
        # Extract schema definition
        self.source_schema = self.parse_schema_definition(content)
        
        # Parse constraints using rapt
        constraints = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or '∶' in line or '(' in line and ')' in line and '∶' not in line:
                continue
                
            try:
                # Parse constraint using rapt
                parsed = self.rapt.to_syntax_tree(line, self.source_schema)
                constraints.append({
                    'original': line,
                    'parsed': parsed
                })
            except Exception as e:
                print(f"Warning: Could not parse constraint '{line}': {e}")
                constraints.append({
                    'original': line,
                    'parsed': None,
                    'error': str(e)
                })
        
        return {
            'schema': self.source_schema,
            'constraints': constraints
        }
    
    def parse_target_schema(self, filepath: str = "target.txt") -> Dict[str, Any]:
        """Parse the target database schema and constraints."""
        print(f"Parsing target schema from {filepath}...")
        content = self.read_file(filepath)
        if not content:
            return {}
            
        # Extract schema definitions
        self.target_schema = self.parse_schema_definition(content)
        
        # Parse constraints using rapt
        constraints = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or '(' in line and ')' in line:
                continue
                
            try:
                # Parse constraint using rapt
                parsed = self.rapt.to_syntax_tree(line, self.target_schema)
                constraints.append({
                    'original': line,
                    'parsed': parsed
                })
            except Exception as e:
                print(f"Warning: Could not parse constraint '{line}': {e}")
                constraints.append({
                    'original': line,
                    'parsed': None,
                    'error': str(e)
                })
        
        return {
            'schema': self.target_schema,
            'constraints': constraints
        }
    
    def parse_mappings(self, filepath: str = "mappings.txt") -> List[Dict[str, Any]]:
        """Parse the transformation mappings."""
        print(f"Parsing mappings from {filepath}...")
        content = self.read_file(filepath)
        if not content:
            return []
            
        mappings = []
        lines = content.split('\n')
        
        # Combine source and target schemas for parsing
        combined_schema = {**self.source_schema, **self.target_schema}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            try:
                # Parse mapping using rapt
                parsed = self.rapt.to_syntax_tree(line, combined_schema)
                mappings.append({
                    'original': line,
                    'parsed': parsed
                })
            except Exception as e:
                print(f"Warning: Could not parse mapping '{line}': {e}")
                mappings.append({
                    'original': line,
                    'parsed': None,
                    'error': str(e)
                })
        
        self.mappings = mappings
        return mappings
    
    def parse_all(self, source_file: str = "source.txt", 
                  target_file: str = "target.txt", 
                  mappings_file: str = "mappings.txt") -> Dict[str, Any]:
        """Parse all three files and return combined results."""
        print("Parsing all transducer files...")
        
        source_data = self.parse_source_schema(source_file)
        target_data = self.parse_target_schema(target_file)
        mappings_data = self.parse_mappings(mappings_file)
        
        return {
            'source': source_data,
            'target': target_data,
            'mappings': mappings_data
        }
    
    def print_summary(self, data: Dict[str, Any]):
        """Print a summary of the parsed data."""
        print("\n" + "="*60)
        print("TRANSDUCER PARSING SUMMARY")
        print("="*60)
        
        # Source schema
        print(f"\nSOURCE SCHEMA:")
        print(f"  Relations: {list(data['source']['schema'].keys())}")
        for rel, attrs in data['source']['schema'].items():
            print(f"    {rel}: {attrs}")
        
        print(f"  Constraints: {len(data['source']['constraints'])}")
        for constraint in data['source']['constraints']:
            status = "✓" if constraint['parsed'] else "✗"
            print(f"    {status} {constraint['original']}")
            if 'error' in constraint:
                print(f"      Error: {constraint['error']}")
        
        # Target schema
        print(f"\nTARGET SCHEMA:")
        print(f"  Relations: {list(data['target']['schema'].keys())}")
        for rel, attrs in data['target']['schema'].items():
            print(f"    {rel}: {attrs}")
        
        print(f"  Constraints: {len(data['target']['constraints'])}")
        for constraint in data['target']['constraints']:
            status = "✓" if constraint['parsed'] else "✗"
            print(f"    {status} {constraint['original']}")
            if 'error' in constraint:
                print(f"      Error: {constraint['error']}")
        
        # Mappings
        print(f"\nMAPPINGS:")
        print(f"  Count: {len(data['mappings'])}")
        for mapping in data['mappings']:
            status = "✓" if mapping['parsed'] else "✗"
            print(f"    {status} {mapping['original']}")
            if 'error' in mapping:
                print(f"      Error: {mapping['error']}")
    
    def to_sql(self, content: str, schema: Dict[str, List[str]]) -> str:
        """Convert rapt content to SQL using the provided schema."""
        try:
            return self.rapt.to_sql(content, schema)
        except Exception as e:
            return f"Error converting to SQL: {e}"


def main():
    """Main function to demonstrate the transducer."""
    transducer = Transducer()
    
    # Parse all files
    data = transducer.parse_all()
    
    # Print summary
    transducer.print_summary(data)
    
    # Demonstrate SQL conversion for mappings
    print(f"\n" + "="*60)
    print("SQL CONVERSION EXAMPLES")
    print("="*60)
    
    combined_schema = {**data['source']['schema'], **data['target']['schema']}
    
    for mapping in data['mappings']:
        if mapping['parsed']:
            print(f"\nMapping: {mapping['original']}")
            sql = transducer.to_sql(mapping['original'], combined_schema)
            print(f"SQL: {sql}")


if __name__ == "__main__":
    main()
