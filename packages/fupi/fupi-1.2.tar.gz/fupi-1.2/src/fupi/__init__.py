try:
    from .fupi import add_dirs_and_children_to_syspath
    # Automatically add directories to sys.path when imported
    add_dirs_and_children_to_syspath()
except Exception as e:
    print(f"Error importing or running fupi: {e}")
    import traceback
    traceback.print_exc()

__all__ = ['add_dirs_and_children_to_syspath']
