<p align="center">
  <img src="images/logo.svg" alt="MXRay Logo" width="150">
</p>

<h1 align="center">🔍 MXRay</h1>
<p align="center">
  <strong>X-ray vision for your Python data structures</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/mxray/">
    <img src="https://img.shields.io/pypi/v/mxray.svg" alt="PyPI version">
  </a>
  <a href="https://pypi.org/project/mxray/">
    <img src="https://img.shields.io/pypi/pyversions/mxray.svg" alt="Python versions">
  </a>
  <a href="https://github.com/GxDrogers/mxray/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
  </a>
  <a href="https://github.com/GxDrogers/mxray/stargazers">
    <img src="https://img.shields.io/github/stars/GxDrogers/mxray.svg" alt="GitHub stars">
  </a>
</p>

<p align="center">
  <i>See through complex nested data structures with beautiful ASCII mind maps and trees</i>
</p>

---

## 🚀 Quick Install

    ```bash
    pip install mxray

## 💡 Instant Insight
    from mxray import xray
    
    data = {
        'project': 'MXRay',
        'creator': 'Midhun Haridas',
        'features': ['smart_icons', 'multiple_styles', 'exporters'],
        'config': {
            'debug': True,
            'max_depth': 5
        }
    }
    
    xray(data)

## 📊 Output
    📦 root
    ├── 🚀 project: 'MXRay'
    ├── 👨💻 creator: 'Midhun Haridas'
    ├── ✨ features
    │   ├── 🧠 smart_icons
    │   ├── 🎨 multiple_styles
    │   └── 💾 exporters
    └── ⚙️ config
        ├── 🐛 debug: True
        └── 📏 max_depth: 5

## 📖 Table of Contents
  Why MXRay?

  Quick Start


  Core Features

  Usage Examples

  Advanced Features

  Command Line Interface

  API Reference

  Installation

  Contributing

  License
  
  Support

## ❓ Why MXRay?

### The Problem
    import json
    print(json.dumps(complex_data, indent=2))
    # Output: Hundreds of lines of nested braces and brackets
    # 😵 Hard to understand structure
    # 🔍 Difficult to find specific data
    # 📏 No visual hierarchy

### The Solution
    from mxray import xray
    xray(complex_data)
    # Output: Beautiful, intuitive ASCII mind map
    # 🎯 Instant understanding of data structure
    # 🔗 Clear parent-child relationships
    # 🎨 Visual hierarchy with smart icons

## 🏁 Quick Start

### Basic Usage
    from mxray import xray
    
    # One-liner magic
    xray(your_data)
    
    # Or with more control
    from mxray import MindMap
    mind_map = MindMap(your_data)
    print(mind_map)

### From Various Sources
    from mxray import MindMapFactory
    
    # From JSON string
    mind_map = MindMapFactory.from_json('{"name": "Midhun", "project": "MXRay"}')
    
    # From file
    mind_map = MindMapFactory.from_file('data.json')
    
    # From URL
    mind_map = MindMapFactory.from_url('https://api.github.com/users/MidhunHaridas')
    
    # From API response
    import requests
    response = requests.get('https://api.example.com/data')
    xray(response.json())

## ✨ Core Features

### 🎨 Multiple Visualization Styles
    from mxray import Styles
    
    data = {'api': {'users': [], 'settings': {}}}
    
    xray(data, style=Styles.TREE)      # Default tree style
    xray(data, style=Styles.MINIMAL)   # Clean minimal style
    xray(data, style=Styles.ARROW)     # Arrow connectors
    xray(data, style=Styles.BOXED)     # Boxed sections

### 🔍 Smart Search & Highlight
    from mxray import MindMap
    
    mind_map = MindMap(complex_data)
    mind_map.search("Midhun")  # Highlights all occurrences
    print(mind_map)

## 📊 Data Type & Memory Insights
    xray(data, show_types=True, show_memory=True)  

### Output
    📦 root (dict) [240 bytes]
    ├── 👤 user (dict) [48 bytes]
    │   ├── 📛 name: 'Midhun' (str) [54 bytes]
    │   └── 🔢 age: 25 (int) [28 bytes]

## 🎭 Beautiful Themes
    from mxray import Themes
    
    xray(data, theme=Themes.PROFESSIONAL)  # Clean business icons
    xray(data, theme=Themes.COLORFUL)      # Vibrant colorful icons
    xray(data, theme=Themes.EMOJI)         # Fun emoji icons (default)

## 💾 Multiple Export Formats
    from mxray import save_mind_map
    
    mind_map = MindMap(data)
    save_mind_map(mind_map, "structure.md")    # Markdown
    save_mind_map(mind_map, "structure.html")  # Interactive HTML
    save_mind_map(mind_map, "structure.json")  # JSON structure


## 🛠️ Usage Examples

### API Response Analysis
    import requests
    from mxray import xray
    
    # Analyze GitHub API response
    response = requests.get('https://api.github.com/users/MidhunHaridas')
    xray(response.json(), show_types=True)

### Configuration File Inspection
    import yaml
    from mxray import xray
    
    with open('config.yaml') as f:
        config = yaml.safe_load(f)
        
    xray(config, style="minimal", show_memory=True)

### Database Schema Visualization
    from mxray import xray
    from my_app import models
    
    # Visualize Django model structure
    xray(models.User.__dict__)

### Real-time Data Monitoring
    from mxray import MindMap
    import time
    
    class DataMonitor:
        def __init__(self):
            self.previous_map = None
        
        def monitor(self, data_source):
            while True:
                current_data = data_source.get_data()
                current_map = MindMap(current_data)
                
                if current_map != self.previous_map:
                    print("\033[2J\033[H")  # Clear terminal
                    print(current_map)
                    self.previous_map = current_map
                
                time.sleep(1)

## 🔬 Advanced Features

### Focus on Specific Paths
    # Zoom into specific data branches
    xray(complex_data).focus_on("users[0].profile.settings")

### Custom Filtering
    from mxray import MindMap
    
    mind_map = MindMap(data)
    
    # Show only nodes with string values
    filtered = mind_map.filter(lambda node: isinstance(node.value, str))
    
    # Show only nodes with more than 2 children
    complex_nodes = mind_map.filter(lambda node: len(node.children) > 2)

### Custom Themes
    custom_theme = {
        "name": "midhun_theme",
        "icons": {
            "user": "👨💻",
            "email": "📨",
            "api_key": "🔑",
            "created_at": "🕒",
            "dict": "🗂️",
            "list": "📜"
        }
    }
    
    xray(data, theme=custom_theme)

### Interactive Exploration
    from mxray import MindMap
    
    # Explore large data structures interactively
    mind_map = MindMap(huge_json_data)
    mind_map.explore()  # Opens interactive terminal browser

## Command Line Interface

### Basic Usage
    # From JSON file
    mxray data.json
    
    # From URL
    mxray https://api.github.com/users/MidhunHaridas
    
    # From JSON string
    mxray '{"name": "Midhun", "project": "MXRay"}'
    
    # From stdin
    echo '{"test": "data"}' | mxray

### Advanced CLI Options
    # Different visualization styles
    mxray data.json --style minimal
    mxray data.json --style arrow
    
    # Show additional information
    mxray data.json --show-types --show-memory
    
    # Search and highlight
    mxray data.json --search "Midhun"
    
    # Custom theme
    mxray data.json --theme professional
    
    # Export to file
    mxray data.json --output structure.html --format html
    mxray data.json --output structure.md --format md


### Full CLI Reference
    mxray --help
    
    usage: mxray [-h] [--style {tree,minimal,arrow,boxed}] 
                 [--theme {default,professional,colorful,emoji}]
                 [--output OUTPUT] [--format {txt,md,html,json}] 
                 [--search SEARCH] [--show-types] [--show-memory] [--no-icons]
                 [input]
    
    X-ray data structures as ASCII mind maps
    
    positional arguments:
      input                 Input file, URL, or JSON string
    
    options:
      -h, --help            show this help message and exit
      --style {tree,minimal,arrow,boxed}
                            Visualization style
      --theme {default,professional,colorful,emoji}
                            Icon theme
      --output OUTPUT, -o OUTPUT
                            Output file
      --format {txt,md,html,json}
                            Output format
      --search SEARCH, -s SEARCH
                            Search and highlight text
      --show-types          Show data types
      --show-memory         Show memory usage
      --no-icons            Hide icons

  
## 📚 API Reference
    Main Functions
    xray(data, **kwargs)

  The main one-liner function for instant visualization.

  Parameters:

    data: Any Python data structure (dict, list, etc.)
  
    style: Visualization style ('tree', 'minimal', 'arrow', 'boxed')
  
    show_icons: Boolean to enable/disable icons (default: True)
  
    show_types: Boolean to show data types (default: False)
  
    show_memory: Boolean to show memory usage (default: False)
  
    theme: Icon theme ('default', 'professional', 'colorful', 'emoji')
  
    max_depth: Maximum depth to visualize (default: None)

    MindMap(data, **kwargs)

  The main class for advanced usage.

  Methods:
  
    .render(): Returns the mind map as string
  
    .search(query): Highlights nodes matching query
  
    .filter(predicate): Filters nodes based on function
  
    .focus_on(path): Zooms into specific data path
  
    .explore(): Interactive exploration (future)

### Factory Methods

  MindMapFactory

    .from_json(json_str): Create from JSON string
  
    .from_file(file_path): Create from file
  
    .from_url(url): Create from URL (requires requests)

### Export Functions
    save_mind_map(mind_map, file_path, format='auto')
    
    Save mind map to various formats.

Formats:

    txt: Plain text (default)
  
    md: Markdown with code blocks
  
    html: Interactive HTML
  
    json: JSON structure

## 📦 Installation

### From PyPI (Recommended)
    pip install mxray

### From Source
    git clone https://github.com/GxDrogers/mxray.git
    cd mxray
    pip install -e .

### For Development
    git clone https://github.com/GxDrogers/mxray.git
    cd mxray
    pip install -e ".[dev]"
    pytest tests/ -v

### Dependencies
  Python 3.7+

  Optional: requests for URL support

## 🤝 Contributing

We love contributions! Here's how you can help:
Reporting Issues

  Check existing issues

  Create new issue with detailed description

### Feature Requests

  Suggest new features via issues

  Discuss implementation approach

### Code Contributions

  Fork the repository

  Create feature branch: git checkout -b feature/amazing-feature

  Commit changes: git commit -m 'Add amazing feature'

  Push to branch: git push origin feature/amazing-feature

  Open Pull Request

## Development Setup
    git clone https://github.com/GxDrogers/mxray.git
    cd mxray
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    pip install -e ".[dev]"
    pre-commit install

## Running Tests
    pytest tests/ -v
    pytest tests/ --cov=mxray --cov-report=html

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

## 👨💻 Author

Midhun Haridas

📧 Email: midhunharidas0@gmail.com

💻 GitHub: @GxDrogers

## 🙏 Acknowledgments

  Inspiration: Every developer who struggled with complex JSON structures
  
  Testing: Early adopters and contributors
  
  Community: Python packaging and open-source ecosystem
  
  Icons: Twitter Emoji for the beautiful icons

## 📞Support
  Documentation: GitHub Wiki
  
  Issues: GitHub Issues
  
  Discussions: GitHub Discussions
  
  Email: midhunharidas0@gmail.com

## 🚀 Ready to X-ray Your Data?
    pip install mxray

⭐ Star the repo if you find MXRay useful!
<p align="center"> <i>MXRay - See your data structures, don't just read them</i> </p> 
    ```    

