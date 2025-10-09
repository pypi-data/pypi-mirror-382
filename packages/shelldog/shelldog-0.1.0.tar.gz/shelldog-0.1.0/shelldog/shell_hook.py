# ## shelldog/shell_hook.py


import os
import sys
import subprocess
from pathlib import Path

class ShellHook:
    """Manages shell hook integration for command tracking."""
    
    def __init__(self):
        # Detect if we're in a virtual environment
        in_venv = hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        )
        
        if in_venv:
            # Store in the venv directory
            venv_path = Path(sys.prefix)
            self.shelldog_dir = venv_path / ".shelldog"
        else:
            # Fallback to home directory
            self.shelldog_dir = Path.home() / ".shelldog"
        
        self.hook_file = self.shelldog_dir / "shelldog_hook.sh"
        self.logger_script = self.shelldog_dir / "log_command.py"
        
        # Ensure directory exists
        self.shelldog_dir.mkdir(exist_ok=True)
    
    def create_logger_script(self):
        """Create the Python script that logs commands."""
        # Get the python executable from current venv
        python_exec = sys.executable
        
        logger_script_content = f'''#!/usr/bin/env python3
import sys
import os

# Use the venv python
sys.executable = "{python_exec}"

# Add shelldog to path if needed
try:
    from shelldog.logger import ShelldogLogger
except ImportError:
    # If shelldog not in path, skip silently
    sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = " ".join(sys.argv[1:])
        logger = ShelldogLogger()
        logger.log_command(command)
'''
        
        with open(self.logger_script, 'w') as f:
            f.write(logger_script_content)
        
        # Make it executable
        os.chmod(self.logger_script, 0o755)
    
    def create_shell_hook(self):
        """Create the shell hook script."""
        # Use the venv python
        python_exec = sys.executable
        
        hook_content = f'''# Shelldog command tracking hook
# This script is sourced by your shell to track commands

# Store the original DEBUG trap if it exists
_shelldog_original_debug_trap="$(trap -p DEBUG)"

# Counter to track DEBUG trap calls (to avoid logging the same command multiple times)
_shelldog_last_cmd=""

# Function to log commands
_shelldog_log_command() {{
    local cmd="$BASH_COMMAND"
    
    # Skip if empty, shelldog command, or internal function
    if [[ -z "$cmd" ]] || [[ "$cmd" == *"shelldog"* ]] || [[ "$cmd" == *"_shelldog_"* ]]; then
        return
    fi
    
    # Avoid logging the same command twice (DEBUG fires multiple times)
    if [[ "$cmd" != "$_shelldog_last_cmd" ]]; then
        _shelldog_last_cmd="$cmd"
        "{python_exec}" "{self.logger_script}" "$cmd" 2>/dev/null &
        wait $! 2>/dev/null
    fi
}}

# Set up the DEBUG trap for Bash
if [ -n "$BASH_VERSION" ]; then
    trap '_shelldog_log_command' DEBUG
fi

# Set up preexec for Zsh
if [ -n "$ZSH_VERSION" ]; then
    preexec() {{
        local cmd="$1"
        if [[ -z "$cmd" ]] || [[ "$cmd" == *"shelldog"* ]] || [[ "$cmd" == *"_shelldog_"* ]]; then
            return
        fi
        "{python_exec}" "{self.logger_script}" "$cmd" 2>/dev/null
    }}
fi

# Export a variable so we know the hook is active
export SHELLDOG_ACTIVE=1
'''
        
        with open(self.hook_file, 'w') as f:
            f.write(hook_content)
        
        return self.hook_file
    
    def get_activation_command(self):
        """Get the command to activate the shell hook."""
        return f"source {self.hook_file}"
    
    def create_unhook_script(self):
        """Create script to remove the hook."""
        unhook_file = self.shelldog_dir / "shelldog_unhook.sh"
        unhook_content = '''# Shelldog unhook script
# Remove the command tracking hook

# Remove DEBUG trap for Bash
if [ -n "$BASH_VERSION" ]; then
    trap - DEBUG
    # Restore original trap if it existed
    if [ -n "$_shelldog_original_debug_trap" ]; then
        eval "$_shelldog_original_debug_trap"
    fi
fi

# Remove preexec for Zsh
if [ -n "$ZSH_VERSION" ]; then
    unset -f preexec 2>/dev/null
fi

# Unset the active flag
unset SHELLDOG_ACTIVE

# Friendly message
echo "🐕 *yawn* Shelldog stopped watching. See you later!"
'''
        
        with open(unhook_file, 'w') as f:
            f.write(unhook_content)
        
        return unhook_file
    
    def install_hook(self):
        """Install the shell hook."""
        # Create both the logger script and hook
        self.create_logger_script()
        hook_file = self.create_shell_hook()
        unhook_file = self.create_unhook_script()
        
        return hook_file, unhook_file
    
    def is_hook_active(self):
        """Check if the hook is currently active in the shell."""
        return os.environ.get('SHELLDOG_ACTIVE') == '1'