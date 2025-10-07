#modx.py: A module whose functions have to do with other modules.
#For example: importall(), a function used to import every single module
#in Python that is supported on most devices without printing an
#error message, does not print out dialog nor pop up a link when
#imported, and not required to be downloaded
#separately with Python (such as Pygame, downloaded in Terminal).
#
#Modules ios_support, pty, this, sre_compile, sre_parse,
#sre_constants, tty, idle and antigravity are left out of import_all().
#Reason: ios_support not supporting computers,
#pty and tty importing a nonexistent module (termios),
#sre_compile, sre_constants and sre_parse printing warnings,
#this printing out "The Zen of Python" poem, idle
#opening up Python Shell window, and
#antigravity popping out a web browser link
#(There are more modules left out but the full list is way too long).
#
#Permission to use this module is granted to anyone wanting to use it,
#under the following conditions: 1.) Any copies of this module must be clearly
#marked as so. 2.) The original of this module must not be misrepresented;
#you cannot claim this module is yours.

'''Notes: for imported() and modx_imported(), dependencies of modx itself as
this feature will be added in a future update, presumably update 2.0.0.

vcompat() checks for most issues for Python versions 2.0 - 3.12 and not all.
If every issue were to be included, the rules alone would be about 1500 lines
and the rest of the function would be 200 lines-ish. Most of the major issues
are included in vcompat(). Only less, very rare problems are left out.

Created by: Austin Wang. Created on: September 19, 2025. Last updated:
October 5, 2025'''

_version_= "1.8.3"

import sys, importlib, pkgutil, random, builtins, ast, importlib.util, os, tokenize, io
from pathlib import Path
from packaging import version

# Record baseline modules at time of ModX load
_initial_modules = set(sys.modules.keys())

# Capture original import
_original_import = builtins.__import__

# Track modules imported manually by user after ModX loaded
_user_imports = set()

def _tracking_import(name, globals=None, locals=None, fromlist=(), level=0):
    """Internal function. Not designed for public use."""
    mod = _original_import(name, globals, locals, fromlist, level)
    top_name = name.partition('.')[0]
    if not top_name.startswith('idlelib'):
        _user_imports.add(top_name)
    return mod

# Install hook
builtins._import_ = _tracking_import

# Track modules imported by ModX (ONLY directly requested ones)
_imported_by_modx = set()

# -------------------------
# Master Module List
# -------------------------
modules = [
        'collections', 'sys', 'asyncio', 'concurrent', 'ctypes', 'dbm', 'email',
        'encodings', 'ensurepip', 'html', 'http', 'idlelib', 'importlib', 'json', 'logging',
        'multiprocessing', 'pathlib', 'pydoc_data', 're', 'sqlite3',
        'sysconfig', 'test', 'tkinter', 'tomllib', 'turtledemo', 'unittest', 'urllib',
        'venv', 'wsgiref', 'xml', 'xmlrpc', 'zipfile', 'zoneinfo',
        '_pyrepl', '_collections_abc', '_colorize',
        '_compat_pickle', '_compression', '_markupbase', '_opcode_metadata',
        '_py_abc', '_pydatetime', '_pydecimal', '_pyio', '_pylong', '_sitebuiltins', '_strptime',
        '_threading_local', '_weakrefset', 'abc', 'argparse', 'ast', 'base64', 'bdb',
        'bisect', 'bz2', 'calendar', 'cmd', 'codecs', 'codeop', 'colorsys', 'compileall', 'configparser',
        'contextlib', 'contextvars', 'copy', 'copyreg', 'cProfile', 'csv', 'dataclasses', 'datetime',
        'decimal', 'difflib', 'dis', 'doctest', 'enum', 'filecmp', 'fileinput', 'fnmatch', 'fractions',
        'ftplib', 'functools', 'genericpath', 'getopt', 'getpass', 'gettext', 'glob', 'graphlib',
        'gzip', 'hashlib', 'heapq', 'hmac', 'imaplib', 'inspect', 'io', 'ipaddress', 'keyword', 'linecache',
        'locale', 'lzma', 'math', 'mailbox', 'mimetypes', 'modulefinder', 'netrc',
        'opcode', 'optparse', 'os', 'pdb', 'pickle', 'pickletools', 'pkgutil',
        'platform', 'plistlib', 'poplib', 'pprint', 'profile', 'pstats', 'py_compile',
        'pyclbr', 'pydoc', 'queue', 'quopri', 'random', 'reprlib', 'runpy', 'sched', 'secrets',
        'selectors', 'shelve', 'shlex', 'shutil', 'signal', 'site', 'smtplib', 'socket', 'socketserver',
        'ssl', 'stat', 'statistics', 'string', 'stringprep',
        'struct', 'subprocess', 'symtable', 'tabnanny', 'tarfile', 'tempfile', 'textwrap',
        'threading', 'timeit', 'token', 'tokenize', 'trace', 'traceback', 'tracemalloc', 'turtle',
        'types', 'typing', 'uuid', 'warnings', 'wave', 'weakref', 'webbrowser', 'zipapp', 'zipimport',
        '_future_', '_hello_', '_phello_', "atexit", "mmap",
        'autocomplete','autocomplete_w','autoexpand','browser','build',
        'calltip','calltip_w','codecontext','colorizer',
        'config','config_key','configdialog','debugger','debugger_r',
        'debugobj','debugobj_r','delegator','direct','dynoption','editor',
        'filelist','format','grep','help','help_about','history','hyperparser',
        'id','idle_test','iomenu','keyring','mainmenu','more_itertools',
        'multicall','outwin','parenmatch','pathbrowser','percolator','pyparse',
        'pyshell','query','redirector','replace','rpc','run',
        'runscript','screeninfo','scrolledlist','search','searchbase','searchengine',
        'sidebar','squeezer','stackviewer','statusbar','textview','tooltip',
        'tree','undo','util','window','zoomheight','zzdummy', 'builtins', 'itertools',
        'operator', 'collections.abc', 'errno', 'msvcrt', 'array', 'marshal',
        'rlcompleter', 'urllib.request', 'urllib.response', 'urllib.parse', 'urllib.error', 
        'urllib.robotparser', 'http.client', 'http.server',
        'xml.etree.ElementTree', 'xml.parsers.expat',
        '_thread', '_weakref', '_collections', '_ast', '_bisect',
        '_heapq', '_io', '_functools', '_operator', '_signal', '_socket', '_ssl',
        '_stat', '_struct', '_datetime', '_random', '_hashlib', '_md5', '_sha1',
        '_blake2', '_pickle', '_json', '_zoneinfo', '_opcode', 'cmath', 'numbers',
        '_codecs_cn', '_codecs_hk', '_codecs_iso2022', '_codecs_jp', '_codecs_kr',
        '_codecs_tw', '_interpchannels', '_interpqueues', '_interpreters',
        '_multibytecodec', '_sha2', '_sha3', '_suggestions', 'faulthandler', 'xxsubtype'
        ]

