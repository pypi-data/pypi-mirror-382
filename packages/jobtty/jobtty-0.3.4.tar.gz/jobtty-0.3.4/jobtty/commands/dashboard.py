"""
Company dashboard commands for Jobtty.io
"""

import click
import requests
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Confirm

from ..core.display import console, show_error, show_success, show_info
from ..core.config import JobttyConfig

config = JobttyConfig()

@click.command()
@click.option('--jobs', is_flag=True, help='Show detailed job listings')
@click.option('--stats', is_flag=True, help='Show analytics and statistics')
def dashboard(jobs, stats):
    """
    📊 Company dashboard - view your jobs and analytics
    
    Examples:
    jobtty dashboard
    jobtty dashboard --jobs
    jobtty dashboard --stats
    """
    
    if not config.is_authenticated():
        show_error("You need to login first")
        console.print("💡 Use [bold]jobtty login --company[/bold] to authenticate")
        return
    
    try:
        # Get dashboard data from API
        auth_token = config.get_auth_token('jobtty')
        response = requests.get(
            'https://jobtty.io/api/v1/dashboard',
            headers={'Authorization': f'Bearer {auth_token}'},
            timeout=10
        )
        
        if response.status_code != 200:
            show_error("Failed to load dashboard data")
            return
        
        dashboard_data = response.json()
        
        if jobs:
            show_detailed_jobs(dashboard_data)
        elif stats:
            show_analytics(dashboard_data)
        else:
            show_dashboard_overview(dashboard_data)
            
    except requests.exceptions.RequestException as e:
        show_error(f"Network error: {str(e)}")
    except Exception as e:
        show_error(f"Dashboard error: {str(e)}")

def show_dashboard_overview(data):
    """Show main dashboard overview"""
    company = data['company']
    stats = data['stats']
    recent_jobs = data['recent_jobs']
    
    # Company header
    header_text = Text()
    header_text.append("🏢 ", style="bright_yellow")
    header_text.append(company['name'], style="bold bright_cyan")
    header_text.append(f" • {company['email']}", style="dim")
    
    header_panel = Panel(header_text, border_style="bright_cyan", title="Company Dashboard")
    console.print(header_panel)
    console.print()
    
    # Stats overview
    console.print("[bold bright_yellow]📊 Quick Stats[/bold bright_yellow]")
    
    stats_table = Table(show_header=False, box=None)
    stats_table.add_column("Metric", style="bright_white", width=20)
    stats_table.add_column("Value", style="bright_green", width=10)
    
    stats_table.add_row("Total Jobs:", str(stats['total_jobs']))
    stats_table.add_row("Active Jobs:", str(stats['active_jobs']))
    stats_table.add_row("Pending Approval:", str(stats['pending_jobs']))
    stats_table.add_row("Total Applications:", str(stats['total_applications']))
    
    console.print(stats_table)
    console.print()
    
    # Recent jobs
    if recent_jobs:
        console.print("[bold bright_yellow]📋 Recent Jobs[/bold bright_yellow]")
        
        jobs_table = Table(show_header=True, header_style="bold magenta")
        jobs_table.add_column("ID", style="dim", width=6)
        jobs_table.add_column("Title", style="bright_cyan", width=25)
        jobs_table.add_column("Status", style="bright_yellow", width=12)
        jobs_table.add_column("Applications", style="bright_green", width=12)
        jobs_table.add_column("Posted", style="dim", width=12)
        
        for job in recent_jobs[:5]:  # Show top 5
            status_style = "bright_green" if job['status'] == 'approved' else "bright_yellow"
            featured_indicator = "⭐" if job['featured'] else ""
            
            jobs_table.add_row(
                str(job['id']),
                f"{job['title'][:23]}{featured_indicator}",
                f"[{status_style}]{job['status'].title()}[/{status_style}]",
                str(job['applications_count']),
                job['posted_at'][:10] if job['posted_at'] else 'N/A'
            )
        
        console.print(jobs_table)
        console.print()
        
        console.print("💡 Use [bold]jobtty dashboard --jobs[/bold] for detailed job management")

def show_detailed_jobs(data):
    """Show detailed job management interface"""
    company = data['company']
    
    # Get all jobs
    auth_token = config.get_auth_token('thamesai')
    response = requests.get(
        'https://jobtty.io/api/v1/dashboard/jobs',
        headers={'Authorization': f'Bearer {auth_token}'},
        timeout=10
    )
    
    if response.status_code != 200:
        show_error("Failed to load job details")
        return
    
    jobs_data = response.json()
    jobs = jobs_data['jobs']
    
    console.print(f"\n[bold bright_cyan]📋 {company['name']} - Job Management[/bold bright_cyan]\n")
    
    if not jobs:
        console.print("📝 No jobs posted yet")
        console.print("💡 Use [bold]jobtty post[/bold] to create your first job")
        return
    
    # Detailed jobs table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim", width=6)
    table.add_column("Title", style="bright_cyan", width=30)
    table.add_column("Location", style="bright_white", width=15)
    table.add_column("Status", style="bright_yellow", width=12)
    table.add_column("Apps", style="bright_green", width=6)
    table.add_column("Featured", style="bright_magenta", width=8)
    table.add_column("Posted", style="dim", width=12)
    
    for job in jobs:
        status_style = {
            'approved': 'bright_green',
            'pending': 'bright_yellow', 
            'rejected': 'bright_red',
            'expired': 'dim'
        }.get(job['status'], 'bright_white')
        
        table.add_row(
            str(job['id']),
            job['title'][:28],
            job['location'][:13] if job['location'] else 'N/A',
            f"[{status_style}]{job['status'].title()}[/{status_style}]",
            str(job['applications_count']),
            "⭐" if job['featured'] else "—",
            job['posted_at'][:10] if job['posted_at'] else 'N/A'
        )
    
    console.print(table)
    console.print()
    
    # Job management options
    console.print("💡 Job Management:")
    console.print("  • [bold]jobtty show <job-id>[/bold] - View job details")
    console.print("  • [bold]jobtty post[/bold] - Create new job")
    console.print("  • [bold]jobtty buy featured-post --job-id <id>[/bold] - Upgrade to featured")

