"""
Saved Search Management Commands
Revolutionary terminal job notifications
"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

from ..core.display import console, show_error, show_success
from ..core.saved_searches import SavedSearchManager, get_all_saved_searches, execute_saved_search
from ..models.saved_search import NotificationFrequency

@click.group()
def searches():
    """💾 Manage saved job searches and notifications"""
    pass

@searches.command()
@click.option('--active', is_flag=True, help='Show only searches with notifications enabled')
def list(active):
    """List all saved searches"""
    
    saved_searches = get_all_saved_searches()
    
    if not saved_searches:
        console.print("📝 No saved searches yet")
        console.print("💡 Use [bold]jobtty search <query> --save[/bold] to create your first saved search")
        return
    
    if active:
        saved_searches = [s for s in saved_searches if s.notifications_enabled]
        console.print(f"[bold bright_cyan]🔔 Active Notification Searches ({len(saved_searches)}):[/bold bright_cyan]\n")
    else:
        console.print(f"[bold bright_cyan]💾 All Saved Searches ({len(saved_searches)}):[/bold bright_cyan]\n")
    
    # Create table
    searches_table = Table(show_header=True, header_style="bold magenta")
    searches_table.add_column("ID", style="cyan", width=12)
    searches_table.add_column("Name", style="bright_white", width=30)
    searches_table.add_column("Query", style="green", width=20)
    searches_table.add_column("Location", style="yellow", width=15)
    searches_table.add_column("Salary", style="blue", width=12)
    searches_table.add_column("Frequency", style="magenta", width=10)
    searches_table.add_column("Matches", style="bright_green", width=8)
    
    for search in saved_searches:
        salary_display = ""
        if search.min_salary:
            salary_display = f"£{search.min_salary//1000}k+"
        
        frequency_icon = {
            "instant": "⚡",
            "hourly": "🕐", 
            "daily": "📅",
            "weekly": "📆"
        }.get(search.notification_frequency.value, "🔔")
        
        searches_table.add_row(
            search.id[:10] + "...",
            search.name[:28] + ("..." if len(search.name) > 28 else ""),
            search.query[:18] + ("..." if len(search.query) > 18 else ""),
            search.location or "Remote",
            salary_display,
            f"{frequency_icon} {search.notification_frequency.value}",
            str(search.total_matches)
        )
    
    console.print(searches_table)
    console.print(f"\n💡 Use [bold]jobtty searches run <search-id>[/bold] to execute a search")
    console.print(f"💡 Use [bold]jobtty searches delete <search-id>[/bold] to remove a search (add --interactive for confirmation)")

@searches.command()
@click.argument('search_id')
def run(search_id):
    """Execute a saved search"""
    
    console.print(f"🔍 Running saved search: [cyan]{search_id}[/cyan]")
    
    # Find and execute the search
    matching_jobs = execute_saved_search(search_id)
    
    if not matching_jobs:
        show_error("No jobs found for this saved search")
        return
    
    console.print(f"\n[bold bright_green]Found {len(matching_jobs)} matching jobs:[/bold bright_green]\n")
    
    # Create jobs table (reuse from search.py)
    from ..core.display import create_jobs_table
    jobs_table = create_jobs_table(matching_jobs)
    console.print(jobs_table)

@searches.command()
@click.argument('search_id')
@click.option('--interactive/--no-interactive', default=False, help='Ask for confirmation before deleting')
def delete(search_id, interactive):
    """Delete a saved search"""
    
    if interactive:
        if not Confirm.ask(f"Delete saved search [cyan]{search_id}[/cyan]?"):
            console.print("❌ Cancelled")
            return
    
    manager = SavedSearchManager()
    success = manager.delete_search(search_id)
    
    if success:
        show_success(f"🗑️ Saved search {search_id} deleted")
    else:
        show_error(f"Search {search_id} not found")

@searches.command()
@click.argument('search_id')
@click.option('--name', help='Update search name')
@click.option('--frequency', type=click.Choice(['instant', 'hourly', 'daily', 'weekly']), help='Update notification frequency')
@click.option('--notifications/--no-notifications', help='Enable/disable notifications')
def update(search_id, name, frequency, notifications):
    """Update saved search settings"""
    
    updates = {}
    
    if name:
        updates['name'] = name
    if frequency:
        updates['notification_frequency'] = NotificationFrequency(frequency)
    if notifications is not None:
        updates['notifications_enabled'] = notifications
    
    if not updates:
        show_error("No updates specified")
        return
    
    manager = SavedSearchManager()
    success = manager.update_search(search_id, updates)
    
    if success:
        show_success(f"✅ Search {search_id} updated")
    else:
        show_error(f"Search {search_id} not found")

@searches.command()
def stats():
    """Show saved search statistics"""
    
    manager = SavedSearchManager()
    stats = manager.get_search_statistics()
    
    if stats.get("total_searches", 0) == 0:
        console.print("📊 No saved searches yet")
        console.print("💡 Use [bold]jobtty search <query> --save[/bold] to get started")
        return
    
    console.print(Panel.fit(
        f"""
[bold cyan]📊 SAVED SEARCH ANALYTICS[/bold cyan]

[white]Overview:[/white]
• Total searches: [green]{stats['total_searches']}[/green]
• Active (notifications on): [yellow]{stats['active_searches']}[/yellow]
• Total job matches: [blue]{stats['total_matches']}[/blue]
• New matches today: [bright_green]{stats['matches_today']}[/bright_green]
• Average matches per search: [magenta]{stats['avg_matches_per_search']}[/magenta]

[white]Notification Settings:[/white]
• Instant: [red]{stats['notification_frequency_breakdown'].get('instant', 0)}[/red] searches
• Hourly: [yellow]{stats['notification_frequency_breakdown'].get('hourly', 0)}[/yellow] searches  
• Daily: [blue]{stats['notification_frequency_breakdown'].get('daily', 0)}[/blue] searches
• Weekly: [green]{stats['notification_frequency_breakdown'].get('weekly', 0)}[/green] searches
        """,
        title="[bold white]📈 SEARCH PERFORMANCE[/bold white]",
        border_style="cyan"
    ))

@searches.command()
@click.option('--days', default=30, help='Number of days of matches to keep')
def cleanup(days):
    """Clean up old job matches"""
    
    if not Confirm.ask(f"Clean up job matches older than {days} days?"):
        console.print("❌ Cancelled")
        return
    
    manager = SavedSearchManager()
    manager.cleanup_old_matches(days)
    
    show_success(f"🧹 Cleanup complete - kept matches from last {days} days")

# Register with CLI in cli.py
if __name__ == "__main__":
    searches()
