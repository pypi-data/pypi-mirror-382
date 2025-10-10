#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path
from .core import MindMap, MindMapFactory, xray
from .exporters import save_mind_map
from .styles import get_theme

def main():
    parser = argparse.ArgumentParser(description="X-ray data structures as ASCII mind maps")
    parser.add_argument('input', nargs='?', help='Input file, URL, or JSON string')
    parser.add_argument('--style', choices=['tree', 'minimal', 'arrow', 'boxed'], 
                       default='tree', help='Visualization style')
    parser.add_argument('--theme', choices=['default', 'professional', 'colorful', 'emoji'],
                       default='default', help='Icon theme')
    parser.add_argument('--output', '-o', help='Output file')
    parser.add_argument('--format', choices=['txt', 'md', 'html', 'json'], 
                       default='txt', help='Output format')
    parser.add_argument('--search', '-s', help='Search and highlight text')
    parser.add_argument('--show-types', action='store_true', help='Show data types')
    parser.add_argument('--show-memory', action='store_true', help='Show memory usage')
    parser.add_argument('--no-icons', action='store_true', help='Hide icons')
    
    args = parser.parse_args()
    
    try:
        # Get input data
        if args.input:
            if args.input.startswith('http'):
                mind_map = MindMapFactory.from_url(args.input)
            elif Path(args.input).exists():
                mind_map = MindMapFactory.from_file(args.input)
            else:
                # Try to parse as JSON string
                mind_map = MindMapFactory.from_json(args.input)
        else:
            # Read from stdin
            data = json.loads(sys.stdin.read())
            mind_map = MindMap(data)
        
        # Apply configuration
        mind_map.show_icons = not args.no_icons
        mind_map.show_types = args.show_types
        mind_map.show_memory = args.show_memory
        mind_map.style = args.style
        mind_map.theme = get_theme(args.theme)
        
        # Apply search if requested
        if args.search:
            mind_map.search(args.search)
        
        # Output result
        if args.output:
            save_mind_map(mind_map, args.output, args.format)
            print(f"Mind map saved to {args.output}")
        else:
            print(mind_map.render())
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()