#########################
# Bulk import functions #
#########################

def import_all():
    """Import almost every module in Python that is given when downloading Python."""
    import builtins
    caller_globals = globals()
    builtins._import_ = _original_import
    success = []
    failed = []
    try:
        for m in modules:
            try:
                # Import AND add to caller's globals
                module_obj = importlib.import_module(m)
                caller_globals[m] = module_obj
                _imported_by_modx.add(m)
                success.append(m)
            except Exception as e:
                failed.append((m, str(e)))
    finally:
        builtins._import_ = _tracking_import
    
    # Show results
    print(f"import_all() Results:")
    print(f"SUCCESS: {len(success)} modules")
    print(f"FAILED: {len(failed)} modules")
    if failed:
        print("\nFailed imports:")
        for mod, error in failed[:10]:  # Show first 10 failures
            print(f"   {mod}: {error}")
        if len(failed) > 10:
            print(f"   ... and {len(failed) - 10} more")

def import_random(n):
    """Import n random stdlib modules and track them."""
    import builtins
    caller_globals = globals()
    chosen = random.sample(modules, min(n, len(modules)))
    builtins._import_ = _original_import
    success = []
    failed = []
    try:
        for m in chosen:
            try:
                # Import AND add to caller's globals
                module_obj = importlib.import_module(m)
                caller_globals[m] = module_obj
                _imported_by_modx.add(m)
                success.append(m)
            except Exception as e:
                failed.append((m, str(e)))
    finally:
        builtins._import_ = _tracking_import
    
    # Show results
    print(f" import_random({n}) Results:")
    print(f" REQUESTED: {len(chosen)} modules")
    print(f" SUCCESS: {len(success)} modules") 
    print(f" FAILED: {len(failed)} modules")
    if failed:
        print("\nFailed imports:")
        for mod, error in failed:
            print(f"   {mod}: {error}")
    
    return success


def import_external():
    """Import all installed third-party modules (not in stdlib list)."""
    import builtins
    caller_globals = globals()
    stdlib_set = set(modules) | set(sys.builtin_module_names)
    builtins._import_ = _original_import
    success = []
    failed = []
    try:
        for finder, name, ispkg in pkgutil.iter_modules():
            if name not in stdlib_set:
                try:
                    # Import AND add to caller's globals
                    module_obj = importlib.import_module(name)
                    caller_globals[name] = module_obj
                    _imported_by_modx.add(name.partition('.')[0])
                    success.append(name)
                except Exception as e:
                    failed.append((name, str(e)))
    finally:
        builtins._import_ = _tracking_import
    
    # Show results
    print(f" import_external() Results:")
    print(f" SUCCESS: {len(success)} third-party modules")
    print(f" FAILED: {len(failed)} modules")
    if failed:
        print("\nFirst 10 failures:")
        for mod, error in failed[:10]:
            print(f"   {mod}: {error}")

