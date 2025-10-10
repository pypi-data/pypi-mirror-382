import argparse
import shutil
import sys
from pathlib import Path
from typing import Optional
import os # For path joining

# Ensure this path is correct for your project structure
# DIETNB_STARTUP_SCRIPT_CONTENT will be read from the _startup.py file directly

def find_ipython_startup_dir() -> Optional[Path]:
    """Finds the default IPython profile's startup directory."""
    try:
        from IPython.paths import get_ipython_dir
        ip_dir = Path(get_ipython_dir())
        profile_dir = ip_dir / 'profile_default'
        startup_dir = profile_dir / 'startup'
        return startup_dir
    except ImportError:
        return None
    except Exception as e:
        return None

def get_ipython_dir() -> str:
    """Returns the IPython directory path."""
    from IPython.paths import get_ipython_dir as ip_get_ipython_dir
    return ip_get_ipython_dir()

def install_startup_script():
    """Installs the dietnb startup script for IPython."""
    try:
        ipython_dir_str = get_ipython_dir()
        if not ipython_dir_str: # Should not happen if IPython is installed
            raise ImportError("IPython directory not found.")
            
        ipython_dir = Path(ipython_dir_str)
        startup_dir = ipython_dir / "profile_default" / "startup"
        startup_dir.mkdir(parents=True, exist_ok=True)
        
        # Path to the _startup.py file within the dietnb package
        # __file__ is the path to the current file (_cli.py)
        # .parent gives the directory of _cli.py (dietnb/dietnb/)
        # then we navigate to _startup.py
        source_startup_script_path = Path(__file__).parent / "_startup.py"

        if not source_startup_script_path.is_file():
            print(f"Error: Source startup script not found. Installation failed.", file=sys.stderr)
            return False
            
        script_name = "00-dietnb.py" # Ensure it runs early
        target_script_path = startup_dir / script_name
        
        # Read content from source and write to target
        with open(source_startup_script_path, "r") as src_f, open(target_script_path, "w") as dest_f:
            dest_f.write(src_f.read())
        
        print(f"dietnb startup script installed to: {target_script_path}")
        print("Please restart your IPython/Jupyter kernel for changes to take effect.")
        print("dietnb will now attempt to activate automatically.")
        return True

    except ImportError:
        print("IPython is not installed or not found. Cannot install startup script.", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Error installing dietnb startup script: {e}", file=sys.stderr)
        return False

def uninstall_startup_script():
    """Uninstalls the dietnb startup script for IPython."""
    try:
        startup_dir = find_ipython_startup_dir()
        if not startup_dir:
            print("IPython startup directory not found. Cannot uninstall script.", file=sys.stderr)
            return False
        
        script_name = "00-dietnb.py"
        target_script_path = startup_dir / script_name

        if target_script_path.is_file():
            try:
                target_script_path.unlink()
                print(f"dietnb startup script removed from: {target_script_path}")
                print("Changes will take effect the next time you start IPython/Jupyter.")
                return True
            except OSError as e:
                print(f"Error removing startup script {target_script_path}: {e}", file=sys.stderr)
                return False
        else:
            print(f"dietnb startup script not found at {target_script_path}. Nothing to uninstall.")
            return True # It's not an error if the file isn't there
            
    except ImportError: # Should be caught by find_ipython_startup_dir, but double-check
        print("IPython is not installed or not found. Cannot uninstall startup script.", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Error uninstalling dietnb startup script: {e}", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(description="dietnb command line utility.")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Install command
    parser_install = subparsers.add_parser('install', help='Install the IPython startup script for automatic activation.')
    parser_install.set_defaults(func=install_startup_script)

    # Uninstall command
    parser_uninstall = subparsers.add_parser('uninstall', help='Uninstall the IPython startup script.')
    parser_uninstall.set_defaults(func=uninstall_startup_script)

    args = parser.parse_args()

    if hasattr(args, 'func'):
        success = args.func()
        sys.exit(0 if success else 1)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main() 