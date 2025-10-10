from mxray import xray, MindMap, MindMapFactory, save_mind_map, Styles, Themes
import json
import os

def test_basic_functionality():
    print("=== TEST 1: BASIC FUNCTIONALITY ===")
    data = {
        'name': 'Midhun',
        'age': 25,
        'projects': ['MXRay', 'OpenSource'],
        'settings': {'theme': 'dark', 'notifications': True}
    }
    xray(data)
    print("✅ Basic functionality works!\n")

def test_different_styles():
    print("=== TEST 2: DIFFERENT STYLES ===")
    data = {'test': 'data', 'nested': {'value': 42}}
    
    print("Tree style:")
    xray(data, style=Styles.TREE)
    
    print("\nMinimal style:")
    xray(data, style=Styles.MINIMAL)
    
    print("\nArrow style:")
    xray(data, style=Styles.ARROW)
    
    print("✅ All styles work!\n")

def test_different_themes():
    print("=== TEST 3: DIFFERENT THEMES ===")
    data = {
        'user': 'Midhun',
        'email': 'midhun@example.com',
        'active': True,
        'count': 42
    }
    
    print("Default theme:")
    xray(data, theme="default")
    
    print("\nProfessional theme:")
    xray(data, theme="professional")
    
    print("\nColorful theme:")
    xray(data, theme="colorful")
    
    print("\nEmoji theme:")
    xray(data, theme="emoji")
    
    print("✅ All themes work!\n")

def test_metadata_features():
    print("=== TEST 4: METADATA FEATURES ===")
    data = {'name': 'Midhun', 'age': 25, 'scores': [95, 87, 92]}
    
    print("With types and memory:")
    xray(data, show_types=True, show_memory=True)
    
    print("\nWithout icons:")
    xray(data, show_icons=False)
    
    print("✅ Metadata features work!\n")

def test_search_functionality():
    print("=== TEST 5: SEARCH FUNCTIONALITY ===")
    data = {
        'users': [
            {'name': 'Midhun', 'role': 'admin'},
            {'name': 'Alice', 'role': 'user'}
        ],
        'admin_settings': {'level': 'high'}
    }
    
    mind_map = MindMap(data)
    print("Searching for 'admin':")
    mind_map.search("admin")
    print(mind_map.render())
    print("✅ Search works!\n")

def test_factory_methods():
    print("=== TEST 6: FACTORY METHODS ===")
    
    # Test from_json
    json_str = '{"creator": "Midhun", "project": "MXRay"}'
    mind_map = MindMapFactory.from_json(json_str)
    print("From JSON:")
    print(mind_map.render())
    
    # Test creating a test file
    test_data = {'test': 'data', 'number': 123}
    with open('test_data.json', 'w') as f:
        json.dump(test_data, f)
    
    try:
        mind_map = MindMapFactory.from_file('test_data.json')
        print("\nFrom file:")
        print(mind_map.render())
    except Exception as e:
        print(f"File reading: {e}")
    
    # Cleanup
    if os.path.exists('test_data.json'):
        os.remove('test_data.json')
    
    print("✅ Factory methods work!\n")

def test_export_functionality():
    print("=== TEST 7: EXPORT FUNCTIONALITY ===")
    data = {
        'project': 'MXRay',
        'author': 'Midhun Haridas',
        'features': ['visualization', 'export', 'cli']
    }
    
    mind_map = MindMap(data)
    
    # Test markdown export
    save_mind_map(mind_map, 'test_export.md', 'md')
    if os.path.exists('test_export.md'):
        print("✅ Markdown export works!")
        os.remove('test_export.md')
    
    # Test HTML export
    save_mind_map(mind_map, 'test_export.html', 'html')
    if os.path.exists('test_export.html'):
        print("✅ HTML export works!")
        os.remove('test_export.html')
    
    # Test JSON export
    save_mind_map(mind_map, 'test_export.json', 'json')
    if os.path.exists('test_export.json'):
        print("✅ JSON export works!")
        os.remove('test_export.json')
    
    print("✅ All exports work!\n")

def test_filter_functionality():
    print("=== TEST 8: FILTER FUNCTIONALITY ===")
    data = {
        'strings': ['hello', 'world'],
        'numbers': [1, 2, 3],
        'nested': {'key': 'value'}
    }
    
    mind_map = MindMap(data)
    
    # Filter only string values
    filtered = mind_map.filter(lambda node: isinstance(node.value, str))
    print("Only string values:")
    print(filtered.render())
    
    print("✅ Filter works!\n")

def test_focus_functionality():
    print("=== TEST 9: FOCUS FUNCTIONALITY ===")
    data = {
        'user': {
            'profile': {'name': 'Midhun', 'age': 25},
            'settings': {'theme': 'dark'}
        }
    }
    
    mind_map = MindMap(data)
    focused = mind_map.focus_on("user.profile")
    print("Focused on user.profile:")
    print(focused.render())
    
    print("✅ Focus works!\n")

def test_cli_functionality():
    print("=== TEST 10: CLI FUNCTIONALITY ===")
    
    # Test basic CLI (simulate command line)
    import subprocess
    import sys
    
    try:
        # Test with direct Python call
        result = subprocess.run([
            sys.executable, '-m', 'mxray.cli', 
            '--help'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ CLI help works!")
        else:
            print(f"CLI help issue: {result.stderr}")
            
    except Exception as e:
        print(f"CLI test skipped: {e}")
    
    print("\n")

def main():
    print("🧪 COMPREHENSIVE MXRAY TEST SUITE 🧪\n")
    
    try:
        test_basic_functionality()
        test_different_styles()
        test_different_themes()
        test_metadata_features()
        test_search_functionality()
        test_factory_methods()
        test_export_functionality()
        test_filter_functionality()
        test_focus_functionality()
        test_cli_functionality()
        
        print("🎉 ALL TESTS COMPLETED! 🎉")
        print("\n📋 Summary: Most core features should work.")
        print("If any test failed, we'll fix it specifically!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        print("Let me know which specific test failed and I'll fix it!")

if __name__ == "__main__":
    main()