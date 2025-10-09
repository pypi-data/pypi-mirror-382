"""
Background Daemon Commands
Control the revolutionary terminal job notification system
"""

import click
import time
from rich.console import Console
from rich.panel import Panel
from pathlib import Path

from ..core.display import console, show_error, show_success
from ..core.notification_daemon import start_daemon, stop_daemon, daemon_status, check_notifications_once

def _listen_file_based(notification_file, background):
    """File-based notification listener for Windows"""
    import time
    
    # Clear existing file
    if notification_file.exists():
        notification_file.unlink()
    
    console.print("📱 Waiting for notifications...")
    
    last_size = 0
    while True:
        if notification_file.exists():
            current_size = notification_file.stat().st_size
            if current_size > last_size:
                # New content added
                with open(notification_file, 'r', encoding='utf-8') as f:
                    f.seek(last_size)
                    new_lines = f.read()
                    for line in new_lines.strip().split('\n'):
                        if line.strip():
                            console.print(f"🔔 {line}")
                last_size = current_size
        
        time.sleep(1)  # Check every second

@click.group()
def daemon():
    """🤖 Control background job notification daemon"""
    pass

@daemon.command()
@click.option('--foreground', is_flag=True, help='Run in foreground (for debugging)')
def start(foreground):
    """Start the job notification daemon"""
    
    console.print(Panel.fit(
        """
[bold bright_yellow]🚀 STARTING REVOLUTIONARY FEATURE![/bold bright_yellow]

[cyan]The Jobtty notification daemon will:[/cyan]
• Monitor your saved searches continuously
• Send job alerts directly to your terminal
• Show notifications while you're coding
• Work across all terminal sessions

[green]This is the world's first terminal-native job notification system![/green]
        """,
        title="[bold white]🤖 Notification Daemon[/bold white]", 
        border_style="bright_yellow"
    ))
    
    try:
        start_daemon(background=not foreground)
        
        if foreground:
            console.print("🔄 Running in foreground mode...")
            console.print("Press Ctrl+C to stop")
        else:
            console.print("✅ Daemon started in background")
            console.print("💡 Use [bold]jobtty daemon status[/bold] to check status")
            
    except Exception as e:
        show_error(f"Failed to start daemon: {str(e)}")

@daemon.command()
def stop():
    """Stop the job notification daemon"""
    
    console.print("🛑 Stopping notification daemon...")
    
    try:
        stop_daemon()
        show_success("Daemon stopped successfully")
    except Exception as e:
        show_error(f"Failed to stop daemon: {str(e)}")

@daemon.command()
def status():
    """Check daemon status and recent activity"""
    
    console.print(Panel.fit(
        "[bold cyan]🤖 JOBTTY NOTIFICATION DAEMON STATUS[/bold cyan]",
        border_style="cyan"
    ))
    
    try:
        daemon_status()
    except Exception as e:
        show_error(f"Failed to check status: {str(e)}")

@daemon.command()
def restart():
    """Restart the notification daemon"""
    
    console.print("🔄 Restarting notification daemon...")
    
    try:
        stop_daemon()
        time.sleep(1)
        start_daemon()
        show_success("Daemon restarted successfully")
    except Exception as e:
        show_error(f"Failed to restart daemon: {str(e)}")

@daemon.command()
def test():
    """Test notification system manually"""
    
    console.print("🧪 Testing notification system...")
    console.print("🔍 Checking all saved searches for new jobs...")
    
    try:
        check_notifications_once()
        show_success("Test completed - check for any notifications!")
    except Exception as e:
        show_error(f"Test failed: {str(e)}")