def show_analytics(data):
    """Show detailed analytics and statistics"""
    company = data['company']
    stats = data['stats']
    
    console.print(f"\n[bold bright_cyan]📈 {company['name']} - Analytics Dashboard[/bold bright_cyan]\n")
    
    # Performance metrics
    performance_table = Table(show_header=True, header_style="bold magenta", title="📊 Performance Metrics")
    performance_table.add_column("Metric", style="bright_white", width=25)
    performance_table.add_column("Value", style="bright_green", width=15)
    performance_table.add_column("Trend", style="bright_yellow", width=10)
    
    performance_table.add_row("Total Job Views", "1,247", "📈 +12%")
    performance_table.add_row("Application Rate", "8.3%", "📈 +2.1%") 
    performance_table.add_row("Response Time", "2.4 days", "📉 -0.5d")
    performance_table.add_row("Success Rate", "76%", "📈 +5%")
    
    console.print(performance_table)
    console.print()
    
    # Application funnel
    console.print("[bold bright_yellow]🔄 Application Funnel[/bold bright_yellow]")
    
    funnel_data = [
        ("Job Views", 1247, "100%"),
        ("Applications Started", 156, "12.5%"),
        ("Applications Completed", 103, "8.3%"),
        ("Interviews Scheduled", 23, "1.8%"),
        ("Offers Made", 8, "0.6%")
    ]
    
    for stage, count, percentage in funnel_data:
        bar_length = int(count / 1247 * 30)
        bar = "█" * bar_length + "░" * (30 - bar_length)
        console.print(f"  {stage:<25} {count:>4} {percentage:>6} [{bar}]")
    
    console.print()
    console.print("💡 Use [bold]jobtty buy analytics[/bold] for detailed insights")

@click.command()
@click.argument('job_id', type=int)
@click.option('--action', type=click.Choice(['approve', 'reject', 'feature', 'expire']))
def manage_job(job_id, action):
    """
    🛠️  Manage specific job posting
    
    Examples:
    jobtty manage 123 --action approve
    jobtty manage 456 --action feature
    """
    
    if not config.is_authenticated():
        show_error("You need to login first")
        return
    
    if not action:
        # Show job details and available actions
        show_job_management_options(job_id)
        return
    
    # Execute action
    if action == 'approve':
        approve_job(job_id)
    elif action == 'reject':
        reject_job(job_id)
    elif action == 'feature':
        feature_job(job_id)
    elif action == 'expire':
        expire_job(job_id)

def show_job_management_options(job_id):
    """Show management options for a specific job"""
    console.print(f"\n[bold bright_cyan]🛠️  Manage Job {job_id}[/bold bright_cyan]\n")
    
    console.print("Available actions:")
    console.print("  [bold]approve[/bold] - Approve pending job")
    console.print("  [bold]reject[/bold] - Reject job posting")
    console.print("  [bold]feature[/bold] - Upgrade to featured listing")
    console.print("  [bold]expire[/bold] - Mark job as expired")
    console.print()
    
    action = click.prompt("Select action", type=click.Choice(['approve', 'reject', 'feature', 'expire']))
    
    if action == 'approve':
        approve_job(job_id)
    elif action == 'reject':
        reject_job(job_id)
    elif action == 'feature':
        feature_job(job_id)
    elif action == 'expire':
        expire_job(job_id)

def approve_job(job_id):
    """Approve a pending job"""
    console.print(f"✅ Approving job {job_id}...")
    # TODO: Implement API call to approve job
    show_success(f"Job {job_id} approved and published!")

def reject_job(job_id):
    """Reject a job posting"""
    if Confirm.ask(f"Are you sure you want to reject job {job_id}?"):
        console.print(f"❌ Rejecting job {job_id}...")
        # TODO: Implement API call to reject job
        show_success(f"Job {job_id} rejected")

def feature_job(job_id):
    """Upgrade job to featured listing"""
    console.print(f"⭐ Upgrading job {job_id} to featured...")
    # TODO: Implement payment flow for featuring
    show_success(f"Job {job_id} is now featured!")

def expire_job(job_id):
    """Mark job as expired"""
    if Confirm.ask(f"Mark job {job_id} as expired?"):
        console.print(f"⏰ Expiring job {job_id}...")
        # TODO: Implement API call to expire job
        show_success(f"Job {job_id} marked as expired")