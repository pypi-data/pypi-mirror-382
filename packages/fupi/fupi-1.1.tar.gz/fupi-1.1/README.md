# fupi

A brute-force shortcut to fix python import hell. Acronym standing for... um, Fixing-Up Python Imports. Sure, let's go with that. 

## Usage

Simply import fupi in your project:

```python
import fupi
```

This automatically detects and adds relevant directories (`src`, `test`, `app`) and their children to your Python path, making imports work seamlessly across your project structure regardless of how bad you screw it up.  This allow you to run components independently, run tests from anywhere, etc. 

This can be a bit dangerous in larger projects, as you have no idea what you're actually importing.  You can create local `fupi.env` files to limit the scope to what you care about, which will help.  This is a "move fast and break things" type of project. 

Also, you may consider commenting out `import fupi` once you get deployment and testing automated / located to a centralized starting point, again to make sure you're not hiding import bugs - by that point you won't likely need this brute-force tool.  Fupi is really a tool to speed up rapid-deploy tests / POCs / etc., where you're coding fast and loose, and especially for one-person projects (of which AI is increasing the number and velocity).

## Configuration

No configuration is needed if you use the defaults: 
- Adds `src`, `test`, `app` folders and subfolders to sys.path... 
- Skipping most common non-application file folders, like `.git`, `venv*`, `__pycache__`, `setup`, etc.

### .ENV File Config

To use different / more folder names, simply add the following to an existing .env file, or
create a new `*.env` or `fupi.env` file:

```
FUPI_ADD_DIRS="src,test"
FUPI_SKIP_DIRS="setup,venv*,*egg*"
```

The program will evaluate every `*.env` file it finds in the current working directory, it's parent, and all it's children. It then picks the best one that contains the two envars below:

The `FUPI_ADD_DIRS` will be string-matched against folders in your project, and on exact match, will include that folder and all subfolders into your sys.path.

The `FUPI_SKIP_DIRS` is a collection of regex patterns to skip, with string begin and end tags added (`^value$`).  Thus you can simply add a list of folder names, or use basic wildcard * characters. If
you want to get crazy with regex, be my guest - but understand the value will be wrapped (`^value$`).

The `FUPI_SKIP_DIRS` will also always append patters to disqualify any path starting with a period('.')
or an underscore('_') (i.e., `'\.*'` and `'\_*'`), which should catch most common skipped folders like
`.git`, `__pycache__`, etc.

### Environment Variable Config

Alternatively, you can add the above to os.envars before you `import fupi`.  Note, this process does NOT
use `dotenv`, which would also load into os.envars, although the behavior is similar, just restricted
to only `FUPI_*` configs.  Similar to the .env approach above, simply add a comma-delimited list of all folder names / regex patterns. 

### Manual Setting

You can also manually call the functions in the fupi libary with whatever settings you'd like.
To take advantage of this option, you'll have to escape the default behavior of running all logic on `import fupi`,
automatically.  Or, you can reset the `sys.path` using the roll-back ability, below.

To escape the auto-run, add a single .env or envvar as per below:

```
FUPI_ADD_DIRS="disable"
```

Then you can configure manually, with:

```python
from fupi import fupi
fupi.add_dirs_and_children_to_syspath(
    add_dirs=['my','app','folders'], 
    skip_dirs=['not','*these*'])
```

## Rollback
Finally, if you want to roll-back to a previous state, sys.path contents are logged in the object `sys_path_history`
which captures the pre-import snapshot at index[0], and subsequent snapshots every time a change is made. This would 
allow you to 'roll-back' to a pre-exexution state by simply:

```python
sys.path = fupi.sys_path_history['history'][0]
```