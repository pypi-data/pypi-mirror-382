#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path
from .core import MindMap, MindMapFactory, xray
from .exporters import save_mind_map
from .styles import get_theme

def friendly_error(message, hint=None):
    """Display user-friendly error messages"""
    print(f"❌ Error: {message}", file=sys.stderr)
    if hint:
        print(f"💡 Hint: {hint}", file=sys.stderr)
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="X-ray data structures as ASCII mind maps",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  mxray '{"name": "John", "age": 30}'
  mxray data.json --style minimal --theme professional
  mxray https://api.github.com/users/octocat --show-types
  echo '{"test": "data"}' | mxray --output result.html --format html

For more examples, visit: https://github.com/GxDrogers/mxray/wiki/Examples-Gallery
        """
    )
    
    parser.add_argument('input', nargs='?', help='Input file, URL, or JSON string')
    parser.add_argument('--style', '-s', choices=['tree', 'minimal', 'arrow', 'boxed'], 
                       default='tree', help='Visualization style (default: tree)')
    parser.add_argument('--theme', '-t', choices=['default', 'professional', 'colorful', 'emoji'],
                       default='default', help='Icon theme (default: default)')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--format', '-f', choices=['txt', 'md', 'html', 'json'], 
                       default='txt', help='Output format (default: txt)')
    parser.add_argument('--search', help='Search and highlight text')
    parser.add_argument('--show-types', action='store_true', help='Show data types')
    parser.add_argument('--show-memory', action='store_true', help='Show memory usage')
    parser.add_argument('--no-icons', action='store_true', help='Hide icons')
    parser.add_argument('--max-depth', type=int, default=10, help='Maximum depth to display (default: 10)')
    parser.add_argument('--truncate-strings', type=int, default=50, help='Max string length before truncation (default: 50)')
    
    args = parser.parse_args()
    
    try:
        # Get input data
        input_data = None
        
        if args.input:
            if args.input.startswith('http'):
                try:
                    mind_map = MindMapFactory.from_url(args.input)
                except Exception as e:
                    friendly_error(
                        f"Failed to fetch URL: {e}",
                        "Check the URL and your internet connection"
                    )
            elif Path(args.input).exists():
                try:
                    mind_map = MindMapFactory.from_file(args.input)
                except json.JSONDecodeError as e:
                    friendly_error(
                        f"Invalid JSON in file: {e}",
                        "Make sure the file contains valid JSON"
                    )
                except Exception as e:
                    friendly_error(
                        f"Failed to read file: {e}",
                        "Check file permissions and format"
                    )
            else:
                # Try to parse as JSON string
                try:
                    mind_map = MindMapFactory.from_json(args.input)
                except json.JSONDecodeError as e:
                    friendly_error(
                        f"Invalid JSON string: {e}",
                        "Make sure you're using valid JSON syntax"
                    )
        else:
            # Read from stdin
            if sys.stdin.isatty():
                friendly_error(
                    "No input provided",
                    "Provide JSON via file, URL, string, or stdin. Use --help for examples."
                )
            try:
                stdin_data = sys.stdin.read().strip()
                if not stdin_data:
                    friendly_error(
                        "Empty input from stdin",
                        "Provide JSON data via stdin or use file/URL input"
                    )
                data = json.loads(stdin_data)
                mind_map = MindMap(data)
            except json.JSONDecodeError as e:
                friendly_error(
                    f"Invalid JSON from stdin: {e}",
                    "Check your input data format"
                )
        
        # Apply configuration
        mind_map.show_icons = not args.no_icons
        mind_map.show_types = args.show_types
        mind_map.show_memory = args.show_memory
        mind_map.style = args.style
        mind_map.theme = get_theme(args.theme)
        mind_map.max_depth = args.max_depth
        mind_map.max_string_length = args.truncate_strings
        
        # Apply search if requested
        if args.search:
            mind_map.search(args.search)
        
        # Output result
        if args.output:
            try:
                save_mind_map(mind_map, args.output, args.format)
                print(f"✅ Mind map saved to {args.output}")
            except Exception as e:
                friendly_error(
                    f"Failed to save file: {e}",
                    "Check file path and permissions"
                )
        else:
            print(mind_map.render())
            
    except KeyboardInterrupt:
        print("\n⏹️  Operation cancelled by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        friendly_error(
            f"Unexpected error: {e}",
            "Report this issue at: https://github.com/GxDrogers/mxray/issues"
        )

if __name__ == "__main__":
    main()