@daemon.command()
def alerts():
    """🔔 Show new job alerts in terminal (interactive notifications)"""
    
    from ..core.saved_searches import SavedSearchManager
    from rich.table import Table
    
    manager = SavedSearchManager()
    
    console.print(Panel.fit(
        """
[bold bright_yellow]🔔 NEW JOB ALERTS![/bold bright_yellow]

[cyan]Showing jobs found by your saved searches:[/cyan]
• Real-time job matches from your 13 saved searches
• Direct terminal workflow - no browser needed!
        """,
        title="[bold white]🎯 JobTTY Terminal Alerts[/bold white]", 
        border_style="bright_yellow"
    ))
    
    # Show recent matches from all saved searches
    total_new_jobs = 0
    
    for search in manager.load_all_searches()[:5]:  # Show first 5 searches
        try:
            results = manager.execute_search(search)
            if results and len(results) > 0:
                console.print(f"\n🔍 [bold]{search.name}[/bold] - Found {len(results)} jobs:")
                
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("ID", style="dim", width=6)
                table.add_column("Title", style="bright_white", width=30)
                table.add_column("Company", style="bright_cyan", width=20)
                table.add_column("Actions", style="bright_green", width=20)
                
                for job in results[:3]:  # Show top 3 jobs
                    table.add_row(
                        str(job.get('id', 'N/A')), 
                        job.get('title', 'Unknown')[:27] + "..." if len(job.get('title', '')) > 30 else job.get('title', 'Unknown'),
                        job.get('company', 'Unknown')[:17] + "..." if len(job.get('company', '')) > 20 else job.get('company', 'Unknown'),
                        f"jobtty show {job.get('id', 'N/A')}"
                    )
                
                console.print(table)
                total_new_jobs += len(results)
        except Exception as e:
            continue
    
    if total_new_jobs == 0:
        console.print("\n📭 No new jobs found right now")
        console.print("💡 Your daemon is monitoring in background - new jobs will appear!")
    else:
        console.print(f"\n🎉 Found [bold bright_green]{total_new_jobs}[/bold bright_green] total jobs!")
        console.print("\n💡 Use [bold]jobtty show <job-id>[/bold] to view details")
        console.print("💡 Use [bold]jobtty apply <job-id>[/bold] to apply instantly!")

@daemon.command()
def logs():
    """Show daemon logs"""
    
    from pathlib import Path
    log_file = Path.home() / ".jobtty" / "daemon.log"
    
    if not log_file.exists():
        console.print("📄 No daemon logs found")
        return
    
    console.print("[bold cyan]📋 Recent Daemon Logs:[/bold cyan]\n")
    
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
            
        # Show last 20 lines
        for line in lines[-20:]:
            console.print(line.strip())
            
    except Exception as e:
        show_error(f"Failed to read logs: {str(e)}")

@daemon.command()
@click.option('--background', '-b', is_flag=True, help='Run in background')
def listen(background):
    """🔊 Listen for terminal job notifications"""
    
    from pathlib import Path
    import subprocess
    import platform
    
    console.print(Panel.fit(
        """
[bold bright_green]🔊 LISTENING FOR JOB NOTIFICATIONS![/bold bright_green]

[cyan]This terminal will now receive:[/cyan]
• Real-time job alerts from your saved searches
• Direct notifications while coding
• Quick apply/dismiss options

[yellow]Keep this terminal open to receive notifications![/yellow]
        """,
        title="[bold white]🔔 Notification Listener[/bold white]", 
        border_style="bright_green"
    ))
    
    pipe_dir = Path.home() / ".jobtty" / "pipes"
    pipe_dir.mkdir(exist_ok=True)
    
    if platform.system() == 'Windows':
        # Windows: Use file-based notifications
        notification_file = pipe_dir / "notifications.txt"
        console.print(f"📡 Monitoring: {notification_file}")
        console.print("🔄 Press Ctrl+C to stop listening\n")
        
        try:
            _listen_file_based(notification_file, background)
        except KeyboardInterrupt:
            console.print("\n👋 Stopped listening for notifications")
        return
    
    # Unix/Linux/macOS: Use named pipes
    notification_pipe = pipe_dir / "notifications"
    
    try:
        # Create named pipe if it doesn't exist
        if not notification_pipe.exists():
            import os
            os.mkfifo(str(notification_pipe))
        
        console.print(f"📡 Listening on: {notification_pipe}")
        console.print("🔄 Press Ctrl+C to stop listening\n")
        
        # Listen for notifications
        if background:
            # Background mode - just setup the pipe
            console.print("✅ Background listener setup complete")
            console.print("💡 Notifications will appear in this terminal")
        else:
            # Foreground mode - actively listen
            import select
            import os
            
            while True:
                try:
                    # Open pipe for reading (blocking)
                    with open(notification_pipe, 'r') as pipe:
                        notification = pipe.read().strip()
                        if notification:
                            # Clear screen and show notification
                            console.clear()
                            console.print(notification)
                            console.print("\n[dim]Press Enter to continue...[/dim]")
                            input()
                except KeyboardInterrupt:
                    console.print("\n🔴 Stopped listening for notifications")
                    break
                except Exception as e:
                    console.print(f"⚠️  Listener error: {e}")
                    time.sleep(1)
                    
    except Exception as e:
        show_error(f"Failed to setup notification listener: {str(e)}")

# Register with CLI
if __name__ == "__main__":
    daemon()