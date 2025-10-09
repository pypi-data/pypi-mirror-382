"""
Terminal display utilities and ASCII art for Jobtty.io
"""

from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich.align import Align
import random

console = Console()

def format_salary(job):
    """Format salary for display"""
    min_sal = job.get("salary_min")
    max_sal = job.get("salary_max")
    
    if min_sal and max_sal:
        return f"${min_sal:,} - ${max_sal:,}"
    elif min_sal:
        return f"${min_sal:,}+"
    elif max_sal:
        return f"Up to ${max_sal:,}"
    else:
        # Fallback to raw salary field if min/max not available
        raw_salary = job.get('salary')
        if raw_salary and raw_salary != 'N/A':
            # Fix backend bug where salary shows as ',000 - ,000'
            if raw_salary == ',000 - ,000':
                return "Competitive"
            return raw_salary
        return "Competitive"

def get_ascii_logo():
    """Get the beautiful JobTTY ASCII logo with green gradient"""
    logo = """
     ██╗ ██████╗ ██████╗ ████████╗████████╗██╗   ██║
     ██║██╔═══██╗██╔══██╗╚══██╔══╝╚══██╔══╝╚██╗ ██╔╝
     ██║██║   ██║██████╔╝   ██║      ██║    ╚████╔╝ 
██   ██║██║   ██║██╔══██╗   ██║      ██║     ╚██╔╝  
╚█████╔╝╚██████╔╝██████╔╝   ██║      ██║      ██║   
 ╚════╝  ╚═════╝ ╚═════╝    ╚═╝      ╚═╝      ╚═╝   
"""
    
    # Create beautiful green gradient logo
    logo_text = Text()
    lines = logo.strip().split('\n')
    
    # Professional green gradient colors
    green_colors = [
        'bright_green',
        'green',
        'bright_green', 
        'green',
        'bright_green',
        'green'
    ]
    
    for i, line in enumerate(lines):
        color = green_colors[i % len(green_colors)]
        logo_text.append(line + '\n', style=f"{color} bold")
    
    return logo_text

def get_tagline():
    """Get the tagline with beautiful green styling"""
    tagline = Text()
    tagline.append("🚀 ", style="bright_green")
    tagline.append("Terminal Job Board", style="bold bright_green")
    tagline.append(" • ", style="green")
    tagline.append("Find your next role", style="bright_green")
    return tagline

def show_startup_banner():
    """Display the full startup banner"""
    console.clear()
    
    # Main logo
    logo = get_ascii_logo()
    tagline = get_tagline()
    
    # Combine logo and tagline
    full_banner = Text()
    full_banner.append_text(logo)
    full_banner.append("\n")
    full_banner.append_text(tagline)
    
    # Create panel with green border
    panel = Panel(
        Align.center(full_banner),
        border_style="bright_green",
        padding=(1, 2)
    )
    
    console.print(panel)
    console.print()

def show_matrix_effect():
    """Show a quick matrix effect on startup - optimized for speed"""
    import time
    
    # Reduced to single line for 10x faster startup
    matrix_chars = "01"
    line = ''.join(random.choice(matrix_chars) for _ in range(80))
    console.print(line, style="bright_green", end="")
    time.sleep(0.02)  # Reduced from 0.3s to 0.02s
    console.clear()

