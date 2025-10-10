from typing import Dict, Any

class Styles:
    TREE = "tree"
    BOXED = "boxed"
    MINIMAL = "minimal"
    ARROW = "arrow"

class Themes:
    """Pre-defined themes with complete icon sets"""
    
    DEFAULT = {
        "name": "default",
        "icons": {
            "dict": "📦", "list": "📋", "tuple": "📑",
            "str": "🔤", "int": "🔢", "float": "🔢",
            "bool": "✅", "bool_false": "❌", "none": "🚫",
            # Common key-based icons
            "name": "📛", "username": "👤", "user": "👤", "email": "📧",
            "age": "🎂", "title": "✏️", "description": "📝",
            "id": "🆔", "url": "🌐", "link": "🔗", "website": "🌐",
            "phone": "📞", "address": "🏠", "location": "📍",
            "price": "💰", "cost": "💰", "amount": "💰",
            "date": "📅", "time": "⏰", "created": "📅", "updated": "🔄",
            "status": "📊", "active": "✅", "enabled": "✅", "disabled": "❌",
            "count": "🔢", "total": "🔢", "size": "📏",
            "file": "📄", "image": "🖼️", "photo": "🖼️",
            "password": "🔒", "token": "🔑", "key": "🔑",
            "tags": "🏷️", "categories": "📑",
        }
    }
    
    PROFESSIONAL = {
        "name": "professional",
        "icons": {
            "dict": "📊", "list": "📑", "tuple": "📄",
            "str": "🔤", "int": "#", "float": "##",
            "bool": "✓", "bool_false": "✗", "none": "∅",
            "name": "Name:", "user": "User:", "email": "Email:",
            "title": "Title:", "description": "Desc:",
        }
    }
    
    COLORFUL = {
        "name": "colorful", 
        "icons": {
            "dict": "🌈", "list": "🎨", "tuple": "📚",
            "str": "🎯", "int": "🔢", "float": "💯",
            "bool": "💚", "bool_false": "💔", "none": "⚫",
            "name": "👤", "user": "🤵", "email": "📮",
            "title": "🏷️", "description": "📄",
        }
    }
    
    EMOJI = {
        "name": "emoji",
        "icons": {
            "dict": "📦", "list": "📋", "tuple": "📑",
            "str": "🔤", "int": "🔢", "float": "🔢", 
            "bool": "✅", "bool_false": "❌", "none": "🚫",
            "name": "📛", "user": "👤", "email": "📧",
            "title": "✏️", "description": "📝",
        }
    }

def get_theme(theme_name: str) -> Dict[str, Any]:
    """Get theme by name with proper fallbacks"""
    themes = {
        "default": Themes.DEFAULT,
        "professional": Themes.PROFESSIONAL, 
        "colorful": Themes.COLORFUL,
        "emoji": Themes.EMOJI
    }
    theme = themes.get(theme_name, Themes.DEFAULT)
    
    # Ensure all required icon keys exist
    required_keys = ["dict", "list", "tuple", "str", "int", "float", "bool", "bool_false", "none"]
    for key in required_keys:
        if key not in theme["icons"]:
            theme["icons"][key] = Themes.DEFAULT["icons"][key]
    
    return theme