import json
from pathlib import Path
from typing import Union
from .core import MindMap

class Exporter:
    """Handle exporting mind maps to various formats"""
    
    @staticmethod
    def to_markdown(mind_map: MindMap, title: str = "Data Structure") -> str:
        """Export to markdown format"""
        lines = [f"# {title}\n", "```"]
        lines.append(str(mind_map))
        lines.append("```")
        return "\n".join(lines)
    
    @staticmethod
    def to_html(mind_map: MindMap, title: str = "Data Structure") -> str:
        """Export to interactive HTML format"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
            <style>
                body {{ font-family: 'Monaco', 'Menlo', monospace; margin: 20px; }}
                .mind-map {{ white-space: pre; line-height: 1.4; }}
                .highlight {{ background-color: yellow; font-weight: bold; }}
            </style>
        </head>
        <body>
            <h1>{title}</h1>
            <div class="mind-map">{str(mind_map)}</div>
            <script>
                // Simple search highlighting
                function highlightText(text) {{
                    const mapElement = document.querySelector('.mind-map');
                    const content = mapElement.textContent;
                    const regex = new RegExp(text, 'gi');
                    const highlighted = content.replace(regex, 
                        match => `<span class="highlight">${{match}}</span>`);
                    mapElement.innerHTML = highlighted;
                }}
            </script>
        </body>
        </html>
        """
        return html
    
    @staticmethod
    def to_json(mind_map: MindMap) -> str:
        """Export mind map structure to JSON"""
        def node_to_dict(node):
            return {
                "key": node.key,
                "value": str(node.value) if not isinstance(node.value, (dict, list)) else node.data_type,
                "depth": node.depth,
                "data_type": node.data_type,
                "children": [node_to_dict(child) for child in node.children]
            }
        
        return json.dumps(node_to_dict(mind_map.root), indent=2)

def save_mind_map(mind_map: MindMap, file_path: Union[str, Path], format: str = "auto"):
    """Save mind map to file in various formats"""
    path = Path(file_path)
    
    if format == "auto":
        format = path.suffix[1:] if path.suffix else "txt"
    
    content = ""
    if format == "md" or format == "markdown":
        content = Exporter.to_markdown(mind_map, path.stem)
    elif format == "html":
        content = Exporter.to_html(mind_map, path.stem)
    elif format == "json":
        content = Exporter.to_json(mind_map)
    else:  # txt
        content = str(mind_map)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)