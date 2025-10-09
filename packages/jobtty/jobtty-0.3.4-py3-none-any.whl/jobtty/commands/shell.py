"""
Shell Integration Commands
Aliases, completion, and terminal magic
"""

import click
import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

from ..core.display import console, show_error, show_success

@click.group()
def shell():
    """🐚 Shell integration and terminal magic"""
    pass

@shell.command()
@click.option('--shell-type', type=click.Choice(['bash', 'zsh', 'fish']), help='Shell type (auto-detected if not specified)')
def setup(shell_type):
    """Setup shell aliases and completion"""
    
    if not shell_type:
        shell_type = os.environ.get('SHELL', '').split('/')[-1]
        if shell_type not in ['bash', 'zsh', 'fish']:
            shell_type = 'zsh'  # Default for macOS
    
    console.print(f"🔧 Setting up shell integration for: [cyan]{shell_type}[/cyan]")
    
    # Generate shell-specific setup
    if shell_type == 'zsh':
        setup_zsh()
    elif shell_type == 'bash':
        setup_bash()
    elif shell_type == 'fish':
        setup_fish()

def setup_zsh():
    """Setup Zsh integration"""
    
    zsh_config = '''
# Jobtty.io Terminal Job Board - Shell Integration
# Added by: jobtty shell setup

# Quick aliases
alias jj="jobtty"
alias jjsearch="jobtty search"
alias jjlist="jobtty searches list"
alias jjdaemon="jobtty daemon"

# Job hunting workflow aliases
alias findjobs="jobtty search"
alias savejob="jobtty save"
alias myjobs="jobtty list --saved"
alias jobstats="jobtty searches stats"

# Notification control
alias notifications-on="jobtty daemon start"
alias notifications-off="jobtty daemon stop"
alias check-jobs="jobtty daemon test"

# Quick job actions (for notifications)
alias apply="jobtty apply"
alias nope="jobtty dismiss"

# Challenge workflow
alias challenge="jobtty challenge"
alias submit="jobtty git submit"

# Function: Smart job search with automatic save
function smartjob() {
    jobtty search "$1" --save --location "${2:-London}" --frequency "${3:-instant}"
}

# Function: Quick job apply
function quickapply() {
    jobtty apply "$1" --quick
}

# Completion for jobtty commands
eval "$(_JOBTTY_COMPLETE=zsh_source jobtty)" 2>/dev/null || true

# Welcome message
echo "🚀 Jobtty shell integration loaded! Use 'jj' for quick access."
'''
    
    # Write to .zshrc
    zshrc = Path.home() / ".zshrc"
    
    console.print("📝 Writing to ~/.zshrc...")
    
    with open(zshrc, 'a') as f:
        f.write(f"\n{zsh_config}\n")
    
    show_success("✅ Zsh integration setup complete!")
    console.print("\n💡 [bold]Restart your terminal[/bold] or run: [cyan]source ~/.zshrc[/cyan]")

def setup_bash():
    """Setup Bash integration"""
    
    bash_config = '''
# Jobtty.io Terminal Job Board - Shell Integration
# Added by: jobtty shell setup

# Quick aliases  
alias jj="jobtty"
alias jjsearch="jobtty search"
alias jjlist="jobtty searches list"
alias findjobs="jobtty search"
alias notifications-on="jobtty daemon start"
alias notifications-off="jobtty daemon stop"

# Bash completion
eval "$(_JOBTTY_COMPLETE=bash_source jobtty)" 2>/dev/null || true

echo "🚀 Jobtty shell integration loaded!"
'''
    
    bashrc = Path.home() / ".bashrc"
    
    with open(bashrc, 'a') as f:
        f.write(f"\n{bash_config}\n")
    
    show_success("✅ Bash integration setup complete!")

def setup_fish():
    """Setup Fish shell integration"""
    
    fish_config = '''
# Jobtty.io shell integration
alias jj="jobtty"
alias findjobs="jobtty search"
alias notifications-on="jobtty daemon start"

function smartjob
    jobtty search $argv[1] --save --location (if test (count $argv) -gt 1; echo $argv[2]; else; echo "London"; end)
end

echo "🚀 Jobtty Fish integration loaded!"
'''
    
    fish_dir = Path.home() / ".config" / "fish"
    fish_dir.mkdir(exist_ok=True)
    
    fish_config_file = fish_dir / "config.fish"
    
    with open(fish_config_file, 'a') as f:
        f.write(f"\n{fish_config}\n")
    
    show_success("✅ Fish integration setup complete!")

@shell.command()
def aliases():
    """Show all available shell aliases"""
    
    console.print(Panel.fit(
        """
[bold cyan]🐚 JOBTTY SHELL ALIASES[/bold cyan]

[yellow]Quick Access:[/yellow]
• [green]jj[/green] = jobtty (super quick!)
• [green]jjsearch[/green] = jobtty search
• [green]jjlist[/green] = jobtty searches list

[yellow]Job Hunting:[/yellow]  
• [green]findjobs[/green] = jobtty search
• [green]savejob[/green] = jobtty save
• [green]myjobs[/green] = jobtty list --saved
• [green]jobstats[/green] = jobtty searches stats

[yellow]Notifications:[/yellow]
• [green]notifications-on[/green] = jobtty daemon start
• [green]notifications-off[/green] = jobtty daemon stop
• [green]check-jobs[/green] = jobtty daemon test

[yellow]Quick Actions:[/yellow]
• [green]apply <job-id>[/green] = jobtty apply
• [green]nope <job-id>[/green] = jobtty dismiss

[yellow]Smart Functions:[/yellow]
• [green]smartjob "flutter" London[/green] = auto-save search
• [green]quickapply <job-id>[/green] = instant apply
        """,
        title="[bold white]⚡ SHELL MAGIC[/bold white]",
        border_style="cyan"
    ))

@shell.command()
def demo():
    """Show terminal integration demo"""
    
    console.print(Panel.fit(
        """
[bold bright_yellow]🎬 JOBTTY TERMINAL INTEGRATION DEMO[/bold bright_yellow]

[cyan]1. Setup aliases:[/cyan]
$ jobtty shell setup

[cyan]2. Quick job search:[/cyan]  
$ jj search "rails developer" -s
$ findjobs "flutter" --location Berlin -s

[cyan]3. Start notifications:[/cyan]
$ notifications-on

[cyan]4. Continue coding...[/cyan]
$ cd my-project && vim app.py
# 💥 BOOM! Job notification appears!

[cyan]5. Quick actions:[/cyan]
$ apply ext_001        # Instant apply!
$ nope ext_002         # Not interested

[cyan]6. Smart workflows:[/cyan]
$ smartjob "python" Remote     # Auto-save with location
$ quickapply ext_003           # No confirmation needed

[bold green]🎯 RESULT: Job hunting integrated seamlessly into development workflow![/bold green]
        """,
        title="[bold white]🚀 TERMINAL MAGIC IN ACTION[/bold white]",
        border_style="bright_yellow"
    ))

# Register with CLI  
if __name__ == "__main__":
    shell()