from pathlib import Path
import sys, os, re 

# capture initial state:
sys_path_history = {
    'history': [sys.path.copy()],
    'metadata': {
        'autostarted': True, 
        'required_envar_keys': ['FUPI_ADD_DIRS'],
        'all_envar_keys': ['FUPI_ADD_DIRS', 'FUPI_SKIP_DIRS'],
        'envars_retrieved_from': None,
        'FUPI_ADD_DIRS': [], 
        'FUPI_SKIP_DIRS': [],
        'FUPI_ADD_DIRS default': ['src', 'test', 'app'], 
        'FUPI_SKIP_DIRS default': ['setup', 'venv*', '*egg*', 'old*', '*old', '*bkup', '*backup']
    }
}
quotes = ['"',"'"]



def __chpth__(p:list) -> Path:
    """Helper function to select the best path from a list of paths containing .env files"""
    found_dirs = p[:] # make a copy
    if not p: return None

    env_file = None
    fupi_paths = [d.resolve() for d in found_dirs if 'fupi' in d.name.lower()] 
    if len(fupi_paths)     == 1: env_file = fupi_paths[0]     # first: `fupi.env` over alternatives
    if len(fupi_paths)      > 1: found_dirs = fupi_paths      #   multiple choices, below become tie-breakers
    if env_file: return env_file

    notest_paths = [d.resolve() for d in found_dirs if 'test' not in [s for s in d.parts]] 
    if len(notest_paths)   == 1: env_file = notest_paths[0]   # second: NOT appearing in a test tree
    if len(notest_paths)    > 1: found_dirs = notest_paths    #   multiple choices, below become tie-breakers
    if env_file: return env_file

    fewest_paths = [d for d in found_dirs if len(d.parts) == min([len(d.parts) for d in found_dirs])]
    if len(fewest_paths)   == 1: env_file = fewest_paths[0]   # third:  smallest number of subdirs
    if len(fewest_paths)    > 1: found_dirs = fewest_paths    #   multiple choices, below become tie-breakers
    if env_file: return env_file

    shortest_paths = [d for d in found_dirs if len(d.parts) == min([len((str(d))) for d in found_dirs])]
    if len(shortest_paths) == 1: env_file = shortest_paths[0] # forth:  shortest char length of path
    if len(shortest_paths)  > 1: found_dirs = shortest_paths  #   multiple choices, below become tie-breakers
    if env_file: return env_file

    # if all else fails: just pick the arbitrarily first found, either 
    if found_dirs: return found_dirs[0] # from filtered list 
    return p[0]  # or unfiltered




def load_dirnames_from_env(dotenv_filepath:Path = './.env') -> tuple[list,list]:
    """
    Loads DIR names, for searching and skipping, from an .env file.

    Environment variables it is looking for (examples below are default):
    - FUPI_ADD_DIRS="src,test"
    - FUPI_SKIP_DIRS="setup,venv*,*egg*"
    
    This does NOT load these data elements into sys.path, nor will
    it load anything else from the .env file (i.e., does not use
    dotenv library). 
    
    If the .env file is not found, it will search for `.env` then `fupi.env` in CWD(),
    then in the parent of CWD(), then the direct children of CWD().  After that, it 
    will use the above defaults.  If the above defaults yield no folders (nothing added
    to sys.path), you will have to call the functions directly. 
    """
    
    use_default = False
    env_file = None
    rtn = {'FUPI_ADD_DIRS':[], 'FUPI_SKIP_DIRS':[]}
    
    # add paths in which to search for an .env file, containing envvars
    search_dirs  = [Path(dotenv_filepath).parent,  # hard-coded value first
                    Path.cwd().absolute(),  # then CWD
                    Path.cwd().absolute().parent,  # then CWD parent
                    *[d for d in Path.cwd().absolute().glob('*/')] ]  # finally all CWD children

    # collect dirs containing an .env file
    found_dirs = [] 
    for dir in search_dirs: 
        for file in [f for f in dir.glob('*.env')]: 
            found_dirs.append(file)
    
    # repeat until we find an .env with the right envvars
    while True: 
        
        # exit if found_dirs is empty
        if not found_dirs: 
            use_default = True
            break
        
        # with 1 or more record in found_dirs, select the most likely single file:
        env_file = __chpth__(found_dirs) 

        # string-parse the lines into a clean dir, absent wrapping quotes
        with open(env_file, 'r') as f:
            lines = [l.strip() for l in f.readlines()]
        lines = {l.split('=')[0].replace('"',''):l.split('=')[1] for l in lines if '=' in l}
        lines = {n:v[1:-1] if v[:1] in quotes or v[-1:] in quotes else v for n,v in lines.items()}

        if [l for l in lines.keys() if l in sys_path_history['metadata']['required_envar_keys']]:
            break # this one will work!

        # if the file is missing FUPI_ADD_DIRS, discard the file and try again:
        if env_file in found_dirs:
            found_dirs.remove(env_file)
        else:
            # Remove by matching path
            found_dirs = [f for f in found_dirs if f.resolve() != env_file.resolve()]

    
    # report on selection made:
    if use_default: 
        sys_path_history['metadata']['envars_retrieved_from'] = 'default values'
        for envar in sys_path_history['metadata']['all_envar_keys']:
            sys_path_history['metadata'][envar] = sys_path_history['metadata'][f'{envar} default']
        
    else: # custom envars found:
        sys_path_history['metadata']['envars_retrieved_from'] = str(env_file)
        lines = {n:v.split(',') for n,v in lines.items() if n in sys_path_history['metadata']['all_envar_keys']}
        for envar in lines.keys():
            sys_path_history['metadata'][envar] = lines[envar]

    return sys_path_history['metadata']['FUPI_ADD_DIRS'], sys_path_history['metadata']['FUPI_SKIP_DIRS']

 


