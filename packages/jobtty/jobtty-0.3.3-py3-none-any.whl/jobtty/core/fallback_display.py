"""
Fallback display functions for systems that don't support Rich properly
"""

import sys
from .display import format_salary

def create_simple_jobs_table(jobs):
    """Create a simple text table without Rich dependencies"""
    
    if not jobs:
        return "No jobs found."
    
    # Simple text table
    lines = []
    lines.append("=" * 80)
    lines.append(f"{'ID':<8} {'Title':<25} {'Company':<18} {'Location':<12} {'Salary':<10}")
    lines.append("-" * 80)
    
    for job in jobs:
        job_id = str(job.get('id', ''))[:7]
        title = str(job.get('title', ''))[:24]
        company = str(job.get('company', ''))[:17]
        location = str(job.get('location', ''))[:11]
        salary = str(format_salary(job))[:9]
        
        lines.append(f"{job_id:<8} {title:<25} {company:<18} {location:<12} {salary:<10}")
    
    lines.append("=" * 80)
    return "\n".join(lines)

def print_jobs_simple(jobs):
    """Print jobs in a simple format without Rich"""
    
    if not jobs:
        print("No jobs found.")
        return
    
    print(f"\nFound {len(jobs)} jobs:")
    print("=" * 80)
    
    # Header
    print(f"{'ID':<8} {'Title':<25} {'Company':<20} {'Location':<15} {'Salary'}")
    print("-" * 80)
    
    for job in jobs:
        job_id = str(job.get('id', ''))[:7]
        title = str(job.get('title', 'Untitled'))[:24]
        company = str(job.get('company', 'Unknown'))[:19]
        location = str(job.get('location', 'N/A'))[:14]
        salary = str(format_salary(job))[:12]
        
        # Add premium indicators in simple format
        if job.get('featured'):
            title = f"* {title[:22]}"  # Use * instead of emoji
        
        print(f"{job_id:<8} {title:<25} {company:<20} {location:<15} {salary}")
        
        # Add remote indicator on separate line if needed
        if job.get('remote'):
            print(f"{'':^8} (Remote work available)")
    
    print("=" * 80)
    print(f"\nType 'jobtty show <job-id>' to view details")

def show_job_details_simple(job):
    """Show job details in simple format"""
    
    print("\n" + "=" * 60)
    print(f"Job ID: {job.get('id')}")
    print(f"Title: {job.get('title', 'Untitled')}")
    print(f"Company: {job.get('company', 'Unknown')}")
    print(f"Location: {job.get('location', 'N/A')}")
    
    salary_display = format_salary(job)
    if salary_display != "Competitive":
        print(f"Salary: {salary_display}")
    
    if job.get('remote'):
        print("Remote: Yes")
    
    if job.get('type'):
        print(f"Type: {job.get('type')}")
    
    print("\nDescription:")
    print("-" * 20)
    description = job.get('description', 'No description available')
    # Wrap text at 70 characters
    words = description.split()
    lines = []
    current_line = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) + 1 > 70:
            if current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
            else:
                lines.append(word)
        else:
            current_line.append(word)
            current_length += len(word) + 1
    
    if current_line:
        lines.append(' '.join(current_line))
    
    for line in lines:
        print(line)
    
    print("=" * 60)

def detect_rich_support():
    """Detect if Rich library can work properly in this environment"""
    
    try:
        from rich.console import Console
        from rich.table import Table
        import sys
        import os
        
        console = Console()
        
        # Check if we have proper terminal support
        if not console.is_terminal:
            return False
        
        # Check encoding (more lenient for compatibility)
        encoding = console.encoding.lower()
        if encoding not in ['utf-8', 'utf8', 'cp1252', 'latin-1', 'ascii']:
            return False
        
        # Check for problematic terminals/environments
        term = os.getenv('TERM', '').lower()
        if term in ['dumb', 'unknown']:
            return False
        
        # Check Python version - older Python might have issues
        if sys.version_info < (3, 6):
            return False
        
        # Try to actually render a simple table to test if it works
        try:
            table = Table(show_header=True)
            table.add_column("Test", width=8)
            table.add_row("660")
            
            # Attempt to render with a string buffer
            from io import StringIO
            string_buffer = StringIO()
            test_console = Console(file=string_buffer, force_terminal=True, width=80)
            test_console.print(table)
            
            # If we got any output, Rich probably works
            output = string_buffer.getvalue()
            if len(output) > 10:  # Should have table content
                return True
            else:
                return False
                
        except Exception:
            return False
        
    except Exception:
        return False

def safe_print_jobs(jobs):
    """Safely print jobs using Rich if available, fallback to simple text"""
    
    if detect_rich_support():
        try:
            from .display import create_jobs_table, console
            table = create_jobs_table(jobs)
            console.print(table)
            return
        except Exception:
            pass
    
    # Fallback to simple display
    print_jobs_simple(jobs)

def safe_show_job_details(job):
    """Safely show job details using Rich if available, fallback to simple text"""
    
    if detect_rich_support():
        try:
            from .display import show_job_details
            show_job_details(job)
            return
        except Exception:
            pass
    
    # Fallback to simple display
    show_job_details_simple(job)

def safe_print_message(message, style="info"):
    """Safely print styled message with fallback"""
    
    if detect_rich_support():
        try:
            from .display import console
            if style == "error":
                console.print(f"❌ {message}", style="red")
            elif style == "success":
                console.print(f"✅ {message}", style="green")
            elif style == "warning":
                console.print(f"⚠️ {message}", style="yellow")
            else:
                console.print(f"ℹ️ {message}")
            return
        except Exception:
            pass
    
    # Fallback to simple print
    if style == "error":
        print(f"ERROR: {message}")
    elif style == "success":
        print(f"SUCCESS: {message}")
    elif style == "warning":
        print(f"WARNING: {message}")
    else:
        print(f"INFO: {message}")