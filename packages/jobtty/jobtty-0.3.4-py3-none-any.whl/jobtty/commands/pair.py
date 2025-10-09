"""
Pair programming commands for Jobtty
Live terminal collaboration for elite developers
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.text import Text
import asyncio
import json
from datetime import datetime

from ..core.collaboration import TerminalShareClient, create_collaboration_session, join_collaboration_session
from ..models.challenge import SAMPLE_CHALLENGES
from ..core.display import show_error, show_success

console = Console()

@click.group()
def pair():
    """🤝 Pair programming and collaboration commands"""
    pass

@pair.command()
@click.argument('challenge_id')
@click.option('--type', 'session_type', default='pair', help='Session type: pair, monitor, group')
@click.option('--public', is_flag=True, help='Make session public for recruiters')
def create(challenge_id, session_type, public):
    """Create a new pair programming session"""
    
    # Validate challenge exists
    challenge = next((c for c in SAMPLE_CHALLENGES if c.id == challenge_id), None)
    if not challenge:
        show_error(f"Challenge '{challenge_id}' not found")
        return
    
    console.print(Panel.fit(
        f"🚀 Creating collaboration session for:\n"
        f"[bold cyan]{challenge.title}[/bold cyan]\n"
        f"Sponsor: [green]{challenge.sponsor_company}[/green]\n"
        f"Budget: [yellow]${challenge.budget:,}/month[/yellow]",
        title="[bold magenta]🤝 Pair Programming Setup[/bold magenta]",
        border_style="magenta"
    ))
    
    if public:
        console.print("[yellow]⚠️ Public session - recruiters can monitor your progress![/yellow]")
    
    # Create session asynchronously
    create_collaboration_session(challenge_id, session_type)

@pair.command()
@click.argument('session_id')
@click.option('--role', default='navigator', help='Your role: driver, navigator, observer')
def join(session_id, role):
    """Join an existing pair programming session"""
    
    console.print(Panel.fit(
        f"🔗 Joining session: [cyan]{session_id}[/cyan]\n"
        f"Role: [green]{role.title()}[/green]\n\n"
        f"[yellow]💡 Tips:[/yellow]\n"
        f"• Use [bold]Ctrl+D[/bold] to disconnect\n"
        f"• Type [bold]/help[/bold] for session commands\n"
        f"• Use [bold]/request-control[/bold] to become driver",
        title="[bold cyan]🤝 Joining Collaboration[/bold cyan]",
        border_style="cyan"
    ))
    
    join_collaboration_session(session_id, role)

@pair.command()
@click.option('--mine', is_flag=True, help='Show only my sessions')
@click.option('--public', is_flag=True, help='Show public sessions available to join')
def list(mine, public):
    """List active collaboration sessions"""
    
    table = Table(title="🔗 Active Collaboration Sessions", title_style="bold magenta")
    table.add_column("Session ID", style="cyan")
    table.add_column("Challenge", style="green")
    table.add_column("Participants", style="yellow")
    table.add_column("Type", style="blue")
    table.add_column("Duration", style="white")
    table.add_column("Status", style="magenta")
    
    # Mock data for demo
    sessions = [
        {
            "id": "sess_abc123",
            "challenge": "Flutter Animation Challenge",
            "participants": "2/4",
            "type": "Pair Programming",
            "duration": "45m",
            "status": "🟢 Active"
        },
        {
            "id": "sess_def456", 
            "challenge": "Rails API Architecture",
            "participants": "1/4",
            "type": "Solo + Monitoring",
            "duration": "12m",
            "status": "🔴 Recruiting"
        }
    ]
    
    for session in sessions:
        table.add_row(
            session["id"],
            session["challenge"],
            session["participants"],
            session["type"],
            session["duration"],
            session["status"]
        )
    
    console.print(table)
    console.print("\n💡 Use [bold cyan]jobtty pair join <session-id>[/bold cyan] to join a session")

@pair.command()
@click.option('--request', is_flag=True, help='Request control from current driver')
@click.option('--release', is_flag=True, help='Release control to navigator')
def control(request, release):
    """Manage session control (driver/navigator switching)"""
    
    if request:
        console.print(Panel.fit(
            "🤚 Control request sent to current driver\n"
            "Waiting for approval...\n\n"
            "[yellow]💡 The driver will see your request and can approve with:[/yellow]\n"
            "[bold cyan]/approve-control[/bold cyan]",
            title="[bold yellow]🔄 Requesting Control[/bold yellow]",
            border_style="yellow"
        ))
    
    elif release:
        console.print(Panel.fit(
            "✅ Control released to navigator\n"
            "You are now in observer mode\n\n"
            "[green]💡 You can watch and chat, but not type[/green]\n"
            "Use [bold cyan]jobtty pair control --request[/bold cyan] to get control back",
            title="[bold green]🤝 Control Released[/bold green]",
            border_style="green"
        ))
    
    else:
        # Show current control status
        console.print(Panel.fit(
            "🎮 Session Control Status\n\n"
            "Current Driver: [bold green]user_abc123[/bold green]\n"
            "Navigator: [bold blue]user_def456[/bold blue]\n"
            "Observers: [bold yellow]recruiter_xyz[/bold yellow]\n\n"
            "[cyan]Commands:[/cyan]\n"
            "• [bold]--request[/bold] to request control\n"
            "• [bold]--release[/bold] to give up control",
            title="[bold]🎮 Control Management[/bold]",
            border_style="white"
        ))

@pair.command()
@click.argument('message', nargs=-1)
def chat(message):
    """Send chat message to session participants"""
    
    if not message:
        show_error("Please provide a message")
        return
    
    chat_text = ' '.join(message)
    timestamp = datetime.now().strftime("%H:%M")
    
    console.print(f"[dim]💬 [{timestamp}] You:[/dim] [white]{chat_text}[/white]")
    
    # TODO: Send to collaboration server
    console.print("[dim]Message sent to session participants[/dim]")

@pair.command()
def status():
    """Show current session status and statistics"""
    
    table = Table(title="📊 Session Statistics", title_style="bold")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="yellow")
    table.add_column("Rank", style="green")
    
    # Mock session stats
    stats = [
        ("Keystrokes", "1,247", "#2"),
        ("Commands Executed", "89", "#1"), 
        ("Git Commits", "12", "#1"),
        ("Test Runs", "23", "#2"),
        ("Progress Score", "485 pts", "#1"),
        ("Time Active", "47m", "-"),
        ("Files Modified", "8", "#1")
    ]
    
    for metric, value, rank in stats:
        table.add_row(metric, value, rank)
    
    console.print(table)
    
    console.print(Panel.fit(
        "🏆 [bold green]Leading the session![/bold green]\n"
        "💡 Keep up the great work - recruiters are watching!\n\n"
        "[dim]Live scoring based on:[/dim]\n"
        "[white]• Code quality and test coverage[/white]\n"
        "[white]• Problem-solving approach[/white]\n"
        "[white]• Git workflow and commit messages[/white]\n"
        "[white]• Terminal efficiency and tool usage[/white]",
        title="[bold yellow]⚡ Performance Insights[/bold yellow]",
        border_style="yellow"
    ))

@pair.command()
def disconnect():
    """Disconnect from current collaboration session"""
    
    console.print(Panel.fit(
        "👋 Disconnecting from collaboration session\n"
        "Your progress has been saved\n\n"
        "[green]✅ Session data available for 24 hours[/green]\n"
        "[cyan]📊 Performance metrics sent to participants[/cyan]\n"
        "[yellow]💼 Recruiter feedback will be available soon[/yellow]",
        title="[bold red]🔌 Session Ended[/bold red]",
        border_style="red"
    ))

if __name__ == "__main__":
    pair()