def add_dirs_and_children_to_syspath(add_dirs = None, skip_dirs = None) -> dict:
    """
    Adds supplied dir names, as we as all children dirs, to sys.path, 
    except those names regex matching entries in the skip dirs list, 
    or dir names starting with `.` or `_` (i.e., `.git` or `__pycache__`).

    ** This process runs on import, but can be rolled-back and re-run. **
    
    Specified are NAMES of directories, not paths, of where to start recursion.
    If a path is supplied, only the top-most directory will be used. 
    
    The order of dirs evaluted are: 
    - parameters passed into the function directly
    - parameters found in the environment variables already, as:
        - FUPI_ADD_DIRS
        - FUPI_SKIP_DIRS
    - Dir names found using `load_dirnames_from_env()`
    - Default values of:
        - add_dirs = ['src','test']
        - skip_dirs = ['setup','venv*']
    
    If you add FUPI_ADD_DIRS but leave it blank, or set to any of the items 
    below, the process will not execute. This is true regardless of where 
    FUPI_ADD_DIRS is set: ['disable','stop','quit','not run','exit','']

    Args:
        add_dirs (list): List of dir names to search for and add to sys.path.
        skip_dirs (list): List of dir names to skip when adding to sys.path.

    Returns: 
        dict: timestamp key and sys.path() output cooresponding to the local 
        machine time. This process runs on import, however, the first entry 
        would be the original system state, if you need to roll-back.
    """

    # define list of add_dirs and optionally, skip_dirs
    #   Supplied in params?
    if add_dirs:  
        add_dirs = list(add_dirs)
        skip_dirs = list(skip_dirs)
        sys_path_history['metadata']['envars_retrieved_from'] = 'function parameters'
    elif os.getenv('FUPI_ADD_DIRS'):  # look in envvars:
            add_dirs = list(os.getenv('FUPI_ADD_DIRS').split(','))
            skip_dirs = list(os.getenv('FUPI_SKIP_DIRS').split(', '))
            sys_path_history['metadata']['envars_retrieved_from'] = 'OS environment variables'
    else:  # pull from .env files, or get default
        add_dirs, skip_dirs = load_dirnames_from_env() # does its own reporting
            
    if not add_dirs: return sys_path_history  # if after all that add_dirs still empty, just exit

    # make sure there are no residual quotes around anything:
    add_dirs = [d[1:-1] if d[:1] in quotes and d[-1:] in quotes else d for d in add_dirs]
    
    # Handle skip_dirs - ensure it's a proper list and split any comma-separated values
    if skip_dirs and isinstance(skip_dirs[0], str) and ',' in skip_dirs[0]:
        # If skip_dirs is a single comma-separated string, split it
        skip_dirs = [d.strip() for d in skip_dirs[0].split(',')]
    
    skip_dirs = [d[1:-1] if d[:1] in quotes and d[-1:] in quotes else d for d in skip_dirs]
    skip_dirs.extend([r'\.*'])  # always skip paths that begin with a period (e.g., `.git`)
    skip_dirs.extend([r'\_*'])  # always skip paths that begin with an underscore (e.g., `__pycache__`)

    # report configuration: 
    sys_path_history['metadata']['FUPI_ADD_DIRS'] = add_dirs
    sys_path_history['metadata']['FUPI_SKIP_DIRS'] = skip_dirs

    # if user has flagged add_dirs to NOT RUN, EXIT.  Must be a single entry list matching below:
    if len(add_dirs) == 1 and add_dirs[0].lower() in ['disable','stop','quit','not run','exit','']: return sys_path_history

    # at this point, we should have clean add_dirs and skip_dirs, and mandate to continue    
    # add all qualifying paths that contain an interested dirpath anywhere:
    allpaths = []
    for dirname in add_dirs: 
        # add any qualifying paths, per add_dirs (as matched strings):
        tdir = Path.cwd().resolve()
        found_paths = [pth for pth in tdir.rglob('*/') if dirname in pth.parts]
        allpaths.extend(found_paths)

    # remove any non-qualifying paths, per skip_dirs (as regex patterns):
    skip_dirs_re = [re.compile(f'^{pth}$'.replace('*', '.*')) for pth in skip_dirs]
    allpaths = [pth for pth in allpaths if not any([s.match(part) for part in pth.parts for s in skip_dirs_re])]
         
    # add allpaths to the sys.path for the current process, 
    # thereby (hopefully) side-stepping python import-hell. 
    sys.path.extend([str(pth) for pth in allpaths if str(pth) not in sys.path])

    # add another entry for our tracking: 
    sys_path_history['history'].append(sys.path.copy())

    return sys_path_history


 