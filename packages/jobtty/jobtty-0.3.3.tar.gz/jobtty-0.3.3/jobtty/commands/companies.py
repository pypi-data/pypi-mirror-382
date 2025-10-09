"""
Company-specific commands and displays
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from ..core.display import console, create_jobs_table, show_error
from ..core.api_client import JobttyAPI
from ..core.company_logos import display_company_header, get_company_logo

api = JobttyAPI()

@click.command()
@click.argument('company_name')
@click.option('--limit', default=10, help='Number of jobs to show')
def company(company_name, limit):
    """
    🏢 View jobs from specific company with ASCII branding
    
    Examples:
    jobtty company netguru
    jobtty company google --limit 5
    """
    
    try:
        # Search for company jobs using JobTTY API with company filter
        search_params = {
            "company": company_name,
            "limit": limit
        }
        
        console.print(f"[bold cyan]Searching for {company_name} jobs...[/bold cyan]")
        
        # Use only JobTTY API (unified source)
        all_jobs = []
        try:
            jobs = api.search_jobs('jobtty', search_params)
            for job in jobs:
                if company_name.lower() in job.get('company', '').lower():
                    job['source'] = 'jobtty'
                    all_jobs.append(job)
        except Exception as e:
            show_error(f"Failed to search JobTTY API: {str(e)}")
        
        if not all_jobs:
            show_error(f"No jobs found for {company_name}")
            return
        
        # Display company header with ASCII logo
        header = display_company_header(company_name, len(all_jobs))
        
        # Create colored panel for company branding
        logo = get_company_logo(company_name)
        if logo:
            logo_panel = Panel(
                Text(logo, style="bright_green"),
                title=f"[bold bright_yellow]{company_name.upper()}[/bold bright_yellow]",
                border_style="bright_green"
            )
            console.print(logo_panel)
        
        console.print(f"\n[bold bright_green]🎯 Found {len(all_jobs)} {company_name} positions:[/bold bright_green]\n")
        
        # Display jobs table
        jobs_table = create_jobs_table(all_jobs[:limit])
        console.print(jobs_table)
        
        # Company-specific tips
        console.print(f"\n💡 [bold]Pro Tips for {company_name}:[/bold]")
        
        if company_name.lower() == 'netguru':
            console.print("• 🇵🇱 Leading Polish software house")
            console.print("• 💼 Remote-first culture") 
            console.print("• 🚀 Work with international clients")
            console.print("• 📚 Strong learning & development programs")
        elif company_name.lower() == 'google':
            console.print("• 🧠 Prepare for technical interviews")
            console.print("• 📊 System design knowledge essential")
            console.print("• 🌍 Global impact projects")
        elif company_name.lower() == 'spotify':
            console.print("• 🎵 Music + Tech combination")
            console.print("• 📱 Mobile-first development")
            console.print("• 🎨 Strong design culture")
        
        console.print(f"\n💡 Type [bold]jobtty show <job-id>[/bold] for details")
        console.print(f"💡 Type [bold]jobtty save <job-id>[/bold] to bookmark")
        
    except Exception as e:
        show_error(f"Error searching {company_name}: {str(e)}")

@click.command()
@click.option('--limit', default=20, help='Number of companies to show')
@click.option('--query', help='Filter companies by name')
def companies(limit, query):
    """
    🏢 List all companies with available positions
    """
    
    if query:
        console.print(f"[bold bright_cyan]🏢 Companies matching '{query}':[/bold bright_cyan]\n")
    else:
        console.print("[bold bright_cyan]🏢 Companies on Jobtty.io:[/bold bright_cyan]\n")
    
    try:
        # Fetch real companies from JobTTY API
        companies_data = api._make_request('jobtty', 'companies')
        
        if not companies_data or 'companies' not in companies_data:
            show_error("Failed to fetch companies from JobTTY API")
            return
        
        companies_list = companies_data['companies']
        
        # Filter companies by query if provided
        if query:
            companies_list = [
                company for company in companies_list 
                if query.lower() in company['name'].lower()
            ]
            
            if not companies_list:
                console.print(f"[yellow]No companies found matching '{query}'.[/yellow]")
                console.print(f"💡 Try a broader search term or view all companies with: [cyan]jobtty companies[/cyan]")
                return
        
        if not companies_list:
            console.print("[yellow]No companies found with active job postings.[/yellow]")
            return
        
        for company in companies_list[:limit]:
            company_name = company['name']
            job_count = company['job_count']
            description = company.get('description', 'Technology company')
            
            # Get ASCII logo if available
            logo = get_company_logo(company_name)
            if logo:
                # Show mini version of logo
                mini_logo = logo.split('\n')[1] if len(logo.split('\n')) > 1 else "🏢"
                console.print(f"[bright_green]{mini_logo}[/bright_green]")
            else:
                console.print("🏢")
            
            console.print(f"[bold bright_yellow]{company_name}[/bold bright_yellow] - {description[:60]}")
            console.print(f"   📊 [cyan]{job_count} open positions[/cyan]")
            console.print(f"   💡 [dim]jobtty company \"{company_name.lower()}\"[/dim]")
            console.print()
        
        if len(companies_list) > limit:
            console.print(f"[dim]Showing {limit} of {len(companies_list)} companies. Use --limit to see more.[/dim]")
    
    except Exception as e:
        show_error(f"Error fetching companies: {str(e)}")
    
    console.print("[bold]💡 Use [cyan]jobtty company <name>[/cyan] to see company jobs[/bold]")