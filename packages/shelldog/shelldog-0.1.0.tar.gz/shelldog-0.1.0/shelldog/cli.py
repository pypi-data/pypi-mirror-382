# shelldog/cli.py
import click
import sys
import random
from .logger import ShelldogLogger
from .shell_hook import ShellHook

# Fun dog phrases
BARK_PHRASES = [
    "🐕 WOOF WOOF! *tail wagging intensifies*",
    "🐕 Bark bark! I'm the goodest boy!",
    "🐕 *sniffs around* Something smells like... code!",
    "🐕 BORK! Time to chase some bugs!",
    "🐕 Awoo! Let me track those commands for you!",
    "🐕 *happy dog noises* WOOF!",
    "🐕 Bork bork! Ready to guard your history!",
    "🐕 *excited barking* Let's do this hooman!",
]

TREAT_PHRASES = [
    "🐕 *catches treat* NOM NOM NOM! You're the best hooman!",
    "🐕 *happy dance* TREAT! My favorite! Just like this code!",
    "🐕 *munches* Mmm... tastes like... SUCCESS!",
    "🐕 *tail wagging at maximum speed* THANK YOU THANK YOU!",
    "🐕 Om nom nom! Can I have another? Please? 🥺",
]

GOODBOY_PHRASES = [
    "🐕 *tail wagging* I'M A GOOD BOY! I'M A GOOD BOY!",
    "🐕 *rolls over* Belly rubs AND compliments?! Best day ever!",
    "🐕 *happy tippy taps* You think I'm good? YOU'RE GOOD!",
    "🐕 *sits proudly* I've been tracking all your commands like a CHAMP!",
    "🐕 *puppy eyes* Really? I'm doing a good job? 🥺",
]

MOTIVATIONAL_PHRASES = [
    "You got this, hooman! 💪",
    "Every great developer was once a beginner! 🌟",
    "Bugs are just features in disguise! 🐛➡️✨",
    "Remember: commit early, commit often! 🔄",
    "Stay pawsitive! 🐾",
    "You're not stuck, you're just between solutions! 🧩",
]

def bark_art():
    """Display the shelldog ASCII art."""
    art = """
🐕 Woof! I'm watching you.

    Never forget what you did.
    Always know where you've been.
    I've got your back.
"""
    click.echo(art)

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """Shelldog - Silent command tracker for development environments."""
    if ctx.invoked_subcommand is None:
        bark_art()
        click.echo("\n🐕 Available commands:")
        click.echo("  shelldog follow     - Start tracking commands")
        click.echo("  shelldog stop       - Stop tracking commands")
        click.echo("  shelldog log        - View command history")
        click.echo("  shelldog status     - Check tracking status")
        click.echo("  shelldog clear      - Clear command history")
        click.echo("  shelldog bark       - Make me bark!")
        click.echo("  shelldog treat      - Give me a treat!")
        click.echo("  shelldog goodboy    - Tell me I'm a good boy!")
        click.echo("\n💡 Tip: Run 'shelldog <command> --help' for more info")

@cli.command()
@click.option('--quiet', '-q', is_flag=True, help='Quiet mode - minimal output')
def follow(quiet):
    """Start silent command tracking."""
    logger = ShelldogLogger()
    hook = ShellHook()
    
    # Install the shell hook
    hook_file, unhook_file = hook.install_hook()
    
    # Enable tracking
    logger.start_tracking()
    
    if quiet:
        # In quiet mode, output the source command for eval
        click.echo(f"source {hook_file}")
    else:
        bark_art()
        click.echo("✓ Shelldog is now following your commands!")
        click.echo(f"\n📝 Commands will be logged to:")
        
        if logger.in_venv:
            click.echo(f"   {logger.log_file}")
            click.echo("   🎯 Project root level logging!")
        else:
            click.echo(f"   {logger.log_file}")
        
        click.echo(f"\n🎉 {random.choice(MOTIVATIONAL_PHRASES)}")
        click.echo("=" * 60)
        click.echo("\n✓ Initialization complete!")
        click.echo("=" * 60)
        click.echo("\n🐕 Activate the hook by running:")
        click.echo(f"   eval \"$(shelldog follow -q)\"")
        click.echo("\n   Or manually:")
        click.echo(f"   source {hook_file}")
        click.echo("\n🐕 Woof! I'm watching... silently.")

@cli.command()
def stop():
    """Stop command tracking."""
    logger = ShelldogLogger()
    hook = ShellHook()
    
    # Disable tracking
    logger.stop_tracking()
    
    unhook_file = hook.shelldog_dir / "shelldog_unhook.sh"
    
    click.echo("🐕 *sad whimper* Okay... I'll stop watching...")
    click.echo("\n✓ Tracking disabled")
    click.echo(f"\n⚠️  To remove the hook from your current shell:")
    click.echo(f"   source {unhook_file}")
    click.echo("\n🐕 I'll be here when you need me again! *tail wag*")

