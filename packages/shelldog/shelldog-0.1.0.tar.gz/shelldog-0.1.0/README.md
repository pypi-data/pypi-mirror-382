# 🐕 Shelldog - Your Faithful Command Companion

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> *Your loyal companion for tracking shell commands - because every good developer needs a faithful friend who remembers everything!*

```
    /\_/\  
   ( o.o ) 
    > ^ <   "Woof! I'm watching... silently."
```

**Shelldog** is a silent, intelligent command tracker for your terminal. Think of it as your development diary that writes itself - tracking every command you run, so you never have to remember "what did I do yesterday?" ever again!

## 🎯 Why Shelldog?

Ever found yourself thinking:
- "What was that curl command I ran last week?"
- "How did I set up this environment again?"
- "I need to write documentation... if only I could remember what I did!"
- "What commands did I run before that bug appeared?"

**Shelldog sits quietly in the background and remembers EVERYTHING for you!** 🧠

### ✨ Features

- 🤫 **Silent Tracking** - Works invisibly without cluttering your terminal
- 🔒 **Privacy First** - Automatically masks passwords, tokens, and API keys
- 🎯 **Smart Detection** - Knows when you're in a virtual environment
- 📁 **Project-Level Logs** - Each venv gets its own history file at the project root
- 🎭 **Personality** - Because who says CLI tools have to be boring?
- 🚀 **Zero Performance Impact** - Logs asynchronously in the background
- 🌈 **Both Bash & Zsh** - Works with your favorite shell

## 📦 Installation

### Quick Install

```bash
pip install shelldog
```

### From Source

```bash
git clone https://github.com/Ansumanbhujabal/shelldog.git
cd shelldog
pip install -e .
```

## 🚀 Quick Start

### 1. Start Tracking

```bash
# Wake up the dog!
shelldog follow

# Activate tracking in your current shell
eval "$(shelldog follow -q)"
```

That's it! Shelldog is now silently logging all your commands. 🎉

### 2. View Your History

```bash
# See everything
shelldog log

# Just today's commands
shelldog log --today

# Last 20 commands
shelldog log -n 20
```

### 3. Check Status

```bash
shelldog status
```

## 🎮 Commands

### Core Commands

| Command | Description |
|---------|-------------|
| `shelldog follow` | Start tracking commands (activates the good boy!) |
| `shelldog stop` | Stop tracking (sends doggo to sleep) |
| `shelldog log` | View command history |
| `shelldog status` | Check if Shelldog is watching |
| `shelldog clear` | Clear command history |
| `shelldog stats` | See cool statistics about your commands |

### Fun Commands (Because Why Not?)

| Command | Description |
|---------|-------------|
| `shelldog bark` | Make Shelldog bark! 🐕 |
| `shelldog treat` | Give Shelldog a treat! 🦴 |
| `shelldog goodboy` | Tell Shelldog he's a good boy! 🏆 |

## 🔧 How It Works

### The Magic Behind the Scenes

1. **Shell Hook**: Shelldog installs a tiny hook in your shell (via `DEBUG` trap in Bash or `preexec` in Zsh)
2. **Silent Logger**: Every command gets logged asynchronously - zero impact on your workflow
3. **Smart Masking**: Sensitive data (passwords, tokens, API keys) are automatically masked
4. **Venv Detection**: Automatically detects if you're in a virtual environment

### Virtual Environment Awareness

When you're in a virtual environment:
- Shelldog creates `shelldog_history.txt` at your **project root** (next to your venv folder)
- Each project gets its own command history
- No more mixing up commands from different projects!

```
my-project/
├── venv/
│   └── .shelldog/          # Hidden config folder
├── shelldog_history.txt     # Your project's command history! 📝
├── src/
└── README.md
```

### Privacy & Security

Shelldog automatically masks sensitive information:

```bash
# What you type:
export API_KEY=super_secret_key_123

# What gets logged:
export API_KEY=****
```

Protected patterns:
- `export VARNAME=value` → `export VARNAME=****`
- `--password`, `--token`, `--api-key`, `--secret`
- Authorization headers in curl commands
- And more!

## 💡 Usage Examples

### Example 1: Track Your Development Session

```bash
# Start your day
cd my-project
source venv/bin/activate
eval "$(shelldog follow -q)"

# Do your work
git pull origin main
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# Later, review what you did
shelldog log --today
```

### Example 2: Debug Like a Pro

```bash
# Something broke! What did you do?
shelldog log -n 50

# Find that specific command
shelldog log | grep docker

# See statistics
shelldog stats
```

### Example 3: Document Your Setup

```bash
# After setting up a new environment
shelldog log > SETUP.md

# Now you have automatic documentation! 📚
```

## 🎨 Example Output

### Starting Shelldog