def create_jobs_table(jobs):
    """Create a beautiful table for job listings with premium styling"""
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim", width=8)
    table.add_column("Title", style="bright_cyan", width=25)
    table.add_column("Company", style="bright_yellow", width=20)
    table.add_column("Location", style="green", width=15)
    table.add_column("Salary", style="bright_green", width=12)
    table.add_column("Type", style="blue", width=8)
    
    for job in jobs:
        # Check if job is premium/featured
        is_premium = job.get('premium', False)
        is_featured = job.get('featured', False)
        company_logo = job.get('company_logo_ascii', '')
        
        # Style based on premium status
        if is_premium or is_featured:
            # Premium jobs get gold styling and logo
            id_style = "bold yellow"
            title_style = "bold bright_yellow"
            company_name = f"{company_logo} {job.get('company', '')[:15]}" if company_logo else job.get('company', '')[:19]
            company_style = "bold gold1"
        else:
            # Regular jobs keep normal styling
            id_style = "dim"
            title_style = "bright_cyan"
            company_name = (job.get('company') or '')[:19]
            company_style = "bright_yellow"
        
        # Add premium indicator to title if featured
        title = job.get('title') or ''
        if is_featured:
            title = f"⭐ {title[:22]}"
        else:
            title = title[:24]
        
        # Create styled text for each cell
        from rich.text import Text
        
        id_text = Text(str(job.get('id', '')), style=id_style)
        title_text = Text(title, style=title_style)
        company_text = Text(company_name, style=company_style)
        location_text = Text((job.get('location') or '')[:14])
        salary_text = Text(format_salary(job))
        type_text = Text(job.get('type') or '')
        
        table.add_row(
            id_text,
            title_text,
            company_text,
            location_text,
            salary_text,
            type_text
        )
    
    return table

def show_job_details(job):
    """Display detailed job information with premium styling"""
    # Check premium status
    is_premium = job.get('premium', False)
    is_featured = job.get('featured', False)
    company_logo = job.get('company_logo_ascii', '')
    
    # Title panel with premium styling
    title_text = job.get('title', 'Unknown Job')
    if is_featured:
        title_text = f"⭐ {title_text}"
    
    title_style = "bold gold1" if (is_premium or is_featured) else "bold bright_cyan"
    border_style = "gold1" if (is_premium or is_featured) else "bright_cyan"
    panel_title = "✨ Premium Job Details" if (is_premium or is_featured) else "Job Details"
    
    title_panel = Panel(
        Text(title_text, style=title_style),
        title=panel_title,
        border_style=border_style
    )
    console.print(title_panel)
    
    # Details table
    details_table = Table(show_header=False, box=None)
    details_table.add_column("Field", style="bold bright_yellow", width=15)
    details_table.add_column("Value", style="bright_white")
    
    # Company row with logo if premium
    company_display = job.get('company', 'N/A')
    if company_logo and (is_premium or is_featured):
        company_display = f"{company_logo} {company_display}"
    
    details_table.add_row("Company:", company_display)
    details_table.add_row("Location:", job.get('location', 'N/A'))
    details_table.add_row("Salary:", format_salary(job))
    details_table.add_row("Type:", job.get('type', 'N/A'))
    details_table.add_row("Remote:", "✅ Yes" if job.get('remote') else "❌ No")
    details_table.add_row("Posted:", job.get('posted_date', 'N/A'))
    
    # Add premium badge if applicable
    if is_premium or is_featured:
        details_table.add_row("Status:", "🏆 PREMIUM" if is_premium else "⭐ FEATURED")
    
    console.print(details_table)
    console.print()
    
    # Description
    description = job.get('description')
    if description:
        # Ensure description is a string
        if isinstance(description, dict):
            description = str(description)
        elif not isinstance(description, str):
            description = str(description)
            
        desc_panel = Panel(
            description,
            title="Description",
            border_style="green"
        )
        console.print(desc_panel)

def show_error(message):
    """Display error message in terminal style"""
    error_text = Text()
    error_text.append("❌ ERROR: ", style="bold red")
    error_text.append(message, style="red")
    console.print(error_text)

def show_success(message):
    """Display success message in terminal style"""
    success_text = Text()
    success_text.append("✅ SUCCESS: ", style="bold green")
    success_text.append(message, style="green")
    console.print(success_text)

def show_info(message):
    """Display info message in terminal style"""
    info_text = Text()
    info_text.append("ℹ️  INFO: ", style="bold blue")
    info_text.append(message, style="blue")
    console.print(info_text)

def show_loading(message="Loading..."):
    """Show loading indicator"""
    from rich.progress import Progress, SpinnerColumn, TextColumn
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(description=message, total=None)
        return progress, task