@cli.command()
@click.option('--tail', '-n', type=int, help='Show only last N entries')
@click.option('--today', is_flag=True, help='Show only today\'s commands')
def log(tail, today):
    """Display the command history."""
    logger = ShelldogLogger()
    
    content = logger.get_log_content()
    
    if not content or content.strip() == "" or "No commands" in content:
        click.echo("🐕 *sniffs around* No commands logged yet!")
        click.echo("\n   Run 'shelldog follow' to start tracking!")
        click.echo(f"   Then activate: source {logger.shelldog_dir}/shelldog_hook.sh")
        if logger.in_venv:
            click.echo(f"\n   📍 Current venv log: {logger.log_file}")
        return
    
    lines = content.strip().split('\n')
    
    if today:
        from datetime import datetime
        today_str = datetime.now().strftime("%Y-%m-%d")
        lines = [line for line in lines if today_str in line]
    
    if tail and tail > 0:
        lines = lines[-tail:]
    
    click.echo("🐕 Shelldog History:\n")
    if logger.in_venv:
        click.echo(f"📍 Venv: {sys.prefix}")
    click.echo("=" * 80)
    for line in lines:
        click.echo(line)
    click.echo("=" * 80)
    click.echo(f"\n📊 Total entries: {len(lines)}")
    
    if len(lines) > 0:
        click.echo(f"🐕 *proud tail wag* I remembered everything!")

@cli.command()
def status():
    """Check if shelldog is currently tracking."""
    logger = ShelldogLogger()
    hook = ShellHook()
    
    is_tracking = logger.is_tracking()
    is_hooked = hook.is_hook_active()
    
    click.echo("🐕 Shelldog Status:\n")
    click.echo("=" * 50)
    click.echo(f"Tracking enabled:    {'✓ Yes' if is_tracking else '✗ No'}")
    click.echo(f"Shell hook active:   {'✓ Yes' if is_hooked else '✗ No'}")
    
    if logger.in_venv:
        click.echo(f"Virtual env:         ✓ Yes (venv-specific logging)")
        click.echo(f"Venv path:           {sys.prefix}")
    else:
        click.echo(f"Virtual env:         ✗ No (using global log)")
    
    click.echo(f"Log file:            {logger.log_file}")
    click.echo(f"Log file exists:     {'✓ Yes' if logger.log_file.exists() else '✗ No'}")
    
    if logger.log_file.exists():
        with open(logger.log_file, 'r') as f:
            line_count = len(f.readlines())
        click.echo(f"Logged commands:     {line_count}")
    
    click.echo("=" * 50)
    
    if is_tracking and not is_hooked:
        click.echo("\n⚠️  Warning: Tracking is enabled but shell hook is not active!")
        click.echo(f"🐕 *puppy eyes* Please run: source {hook.hook_file}")
    elif not is_tracking and is_hooked:
        click.echo("\n⚠️  Warning: Shell hook is active but tracking is disabled!")
        click.echo("🐕 Run: shelldog follow")
    elif is_tracking and is_hooked:
        click.echo("\n✓ Shelldog is actively tracking your commands! 🐕")
        click.echo(f"   {random.choice(MOTIVATIONAL_PHRASES)}")
    else:
        click.echo("\n🐕 Shelldog is idle. *yawn* Run 'shelldog follow' to wake me up!")

@cli.command()
@click.confirmation_option(prompt='🐕 Are you sure? This will erase all my memories!')
def clear():
    """Clear the command history."""
    logger = ShelldogLogger()
    logger.clear_log()
    click.echo("🐕 *shakes head vigorously* All clean! Starting fresh!")
    click.echo("   Command history cleared. It's like it never happened! 🧹")

@cli.command()
def bark():
    """Make shelldog bark! 🐕"""
    click.echo(random.choice(BARK_PHRASES))

@cli.command()
def treat():
    """Give shelldog a treat! 🦴"""
    click.echo(random.choice(TREAT_PHRASES))

@cli.command()
def goodboy():
    """Tell shelldog he's a good boy! 🏆"""
    click.echo(random.choice(GOODBOY_PHRASES))

@cli.command()
def stats():
    """Show detailed statistics about your tracked commands."""
    logger = ShelldogLogger()
    
    if not logger.log_file.exists():
        click.echo("🐕 No stats yet! Start tracking to see cool statistics!")
        return
    
    with open(logger.log_file, 'r') as f:
        lines = f.readlines()
    
    if not lines:
        click.echo("🐕 No commands tracked yet!")
        return
    
    # Count command types
    command_counts = {}
    for line in lines:
        if ']' in line:
            cmd = line.split(']', 1)[1].strip().split()[0] if ']' in line else ''
            command_counts[cmd] = command_counts.get(cmd, 0) + 1
    
    click.echo("🐕 Shelldog Statistics:\n")
    click.echo("=" * 50)
    click.echo(f"Total commands tracked:  {len(lines)}")
    click.echo(f"\nTop commands:")
    for cmd, count in sorted(command_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        click.echo(f"  {cmd:20} {count:>4} times")
    click.echo("=" * 50)
    click.echo("\n🐕 *impressed* You've been busy, hooman!")

if __name__ == '__main__':
    cli()