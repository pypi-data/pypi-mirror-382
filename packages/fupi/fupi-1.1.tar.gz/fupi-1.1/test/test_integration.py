import subprocess
import tempfile
import os
from pathlib import Path

def test_fupi_import_integration():
    """Integration test: simulate pip install fupi and test import behavior"""
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test project structure
        (Path(tmpdir) / 'src').mkdir()
        (Path(tmpdir) / 'src' / 'myapp').mkdir()
        (Path(tmpdir) / 'test').mkdir()
        (Path(tmpdir) / 'test' / 'unit').mkdir()
        
        # Create test script that mimics the exact user experience
        test_script = Path(tmpdir) / 'test_fupi.py'
        fupi_src = Path(__file__).parent.parent / 'src'
        
        test_script.write_text(f'''
import sys
import os

# Add fupi to path (simulating pip install)
sys.path.insert(0, r"{fupi_src}")

print("sys.path BEFORE fupi")
before_len = len(sys.path)
before_paths = sys.path.copy()

import fupi

print("sys.path AFTER fupi") 
after_len = len(sys.path)
new_paths = [p for p in sys.path if p not in before_paths]

print(f"Paths before: {{before_len}}")
print(f"Paths after: {{after_len}}")
print(f"New paths: {{new_paths}}")

# Exit with status code indicating success/failure
if after_len > before_len:
    print("SUCCESS: fupi added paths to sys.path")
    sys.exit(0)
else:
    print("FAILURE: fupi did not modify sys.path")
    sys.exit(1)
''')
        
        # Run the test script in subprocess with fresh Python interpreter
        result = subprocess.run([
            'python3', str(test_script)
        ], cwd=tmpdir, capture_output=True, text=True)
        
        print("STDOUT:")
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        # Assert the test passed
        assert result.returncode == 0, f"Integration test failed. Return code: {result.returncode}"
        assert "SUCCESS: fupi added paths to sys.path" in result.stdout

if __name__ == '__main__':
    test_fupi_import_integration()
    print("Integration test passed!")