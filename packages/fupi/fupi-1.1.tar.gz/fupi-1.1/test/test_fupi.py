import sys
import os
from pathlib import Path
import tempfile
import shutil

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from fupi.fupi import load_dirnames_from_env, add_dirs_and_children_to_syspath

def test_load_dirnames_from_env_defaults():
    """Test that defaults are returned when no .env file exists"""
    original_cwd = os.getcwd()
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            add_dirs, skip_dirs = load_dirnames_from_env()
            assert add_dirs == ['src', 'test', 'app']
            assert 'setup' in skip_dirs
            assert 'venv*' in skip_dirs
    finally:
        os.chdir(original_cwd)

def test_load_dirnames_from_env_custom():
    """Test loading custom values from .env file"""
    original_cwd = os.getcwd()
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            env_file = Path(tmpdir) / '.env'
            env_file.write_text('FUPI_ADD_DIRS="app,lib"\nFUPI_SKIP_DIRS="build,dist"')
            
            add_dirs, skip_dirs = load_dirnames_from_env()
            assert add_dirs == ['app', 'lib']
            assert skip_dirs == ['build', 'dist']
    finally:
        os.chdir(original_cwd)

def test_add_dirs_finds_directories():
    """Test that directories are found and added to sys.path"""
    original_cwd = os.getcwd()
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            
            # Create test directories
            (Path(tmpdir) / 'src').mkdir()
            (Path(tmpdir) / 'src' / 'subdir').mkdir()
            (Path(tmpdir) / 'test').mkdir()
            
            original_path_len = len(sys.path)
            add_dirs_and_children_to_syspath(['src', 'test'], ['venv*'])
            
            # Should have added paths
            assert len(sys.path) > original_path_len
            assert any('src' in p for p in sys.path)
    finally:
        os.chdir(original_cwd)

def test_skip_dirs_filtering():
    """Test that skip_dirs patterns work correctly"""
    original_cwd = os.getcwd()
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            
            # Create directories including ones to skip
            (Path(tmpdir) / 'src').mkdir()
            (Path(tmpdir) / 'venv_test').mkdir()
            (Path(tmpdir) / 'src' / 'venv_nested').mkdir()
            
            original_path_len = len(sys.path)
            add_dirs_and_children_to_syspath(['src'], ['venv*'])
            
            # Should not include venv paths
            new_paths = sys.path[original_path_len:]
            assert not any('venv' in p for p in new_paths)
    finally:
        os.chdir(original_cwd)

def test_disable_functionality():
    """Test that 'disable' prevents execution"""
    original_path_len = len(sys.path)
    result = add_dirs_and_children_to_syspath(['disable'], [])
    
    # Should not modify sys.path
    assert len(sys.path) == original_path_len
    assert result is not None

def test_skip_dirs_comma_separated_string():
    """Test that comma-separated skip_dirs string is properly split"""
    original_cwd = os.getcwd()
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            
            # Create test directories including ones to skip
            (Path(tmpdir) / 'src').mkdir()
            (Path(tmpdir) / 'setup_dir').mkdir()
            (Path(tmpdir) / 'old_stuff').mkdir()
            (Path(tmpdir) / 'venv_test').mkdir()
            
            # Test with comma-separated string (simulating .env file parsing)
            original_path_len = len(sys.path)
            result = add_dirs_and_children_to_syspath(['src'], ['setup*,old*,venv*'])
            
            # Verify skip_dirs was properly split in metadata
            skip_dirs = result['metadata']['FUPI_SKIP_DIRS']
            assert 'setup*' in skip_dirs
            assert 'old*' in skip_dirs
            assert 'venv*' in skip_dirs
            assert r'\.*' in skip_dirs  # default pattern should be added
            assert r'\_*' in skip_dirs  # default pattern should be added
            
            # Verify no skipped directories were added to sys.path
            new_paths = sys.path[original_path_len:]
            
            # Check for paths containing the temp directory and skip patterns
            temp_new_paths = [p for p in new_paths if tmpdir in p]
            
            # Check that only src directory was added, not the skipped ones
            assert any('src' in p for p in temp_new_paths), "src directory should be added"
            assert not any('setup_dir' in p for p in temp_new_paths), "setup_dir should be skipped"
            assert not any('old_stuff' in p for p in temp_new_paths), "old_stuff should be skipped"
            assert not any('venv_test' in p for p in temp_new_paths), "venv_test should be skipped"
            
    finally:
        os.chdir(original_cwd)

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
            
            # Test the function directly since module import is cached
            from fupi.fupi import add_dirs_and_children_to_syspath
            
            original_paths = sys.path.copy()
            original_len = len(sys.path)
            
            # Call the function directly (simulating what import fupi does)
            add_dirs_and_children_to_syspath()
            
            new_paths = [p for p in sys.path if p not in original_paths]
            
            # Verify paths were added
            assert len(sys.path) > original_len, "No paths were added to sys.path"
            assert len(new_paths) > 0, "No new paths detected"
            
            # Check that src and test directories were added
            src_found = any(tmpdir in p and 'src' in p for p in new_paths)
            test_found = any(tmpdir in p and 'test' in p for p in new_paths)
            
            assert src_found or test_found, "Neither src nor test directories were added"
            
    finally:
        os.chdir(original_cwd)

if __name__ == '__main__':
    test_load_dirnames_from_env_defaults()
    test_load_dirnames_from_env_custom()
    test_add_dirs_finds_directories()
    test_skip_dirs_filtering()
    test_disable_functionality()
    print("All tests passed!")