```bash
$ shelldog follow

🐕 Woof! I'm watching you.

    Never forget what you did.
    Always know where you've been.
    I've got your back.

✓ Shelldog is now following your commands!

📝 Commands will be logged to:
   /path/to/project/shelldog_history.txt
   🎯 Project root level logging!

🎉 Stay pawsitive! 🐾
============================================================

✓ Initialization complete!
============================================================

🐕 Activate the hook by running:
   eval "$(shelldog follow -q)"
```

### Viewing History

```bash
$ shelldog log -n 5

🐕 Shelldog History:

================================================================================
[2025-10-08 14:23:45] pip install requests
[2025-10-08 14:24:12] python app.py
[2025-10-08 14:25:33] git add .
[2025-10-08 14:25:40] git commit -m "Add new feature"
[2025-10-08 14:25:55] git push origin main
================================================================================

📊 Total entries: 5
🐕 *proud tail wag* I remembered everything!
```

### Status Check

```bash
$ shelldog status

🐕 Shelldog Status:

==================================================
Tracking enabled:    ✓ Yes
Shell hook active:   ✓ Yes
Virtual env:         ✓ Yes (venv-specific logging)
Venv path:           /opt/CodeRepo/SideProjects/shelldog/venv
Log file:            /opt/CodeRepo/SideProjects/shelldog/shelldog_history.txt
Log file exists:     ✓ Yes
Logged commands:     247
==================================================

✓ Shelldog is actively tracking your commands! 🐕
   Every great developer was once a beginner! 🌟
```

## ⚙️ Configuration

### Log File Locations

- **In a venv**: `<project_root>/shelldog_history.txt`
- **Global**: `~/.shelldog/shelldog_history.txt`

### State Files

Shelldog keeps its configuration in:
- **In a venv**: `<venv>/.shelldog/`
- **Global**: `~/.shelldog/`

## 🤝 Shell Integration

### Manual Activation

If you want to manually control when Shelldog watches:

```bash
# Start tracking
source ~/.shelldog/shelldog_hook.sh

# Stop tracking
source ~/.shelldog/shelldog_unhook.sh
```

### Add to Shell Profile (Optional)

Want Shelldog to start automatically? Add to your `~/.bashrc` or `~/.zshrc`:

```bash
# Auto-start Shelldog in virtual environments
if [[ -n "$VIRTUAL_ENV" ]]; then
    eval "$(shelldog follow -q)" 2>/dev/null
fi
```

## 🐛 Troubleshooting

### "Shelldog is enabled but not logging!"

Make sure the hook is active:

```bash
shelldog status

# If hook is not active, run:
eval "$(shelldog follow -q)"
```

### "Commands are logged twice!"

This can happen if you source the hook multiple times. Run:

```bash
shelldog stop
eval "$(shelldog follow -q)"
```

### "Shelldog logs its own commands!"

It shouldn't! Shelldog filters itself out. If you see this, please file a bug report! 🐛

## 📝 What Gets Logged?

### ✅ Logged
- All shell commands
- Script executions
- Git commands
- Package installations
- Database migrations
- Server starts/stops
- Basically everything you type!

### ❌ Not Logged
- `shelldog` commands themselves
- Internal shell functions
- Empty commands
- Shell initialization stuff

## 🎓 Pro Tips

1. **Review Daily**: `shelldog log --today` at the end of the day
2. **Document Projects**: `shelldog log > COMMANDS.md` for documentation
3. **Debug Sessions**: `shelldog log -n 50` to see recent commands
4. **Find Patterns**: `shelldog stats` to see your most-used commands
5. **Clean Slate**: `shelldog clear` when starting fresh

## 🤔 FAQ

**Q: Does Shelldog slow down my terminal?**  
A: Nope! Logging happens asynchronously in the background. Zero performance impact.

**Q: Is my sensitive data safe?**  
A: Yes! Shelldog automatically masks passwords, tokens, and API keys.

**Q: Can I use this in production?**  
A: Shelldog is designed for development environments. Use caution in production!

**Q: Does it work with tmux/screen?**  
A: Yes! Each session tracks independently.

**Q: What shells are supported?**  
A: Bash and Zsh are fully supported.

## 🎨 Why the Dog Theme?

Because:
1. Dogs are loyal (like your command history should be)
2. Dogs remember everything (especially treats)
3. Dogs are always happy to help
4. CLI tools deserve more personality! 🎉

## 📄 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions are welcome! Feel free to:
- 🐛 Report bugs
- 💡 Suggest features
- 🔧 Submit pull requests
- 🎨 Improve documentation

## 🙏 Acknowledgments

Built with ❤️ by developers who got tired of asking "wait, what command did I just run?"

---

<div align="center">

**Made with 🐕 and ☕ by Ansuman Bhujabala**

If Shelldog helps you, give him a treat! ⭐ this repo

```
🐕 *tail wagging intensifies*
```

</div>
