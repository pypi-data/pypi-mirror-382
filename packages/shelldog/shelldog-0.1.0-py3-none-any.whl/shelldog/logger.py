# shelldog/logger.py
import os
import re
import sys
from datetime import datetime
from pathlib import Path

class ShelldogLogger:
    """Handles logging of shell commands with masking of sensitive data."""
    
    def __init__(self):
        # Detect if we're in a virtual environment
        self.in_venv = hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        )
        
        if self.in_venv:
            # Get the venv root directory (parent of bin, lib, etc.)
            venv_path = Path(sys.prefix)
            
            # Try to find the project root (parent of venv)
            # Assume venv is named 'venv' or similar
            venv_name = venv_path.name
            project_root = venv_path.parent
            
            # Store log file at project root level (same level as venv folder)
            self.log_file = project_root / "shelldog_history.txt"
            
            # Keep .shelldog hidden folder inside venv for state and other files
            self.shelldog_dir = venv_path / ".shelldog"
        else:
            # Fallback to home directory
            self.shelldog_dir = Path.home() / ".shelldog"
            self.log_file = self.shelldog_dir / "shelldog_history.txt"
        
        self.state_file = self.shelldog_dir / ".shelldog_state"
        
        # Ensure directory exists
        self.shelldog_dir.mkdir(exist_ok=True)
    
    def is_tracking(self):
        """Check if tracking is currently active."""
        if not self.state_file.exists():
            return False
        
        try:
            with open(self.state_file, 'r') as f:
                state = f.read().strip()
                return state == "active"
        except:
            return False
    
    def start_tracking(self):
        """Enable tracking."""
        with open(self.state_file, 'w') as f:
            f.write("active")
    
    def stop_tracking(self):
        """Disable tracking."""
        with open(self.state_file, 'w') as f:
            f.write("inactive")
    
    def should_log_command(self, command):
        """Determine if a command should be logged."""
        if not command or not command.strip():
            return False
        
        # Ignore shelldog commands themselves
        if command.strip().startswith("shelldog"):
            return False
        
        # Ignore internal shell stuff
        ignore_patterns = [
            r'^__vsc_prompt',
            r'^\[\s*\d+\]',
            r'^trap\s',
        ]
        
        for pattern in ignore_patterns:
            if re.match(pattern, command.strip()):
                return False
        
        # Log ALL commands EXCEPT the ignored ones above
        return True
    
    def mask_sensitive_data(self, command):
        """Mask sensitive information in commands."""
        # Don't mask SHELLDOG_ACTIVE or other shelldog internal vars
        if 'SHELLDOG_ACTIVE' in command:
            return command
        
        # Mask export/set variable VALUES ONLY (not the command or variable name)
        patterns = [
            # For export VARNAME=value → export VARNAME=****
            (r'(export\s+(?!SHELLDOG)\w+)=([^\s]+)', r'\1=****'),
            # For set VARNAME=value → set VARNAME=****
            (r'(set\s+(?!SHELLDOG)\w+)=([^\s]+)', r'\1=****'),
            # Mask common sensitive flags
            (r'(--password[=\s]+)([^\s]+)', r'\1****'),
            (r'(--token[=\s]+)([^\s]+)', r'\1****'),
            (r'(--api[-_]?key[=\s]+)([^\s]+)', r'\1****'),
            (r'(--secret[=\s]+)([^\s]+)', r'\1****'),
            # Mask authorization headers
            (r'(Authorization:\s*)([^\s]+)', r'\1****'),
            (r'(-H\s+["\']Authorization:\s*)([^"\']+)', r'\1****'),
        ]
        
        masked_command = command
        for pattern, replacement in patterns:
            masked_command = re.sub(pattern, replacement, masked_command, flags=re.IGNORECASE)
        
        return masked_command
    
    def log_command(self, command):
        """Log a command to the history file."""
        if not self.is_tracking():
            return
        
        if not self.should_log_command(command):
            return
        
        # Mask sensitive data
        masked_command = self.mask_sensitive_data(command)
        
        # Create log entry
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {masked_command}\n"
        
        # Append to log file
        with open(self.log_file, 'a') as f:
            f.write(log_entry)
    
    def get_log_content(self):
        """Retrieve all log content."""
        if not self.log_file.exists():
            return "No commands logged yet. 🐕"
        
        with open(self.log_file, 'r') as f:
            return f.read()
    
    def clear_log(self):
        """Clear the log file."""
        if self.log_file.exists():
            self.log_file.unlink()