def import_screen():
    """Import common screen/GUI/game modules if available."""
    import builtins
    caller_globals = globals()
    screen_modules = ['pygame', 'pyglet', 'arcade', 'tkinter', 'turtle']
    builtins._import_ = _original_import
    success = []
    failed = []
    try:
        for m in screen_modules:
            try:
                # Import AND add to caller's globals
                module_obj = importlib.import_module(m)
                caller_globals[m] = module_obj
                _imported_by_modx.add(m)
                success.append(m)
            except Exception as e:
                failed.append((m, str(e)))
    finally:
        builtins._import_ = _tracking_import
    
    # Show results
    print(f" import_screen() Results:")
    print(f" SUCCESS: {len(success)} GUI modules")
    print(f" FAILED: {len(failed)} modules")
    if failed:
        print("\nFailed imports:")
        for mod, error in failed:
            print(f"   {mod}: {error}")

def import_letter(letter):
    """Import every stdlib module from ModX 'modules' list
whose name starts with given letter."""
    import builtins
    caller_globals = globals()
    letter = letter.lower()
    success = []
    failed = []
    builtins._import_ = _original_import
    try:
        for m in modules:
            if m.lower().startswith(letter):
                try:
                    # Import AND add to caller's globals
                    module_obj = importlib.import_module(m)
                    caller_globals[m] = module_obj
                    _imported_by_modx.add(m)
                    success.append(m)
                except Exception as e:
                    failed.append((m, str(e)))
    finally:
        builtins._import_ = _tracking_import
    
    # Show results
    print(f" import_letter('{letter}') Results:")
    print(f" SUCCESS: {len(success)} modules starting with '{letter}'")
    print(f" FAILED: {len(failed)} modules")
    if failed:
        print("\nFailed imports:")
        for mod, error in failed:
            print(f"   {mod}: {error}")
    
    return success

######################
# Data and reporting #
######################

