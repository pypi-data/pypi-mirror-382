import sys
import os
from pathlib import Path
import tempfile
import importlib

def test_import_fupi_modifies_syspath():
    """Test the primary use-case: importing fupi should modify sys.path"""
    original_cwd = os.getcwd()
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            
            # Create test directories that should be found
            (Path(tmpdir) / 'src').mkdir()
            (Path(tmpdir) / 'src' / 'subdir').mkdir()
            (Path(tmpdir) / 'test').mkdir()
            (Path(tmpdir) / 'test' / 'unit').mkdir()
            
            # Add fupi src to path for import
            fupi_src = Path(__file__).parent.parent / 'src'
            if str(fupi_src) not in sys.path:
                sys.path.insert(0, str(fupi_src))
            
            print('\nsys.path BEFORE fupi')
            original_paths = sys.path.copy()
            original_len = len(sys.path)
            
            # Since import is cached, test the function directly
            from fupi.fupi import add_dirs_and_children_to_syspath
            add_dirs_and_children_to_syspath()
            
            print('\nsys.path AFTER fupi')
            new_paths = [p for p in sys.path if p not in original_paths]
            
            # Verify paths were added
            assert len(sys.path) > original_len, "No paths were added to sys.path"
            assert len(new_paths) > 0, "No new paths detected"
            
            # Check that src and test directories were added (from temp dir)
            src_found = any(tmpdir in p and 'src' in p for p in new_paths)
            test_found = any(tmpdir in p and 'test' in p for p in new_paths)
            
            print(f"New paths added: {new_paths}")
            print(f"Found src paths: {src_found}")
            print(f"Found test paths: {test_found}")
            
            assert src_found or test_found, "Neither src nor test directories were added"
    finally:
        os.chdir(original_cwd)

if __name__ == '__main__':
    test_import_fupi_modifies_syspath()
    print("Import test passed!")