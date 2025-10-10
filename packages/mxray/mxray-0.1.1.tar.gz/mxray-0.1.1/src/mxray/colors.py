"""
ANSI color support for terminal output
"""

class Colors:
    """ANSI color codes"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    GRAY = '\033[90m'

class ColorTheme:
    """Color themes for different parts of the mind map"""
    
    @staticmethod
    def default():
        return {
            'key': Colors.CYAN,
            'string': Colors.GREEN,
            'number': Colors.YELLOW,
            'boolean': Colors.MAGENTA,
            'null': Colors.RED,
            'type': Colors.GRAY,
            'memory': Colors.GRAY,
            'highlight': Colors.YELLOW + Colors.BOLD,
            'connector': Colors.WHITE,
        }
    
    @staticmethod
    def professional():
        return {
            'key': Colors.BLUE,
            'string': Colors.GREEN,
            'number': Colors.WHITE,
            'boolean': Colors.MAGENTA,
            'null': Colors.RED,
            'type': Colors.GRAY,
            'memory': Colors.GRAY,
            'highlight': Colors.YELLOW,
            'connector': Colors.WHITE,
        }
    
    @staticmethod
    def colorful():
        return {
            'key': Colors.CYAN + Colors.BOLD,
            'string': Colors.GREEN,
            'number': Colors.YELLOW,
            'boolean': Colors.MAGENTA,
            'null': Colors.RED,
            'type': Colors.BLUE,
            'memory': Colors.GRAY,
            'highlight': Colors.YELLOW + Colors.BOLD,
            'connector': Colors.WHITE,
        }

def supports_color():
    """Check if terminal supports colors"""
    try:
        import sys
        return sys.stdout.isatty()
    except:
        return False

def get_color_theme(theme_name='default'):
    """Get color theme by name"""
    themes = {
        'default': ColorTheme.default(),
        'professional': ColorTheme.professional(),
        'colorful': ColorTheme.colorful(),
        'none': {k: '' for k in ColorTheme.default().keys()},  # No colors
    }
    return themes.get(theme_name, themes['default'])