def modfunctions(module_name):
    """Show how many and what functions a module has without importing it."""
    try:
        # Find module spec without importing
        spec = importlib.util.find_spec(module_name)
        if not spec:
            print(f"Module '{module_name}' not found.")
            return
        
        if not spec.origin or not spec.origin.endswith('.py'):
            print(f"Module '{module_name}' is built-in or compiled (no source for analysis).")
            return
        
        print(f"Module: {module_name}")
        print(f"Source: {spec.origin}")
        print("=" * 50)
        
        # Read and parse the source file
        with open(spec.origin, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # Parse with AST to find function definitions
        functions = []
        try:
            tree = ast.parse(source_code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Skip private functions (starting with _) and specific internal functions
                    if (not node.name.startswith('_') and 
                        node.name not in ['easter_egg'] and
                        not node.name.startswith('_tracking')):
                        functions.append(node.name)
        except SyntaxError:
            print("Could not parse module source code.")
            return
        
        # Sort and display results
        functions.sort()
        print(f"Total public functions: {len(functions)}")
        
        if functions:
            print("\nFunctions found:")
            for i, func_name in enumerate(functions, 1):
                print(f"  {i}. {func_name}()")
        else:
            print("\nNo public functions found in this module.")
            
    except (FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
        print(f"Could not read module source: {e}")
    except Exception as e:
        print(f"Error analyzing module: {e}")

def modclasses(module_name):
    """Show how many and what classes a module has without importing it."""
    try:
        # Find module spec without importing
        spec = importlib.util.find_spec(module_name)
        if not spec:
            print(f"Module '{module_name}' not found.")
            return
        
        if not spec.origin or not spec.origin.endswith('.py'):
            print(f"Module '{module_name}' is built-in or compiled (no source for analysis).")
            return
        
        print(f"Module: {module_name}")
        print(f"Source: {spec.origin}")
        print("=" * 50)
        
        # Read and parse the source file - NO IMPORT HAPPENS HERE
        with open(spec.origin, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # Parse with AST to find class definitions
        classes = []
        try:
            tree = ast.parse(source_code)  # This just parses the text, doesn't import
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Skip private classes (starting with _)
                    if not node.name.startswith('_'):
                        classes.append(node.name)
        except SyntaxError:
            print("Could not parse module source code.")
            return
        
        # Sort and display results
        classes.sort()
        print(f"Total public classes: {len(classes)}")
        
        if classes:
            print("\nClasses found:")
            for i, class_name in enumerate(classes, 1):
                print(f"  {i}. {class_name}")
        else:
            print("\nNo public classes found in this module.")
            
    except (FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
        print(f"Could not read module source: {e}")
    except Exception as e:
        print(f"Error analyzing module: {e}")

def list_importall():
    """Return the list of modules that import_all() would import."""
    return modules

def modules_loaded():
    """Show how many modules are currently loaded in sys.modules."""
    return len(sys.modules)

def imported():
    """Show all modules imported since ModX loaded
(user + ModX + dependencies (excluding ModX dependencies))."""
    current = set(sys.modules.keys())
    new_since = current - _initial_modules

    # Filter out modx internals and noise
    filtered_modules = set()
    for module_name in new_since:
        if (module_name == 'modx' or 
            module_name.startswith('modx.') or
            module_name.startswith('test.') or
            module_name.startswith('_test') or
            module_name in ['_main_', 'sys', 'builtins']):
            continue
        filtered_modules.add(module_name)
    sorted_modules = sorted(filtered_modules)
    print("Modules imported after ModX load (user + ModX + dependencies):")
    for name in sorted_modules:
        print("-", name)
    print(f"\nTotal modules imported after ModX load: {len(sorted_modules)}")


def modx_imported():
    """Show ONLY the modules directly imported via ModX functions."""
    shown = sorted(_imported_by_modx)
    print("Modules imported directly via ModX (excluding dependencies):")
    for name in shown:
        print("-", name)
    print(f"\nTotal modules imported via ModX: {len(shown)}")
    
def nonimported():
    """Return a list of most STANDARD LIBRARY
modules that have NOT been imported yet."""
    # Get all known standard library modules from our master list
    all_stdlib_modules = set(modules)
    
    # Add built-in modules
    all_stdlib_modules.update(sys.builtin_module_names)
    
    # Filter out modules that are already imported
    unimported = []
    for module_name in all_stdlib_modules:
        if module_name not in sys.modules:
            unimported.append(module_name)
    
    return sorted(unimported)

############################
# Tracking and Information #
############################

def dependencies(module_name):
    """Show what other modules a specific module depends on without importing it."""
    import re
    import ast
    
    dependencies = set()
    
    print(f"Dependency analysis for: {module_name}")
    print("=" * 40)
    
    try:
        # Find the module spec without importing
        spec = importlib.util.find_spec(module_name)
        if not spec:
            print(f"Module '{module_name}' not found")
            return
        
        if spec.origin and spec.origin.endswith('.py'):
            print(f"File: {spec.origin}")
            
            try:
                with open(spec.origin, 'r', encoding='utf-8') as f:
                    source_code = f.read()
                
                # Parse with AST for accurate import detection
                try:
                    tree = ast.parse(source_code)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                dependencies.add(alias.name.split('.')[0])
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:  # from x import y
                                dependencies.add(node.module.split('.')[0])
                except SyntaxError:
                    # Fallback to regex for compiled modules or syntax issues
                    imports = re.findall(r'^(?:import|from)\s+([\w\.]+)', source_code, re.MULTILINE)
                    for imp in imports:
                        dependencies.add(imp.split('.')[0])
                        
            except (UnicodeDecodeError, FileNotFoundError, IOError):
                print("   (Source not readable)")
        
        elif spec.origin:
            print(f"File: {spec.origin} (compiled module)")
        else:
            print("   (Built-in module)")
        
        # Filter out common built-ins and self
        dependencies.discard(module_name.split('.')[0])
        dependencies.discard('_future_')
        dependencies.discard('builtins')
        
        # Show results
        if dependencies:
            print("Dependencies found:")
            for dep in sorted(dependencies):
                # Check if dependency would be importable
                dep_spec = importlib.util.find_spec(dep)
                status = "[AVAILABLE]" if dep_spec else "[NOT FOUND]"
                print(f"   {dep}")
        else:
            print("No external dependencies found")
            
    except Exception as e:
        print(f"Error analyzing module: {e}")

def search_modules(keyword):
    """Search for modules whose names contain the keyword."""
    keyword = keyword.lower()
    return [m for m in modules if keyword in m.lower()]

def info(module_name):
    """Show basic info about a module: file path, built-in status, docstring."""
    import inspect
    try:
        mod = sys.modules[module_name] if module_name in sys.modules else importlib.import_module(module_name)
    except ImportError:
        print(f"Module '{module_name}' not found.")
        return
    path = getattr(mod, '_file_', '(built-in)')
    doc = (inspect.getdoc(mod) or '').splitlines()[0:3]
    print(f"Module: {module_name}")
    print(f"Path: {path}")
    print("Docstring:")
    for line in doc:
        print(line)

def is_imported(module_name: str):
    """
    Check if a module is imported in the caller's globals.
    True  -> currently imported in shell globals
    False -> exists but not imported yet
    'Module X doesn't exist.' -> if module does not exist
    """
    import importlib.util, inspect
    frame = inspect.currentframe().f_back
    caller_globals = frame.f_globals
    if module_name in caller_globals:
        return True
    spec = importlib.util.find_spec(module_name)
    if spec:
        return False
    return f"Module {module_name} doesn't exist."

def vcompat(module_name, python_version=None):
    """
    Compatibility checker for Python versions.

    - If python_version is given: checks only that version.
    - If None: sweeps ALL Python versions 2.0 → 3.12,
      reports each issue only once with earliest relevant version.
    """
    COMPAT_RULES = {
        # === Python 2.0-2.7 Features ===
        "print": {"removed_in": "3.0", "note": "Python 2 print statement not valid in Python 3+"},
        "print>>": {"removed_in": "3.0", "note": "Python 2 print chevron syntax removed"},
        "xrange": {"removed_in": "3.0", "note": "Use range() in Python 3"},
        "raw_input": {"removed_in": "3.0", "note": "Use input() in Python 3"},
        "unicode": {"removed_in": "3.0", "note": "Use str in Python 3"},
        "long": {"removed_in": "3.0", "note": "long type merged into int"},
        "basestring": {"removed_in": "3.0", "note": "basestring removed, use str"},
        "apply": {"removed_in": "3.0", "note": "apply() removed, call function directly"},
        "execfile": {"removed_in": "3.0", "note": "execfile() removed, use exec()"},
        "reload": {"removed_in": "3.0", "note": "reload() moved to importlib"},
        "coerce": {"removed_in": "3.0", "note": "coerce() removed"},
        "file": {"removed_in": "3.0", "note": "file type removed, use open()"},

        # Python 2.2+ (generators)
        "generators": {"added_in": "2.2", "note": "Generators and yield added"},

        # Python 2.3+
        "enumerate": {"added_in": "2.3", "note": "enumerate() function added"},
        "boolean": {"added_in": "2.3", "note": "bool type added"},

        # Python 2.4+
        "decorators": {"added_in": "2.4", "note": "Function decorators @ added"},
        "generator_expressions": {"added_in": "2.4", "note": "Generator expressions added"},

        # Python 2.5+
        "with_statement": {"added_in": "2.5", "note": "with statement added"},
        "conditional_expressions": {"added_in": "2.5", "note": "x if condition else y syntax added"},

        # Python 2.6+
        "str.format": {"added_in": "2.6", "note": "str.format() method added"},
        "class_decorators": {"added_in": "2.6", "note": "Class decorators added"},

        # Python 2.7+
        "dict_comprehensions": {"added_in": "2.7", "note": "Dictionary comprehensions added"},
        "set_literals": {"added_in": "2.7", "note": "Set literals {1,2,3} added"},

        # === Python 3.0+ Breaking Changes ===
        "exec": {"changed_in": "3.0", "note": "exec is a function, not a statement"},
        "print_function": {"changed_in": "3.0", "note": "print is a function, not a statement"},

        # Module renames (3.0)
        "ConfigParser": {"removed_in": "3.0", "note": "Renamed to configparser"},
        "cPickle": {"removed_in": "3.0", "note": "Renamed to pickle"},
        "StringIO": {"removed_in": "3.0", "note": "Use io.StringIO"},
        "Queue": {"removed_in": "3.0", "note": "Renamed to queue"},
        "SocketServer": {"removed_in": "3.0", "note": "Renamed to socketserver"},
        "Tkinter": {"removed_in": "3.0", "note": "Renamed to tkinter"},
        "urllib2": {"removed_in": "3.0", "note": "Renamed to urllib"},

        # Python 3.1+
        "importlib": {"added_in": "3.1", "note": "importlib module added"},
        "ordered_dict": {"added_in": "3.1", "note": "collections.OrderedDict added"},

        # Python 3.2+
        "concurrent.futures": {"added_in": "3.2", "note": "concurrent.futures module added"},
        "argparse": {"added_in": "3.2", "note": "argparse added to stdlib"},

        # Python 3.3+
        "yield from": {"added_in": "3.3", "note": "yield from syntax added"},
        "venv": {"added_in": "3.3", "note": "venv module added"},
        "faulthandler": {"added_in": "3.3", "note": "faulthandler module added"},
        "ipaddress": {"added_in": "3.3", "note": "ipaddress module added"},

        # Python 3.4+
        "asyncio": {"added_in": "3.4", "note": "asyncio module added"},
        "enum": {"added_in": "3.4", "note": "enum module added"},
        "pathlib": {"added_in": "3.4", "note": "pathlib module added"},

        # Python 3.5+
        "async": {"changed_in": "3.5", "note": "'async' became a reserved keyword"},
        "await": {"changed_in": "3.5", "note": "'await' became a reserved keyword"},
        "typing": {"added_in": "3.5", "note": "typing module added"},
        "@ operator": {"added_in": "3.5", "note": "Matrix multiplication operator @ added"},

        # Python 3.6+
        "fstrings": {"added_in": "3.6", "note": "f-string syntax added"},
        "secrets": {"added_in": "3.6", "note": "secrets module added"},
        "underscore_literals": {"added_in": "3.6", "note": "1_000_000 numeric literal syntax"},

        # Python 3.7+
        "async/await": {"changed_in": "3.7", "note": "async/await became proper keywords"},
        "dataclasses": {"added_in": "3.7", "note": "dataclasses module added"},
        "contextvars": {"added_in": "3.7", "note": "contextvars module added"},

        # Python 3.8+
        "walrus": {"added_in": "3.8", "note": "Walrus operator := added"},
        "positional_only": {"added_in": "3.8", "note": "Positional-only parameters / added"},
        "fstring=": {"added_in": "3.8", "note": "f-string = debugging syntax added"},

        # Python 3.9+
        "dict_union": {"added_in": "3.9", "note": "Dict union | operator added"},
        "str_removeprefix": {"added_in": "3.9", "note": "str.removeprefix/removesuffix added"},
        "zoneinfo": {"added_in": "3.9", "note": "zoneinfo module added"},

        # Python 3.10+
        "match": {"added_in": "3.10", "note": "Structural pattern matching added"},
        "union_operator": {"added_in": "3.10", "note": "X | Y union type syntax added"},

        # Python 3.11+
        "exception_groups": {"added_in": "3.11", "note": "ExceptionGroups and except* added"},
        "tomllib": {"added_in": "3.11", "note": "tomllib module added"},

        # Python 3.12+
        "fstring_debug": {"added_in": "3.12", "note": "Enhanced f-string debugging"},
        "type_parameter_syntax": {"added_in": "3.12", "note": "New type parameter syntax"},

        # === Critical Deprecations ===
        "cgi": {"deprecated_in": "3.11", "removed_in": "3.13", "note": "cgi module deprecated"},
        "distutils": {"deprecated_in": "3.10", "removed_in": "3.12", "note": "distutils deprecated"},
        "imp": {"deprecated_in": "3.4", "removed_in": "3.12", "note": "imp module deprecated"},
        "asyncore": {"deprecated_in": "3.6", "note": "asyncore module deprecated"},
        "asynchat": {"deprecated_in": "3.6", "note": "asynchat module deprecated"},

        # === Syntax Changes ===
        "raise Exception,": {"removed_in": "3.0", "note": "Old raise syntax removed"},
        "except Exception,": {"removed_in": "3.0", "note": "Old except syntax removed"},
        "backticks": {"removed_in": "3.0", "note": "Backticks for repr() removed"},
        "<>": {"removed_in": "3.0", "note": "<> operator removed, use !="},

        # === Standard Library Changes ===
        "thread": {"removed_in": "3.0", "note": "thread module renamed to _thread"},
        "dummy_thread": {"removed_in": "3.0", "note": "dummy_thread module removed"},
        "anydbm": {"removed_in": "3.0", "note": "anydbm module removed"},
        "dbhash": {"removed_in": "3.0", "note": "dbhash module removed"},
        "dumbdbm": {"removed_in": "3.0", "note": "dumbdbm module removed"},
        "gdbm": {"removed_in": "3.0", "note": "gdbm module removed"},
        "whichdb": {"removed_in": "3.0", "note": "whichdb module removed"},
        "bsddb": {"removed_in": "3.0", "note": "bsddb module removed"},
        "md5": {"removed_in": "3.0", "note": "md5 module removed, use hashlib"},
        "sha": {"removed_in": "3.0", "note": "sha module removed, use hashlib"},
        "crypt": {"removed_in": "3.0", "note": "crypt module removed"},
        "popen2": {"removed_in": "3.0", "note": "popen2 module removed"},
        "commands": {"removed_in": "3.0", "note": "commands module removed, use subprocess"},
    }

    # Versions to check
    if python_version:
        targets = [version.parse(str(python_version))]
        if targets[0] > version.parse("3.12"):
            targets[0] = version.parse("3.12")
    else:
        targets = [version.parse(f"{major}.{minor}")
                   for major in (2, 3)
                   for minor in range(0, (8 if major == 2 else 13))]

    # --- Load source ---
    spec = importlib.util.find_spec(module_name)
    if not spec or not spec.origin or not spec.origin.endswith(".py"):
        print(f"Module {module_name} not found or not a .py source file.")
        return

    with open(spec.origin, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    warnings = {}

    # --- Parse with tokenize to identify comments and strings ---
    tokens = list(tokenize.generate_tokens(io.StringIO(content).readline))
    
    # Build a set of token positions that are in comments or strings
    comment_string_positions = set()
    current_line = 1
    current_col = 0
    
    for tok in tokens:
        if tok.type in (tokenize.COMMENT, tokenize.STRING):
            # Mark this entire token as being in comment/string
            start_line, start_col = tok.start
            end_line, end_col = tok.end
            
            # For multi-line tokens, we need to handle line breaks
            if start_line == end_line:
                for col in range(start_col, end_col):
                    comment_string_positions.add((start_line, col))
            else:
                # First line
                for col in range(start_col, 1000):  # Assume line length < 1000
                    comment_string_positions.add((start_line, col))
                # Middle lines
                for line in range(start_line + 1, end_line):
                    for col in range(0, 1000):
                        comment_string_positions.add((line, col))
                # Last line
                for col in range(0, end_col):
                    comment_string_positions.add((end_line, col))
    
    def _is_in_comment_or_string(line, col):
        """Check if a position is within a comment or string."""
        return (line, col) in comment_string_positions

    def _add_warning(key, rule, label):
        if key not in warnings:
            warnings[key] = label

    def _check_if_problematic(rule, targets):
        """Not designed for public use"""
        if "removed_in" in rule:
            removed_ver = version.parse(rule["removed_in"])
            return any(target >= removed_ver for target in targets)
        elif "added_in" in rule:
            added_ver = version.parse(rule["added_in"])
            return any(target < added_ver for target in targets)
        return False

    # === Check tokens - only if NOT in comments or strings ===
    for key, rule in COMPAT_RULES.items():
        if key in ["print_stmt", "exec_stmt", "async_kw", "await_kw", "walrus", "match"]:
            continue  # handled by AST
        
        # More precise token checking - look for actual usage patterns
        if any(key in token.string for token in tokens if token.type == tokenize.NAME):
            # Check each occurrence to see if it's in a comment or string
            valid_occurrence = False
            
            for token in tokens:
                if token.type == tokenize.NAME and token.string == key:
                    line, col = token.start
                    if not _is_in_comment_or_string(line, col):
                        valid_occurrence = True
                        break
            
            if not valid_occurrence:
                continue  # Skip if all occurrences are in comments/strings

            # Check specific Python 2 syntax patterns
            if key == "print" and "print " in content:
                # Check if this is actual code (not in comment/string)
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    if "print " in line and not line.strip().startswith('#'):
                        # Check character positions
                        pos = line.find("print ")
                        if not _is_in_comment_or_string(i, pos):
                            problematic_for_any = _check_if_problematic(rule, targets)
                            if problematic_for_any:
                                _add_warning(key, rule, ("3.0", f"REMOVED → {rule['note']}"))
                            break
            
            elif key == "xrange" and "xrange(" in content:
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    if "xrange(" in line and not line.strip().startswith('#'):
                        pos = line.find("xrange(")
                        if not _is_in_comment_or_string(i, pos):
                            problematic_for_any = _check_if_problematic(rule, targets)
                            if problematic_for_any:
                                _add_warning(key, rule, ("3.0", f"REMOVED → {rule['note']}"))
                            break
            
            elif key == "raw_input" and "raw_input(" in content:
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    if "raw_input(" in line and not line.strip().startswith('#'):
                        pos = line.find("raw_input(")
                        if not _is_in_comment_or_string(i, pos):
                            problematic_for_any = _check_if_problematic(rule, targets)
                            if problematic_for_any:
                                _add_warning(key, rule, ("3.0", f"REMOVED → {rule['note']}"))
                            break

            elif key == "unicode" and "unicode(" in content:
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    if "unicode(" in line and not line.strip().startswith('#'):
                        pos = line.find("unicode(")
                        if not _is_in_comment_or_string(i, pos):
                            problematic_for_any = _check_if_problematic(rule, targets)
                            if problematic_for_any:
                                _add_warning(key, rule, ("3.0", f"REMOVED → {rule['note']}"))
                            break

            elif key == "long" and "long(" in content:
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    if "long(" in line and not line.strip().startswith('#'):
                        pos = line.find("long(")
                        if not _is_in_comment_or_string(i, pos):
                            problematic_for_any = _check_if_problematic(rule, targets)
                            if problematic_for_any:
                                _add_warning(key, rule, ("3.0", f"REMOVED → {rule['note']}"))
                            break
        
            elif key == "basestring" and "basestring(" in content:
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    if "basestring(" in line and not line.strip().startswith('#'):
                        pos = line.find("basestring(")
                        if not _is_in_comment_or_string(i, pos):
                            problematic_for_any = _check_if_problematic(rule, targets)
                            if problematic_for_any:
                                _add_warning(key, rule, ("3.0", f"REMOVED → {rule['note']}"))
                            break
            
            elif key == "StringIO" and "StringIO" in content:
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    if "StringIO" in line and not line.strip().startswith('#'):
                        # Check if it's not io.StringIO (which is valid)
                        if "io.StringIO" not in line:
                            pos = line.find("StringIO")
                            if not _is_in_comment_or_string(i, pos):
                                problematic_for_any = _check_if_problematic(rule, targets)
                                if problematic_for_any:
                                    _add_warning(key, rule, ("3.0", f"REMOVED → {rule['note']}"))
                                break
            
            # For other features, be more careful about false positives
            elif key not in ["print", "xrange", "raw_input", "unicode", "long", "basestring", "StringIO"]:
                problematic_for_any = _check_if_problematic(rule, targets)
                if problematic_for_any:
                    if "removed_in" in rule:
                        _add_warning(key, rule, (rule["removed_in"], f"REMOVED → {rule['note']}"))
                    elif "added_in" in rule:
                        _add_warning(key, rule, (rule["added_in"], f"NOT AVAILABLE before {rule['added_in']} → {rule['note']}"))

    # === Check AST ===
    tree = None
    try:
        tree = ast.parse(content)
    except Exception:
        pass
    
    if tree:
        for node in ast.walk(tree):
        # Python 2-only AST nodes (safe check)
            if hasattr(ast, "Print") and isinstance(node, ast.Print):
                problematic = any(target >= version.parse("3.0") for target in targets)
                if problematic:
                    _add_warning("print_stmt", COMPAT_RULES["print"],
                                ("3.0", f"REMOVED → {COMPAT_RULES['print']['note']}"))

            if hasattr(ast, "Exec") and isinstance(node, ast.Exec):
                problematic = any(target >= version.parse("3.0") for target in targets)
                if problematic:
                    _add_warning("exec_stmt", COMPAT_RULES["exec"],
                                ("3.0", f"CHANGED → {COMPAT_RULES['exec']['note']}"))

            # Walrus operator := (Python 3.8+)
            if isinstance(node, ast.NamedExpr):
                problematic = any(target < version.parse("3.8") for target in targets)
                if problematic:
                    _add_warning("walrus", COMPAT_RULES["walrus"],
                                ("3.8", f"NOT AVAILABLE before 3.8 → {COMPAT_RULES['walrus']['note']}"))

            # Structural pattern matching (Python 3.10+)
            if hasattr(ast, "Match") and isinstance(node, ast.Match):
                problematic = any(target < version.parse("3.10") for target in targets)
                if problematic:
                    _add_warning("match", COMPAT_RULES["match"],
                                ("3.10", f"NOT AVAILABLE before 3.10 → {COMPAT_RULES['match']['note']}"))

            # Async/await keywords
            if isinstance(node, ast.AsyncFunctionDef):
                problematic = any(target < version.parse("3.5") for target in targets)
                if problematic:
                    _add_warning("async_kw", COMPAT_RULES["async"],
                                ("3.5", f"CHANGED since 3.5 → {COMPAT_RULES['async']['note']}"))

            if isinstance(node, ast.Await):
                problematic = any(target < version.parse("3.5") for target in targets)
                if problematic:
                    _add_warning("await_kw", COMPAT_RULES["await"],
                                ("3.5", f"CHANGED since 3.5 → {COMPAT_RULES['await']['note']}"))

            # F-strings (Python 3.6+)
            if isinstance(node, ast.JoinedStr):
                problematic = any(target < version.parse("3.6") for target in targets)
                if problematic:
                    _add_warning("fstrings", COMPAT_RULES["fstrings"],
                                ("3.6", f"NOT AVAILABLE before 3.6 → {COMPAT_RULES['fstrings']['note']}"))

    # === Output ===
    print(f"Compatibility Report for {module_name}")
    print(f"Target Python Version: {python_version if python_version else 'All versions 2.0-3.12'}")
    print("=" * 50)
    if not warnings:
        print("No compatibility issues detected.")
    else:
        print(f"{'Feature':<10} | {'Version':<7} | Warning")
        print("-" * 80)
        for feat, (ver, note) in warnings.items():
            print(f"{feat:<10} | {ver:<7} | {note}")
            
##################
# Help functions #
##################

def easter_egg(xrghzqxrghzq=None):
    "??????????"
    a= '''          #   #  #####  #       #        ##
          #   #  #      #       #       #  #
          #####  #####  #       #      #    #
          #   #  #      #       #       #  #
          #   #  #####  #####   #####    ##

      #           #   ##    ####    #      ###    #
       #    #    #   #  #   #   #   #      #  #   #
        #   #   #   #    #  ####    #      #  #   #
         # # # #     #  #   #  #    #      #  #   
          #   #       ##    #   #   #####  ###    #
     
                        #####     #
                       #     #   #
                       #     #  #
                        #####  #
                        ######
                        # #
                        # #
                       #  #
                       #  #
                       #  #
                         # #
                        #   #
                       #     #'''
    if xrghzqxrghzq == "abc":
        print(a)
    else:
        raise ValueError("^&*()^*&%^#$@$#^(*&%#^$%&*^$%$$!$#@$&(")
        sys.exit("!)@(#$&*%^&#R&#$)!!%$@&)#@*)^!$#&!%*^)!$@#)%!$")
        quit()

def modx_help():
    """
    Show full ModX help including all functions and example usage.
    """
    help_text = """
ModX — The Python Module Universe
=================================

Functions:
----------

import_all()
    Import almost every standard library module at once.
    Example: modx.import_all()

import_external()
    Import all installed third-party modules.
    Example: modx.import_external()

import_screen()
    Import common screen/GUI/game modules if available (pygame, turtle, tkinter, etc.).
    Example: modx.import_screen()

import_letter(letter)
    Import every standard library module starting with a given letter.
    Example: modx.import_letter('t')

import_random(n)
    Import n random standard library modules.
    Example: modx.import_random(5)

list_importall()
    Return a list of modules that import_all() would load.
    Example: modx.list_importall()

modules_loaded()
    Show how many total modules are currently loaded in sys.modules.
    Example: modx.modules_loaded()

dependencies()
    Show what other modules a specific module depends on without importing it.
    Example: modx.dependencies("random")

imported()
    Show ALL modules imported after ModX loaded (user + ModX + dependencies).
    Example: modx.imported()

modx_imported()
    Show ONLY the modules imported directly via ModX functions (excluding dependencies).
    Example: modx.modximported()

nonimported()
    Return a list of standard library modules not yet imported.
    Example: modx.nonimported()

info(module_name)
    Show information about a module.
    Example: modx.info('random')

search_modules(keyword)
    Search for modules whose names contain the keyword.
    Example: modx.search_modules('html')

is_imported(module_name)
    Check if a module is currently imported.
    Example: modx.isimported('random')

vcompat(module_name, python_version)
    Check if a module works with different Python versions
    Example: modx.vcompat('pygame')

modx_help()
    Show this help screen.
    Example: modx.modxhelp()
"""
    print(help_text)
