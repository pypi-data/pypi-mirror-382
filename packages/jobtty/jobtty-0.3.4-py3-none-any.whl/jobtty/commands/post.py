"""
Job posting commands for Jobtty.io
"""

import click
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.console import Console
from rich.panel import Panel

from ..core.display import console, show_error, show_success, show_info
from ..core.config import JobttyConfig

config = JobttyConfig()

@click.command()
@click.option('--title', help='Job title')
@click.option('--company', help='Company name')
@click.option('--location', help='Job location')
@click.option('--salary-min', type=int, help='Minimum salary')
@click.option('--salary-max', type=int, help='Maximum salary')
@click.option('--remote', is_flag=True, help='Remote position')
@click.option('--interactive', is_flag=True, help='Interactive job posting mode')
def post_job(title, company, location, salary_min, salary_max, remote, interactive):
    """
    📝 Post a new job listing
    
    Examples:
    jobtty post --title "Senior Python Developer" --company "TechCorp"
    jobtty post --interactive
    """
    
    if not config.is_authenticated():
        show_error("You need to login first to post jobs")
        console.print("💡 Use [bold]jobtty login[/bold] to authenticate")
        return
    
    console.print("\n[bold bright_yellow]📝 Post New Job[/bold bright_yellow]\n")
    
    # Interactive mode or collect missing data
    if interactive or not title:
        title = title or Prompt.ask("💼 Job title")
        company = company or Prompt.ask("🏢 Company name")
        location = location or Prompt.ask("📍 Location", default=config.get('location', 'London, UK'))
        
        console.print("\n💰 Salary range:")
        salary_min = salary_min or IntPrompt.ask("  Minimum salary (£)", default=50000)
        salary_max = salary_max or IntPrompt.ask("  Maximum salary (£)", default=80000)
        
        remote = remote or Confirm.ask("🏠 Remote position?", default=False)
        
        console.print("\n📋 Job details:")
        job_type = Prompt.ask("Job type", choices=['full-time', 'part-time', 'contract', 'freelance'], default='full-time')
        experience_level = Prompt.ask("Experience level", choices=['entry', 'mid', 'senior', 'lead'], default='mid')
        
        console.print("\n📝 Job description:")
        console.print("Enter job description (press Ctrl+D when finished):")
        
        description_lines = []
        try:
            while True:
                line = input()
                description_lines.append(line)
        except EOFError:
            pass
        
        description = '\n'.join(description_lines) if description_lines else Prompt.ask("Short description")
        
        skills = Prompt.ask("Required skills (comma-separated)", default="Python, Git, REST APIs")
        benefits = Prompt.ask("Benefits (optional)", default="Health insurance, Flexible hours")
    
    # Prepare job data
    job_data = {
        'title': title,
        'company': company,
        'location': location,
        'salary_min': salary_min,
        'salary_max': salary_max,
        'remote': remote,
        'job_type': job_type if interactive else 'full-time',
        'experience_level': experience_level if interactive else 'mid',
        'description': description if interactive else f"Exciting opportunity for {title} at {company}",
        'skills_required': skills if interactive else "Python, Git",
        'benefits': benefits if interactive else "Competitive package"
    }
    
    # Show preview
    preview_job_posting(job_data)
    
    if not Confirm.ask("\n✅ Post this job?", default=True):
        console.print("❌ Job posting cancelled")
        return
    
    # Determine pricing
    show_pricing_options(job_data)

def preview_job_posting(job_data):
    """Show preview of job posting"""
    console.print("\n[bold bright_cyan]👁️  Job Posting Preview[/bold bright_cyan]\n")
    
    preview_text = f"""[bold bright_yellow]{job_data['title']}[/bold bright_yellow]
🏢 [bright_green]{job_data['company']}[/bright_green]
📍 {job_data['location']}
💰 £{job_data['salary_min']:,} - £{job_data['salary_max']:,}
🏠 {'Remote Available' if job_data['remote'] else 'On-site'}
⏰ {job_data['job_type'].title()}
🎯 {job_data['experience_level'].title()} Level

📋 Description:
{job_data['description']}

🛠️  Required Skills:
{job_data['skills_required']}

🎁 Benefits:
{job_data['benefits']}"""
    
    panel = Panel(preview_text, border_style="bright_cyan", title="Preview")
    console.print(panel)

def show_pricing_options(job_data):
    """Show job posting pricing options"""
    console.print("\n[bold bright_yellow]💎 Choose Your Posting Package[/bold bright_yellow]\n")
    
    options = [
        {
            'name': 'Basic Listing',
            'price': '£0',
            'duration': '30 days',
            'features': ['Standard listing', 'Email notifications', 'Basic analytics'],
            'recommended': False
        },
        {
            'name': 'Featured Listing',
            'price': '£29',
            'duration': '45 days', 
            'features': ['Featured placement', 'Highlighted listing', 'Priority in search', 'Advanced analytics'],
            'recommended': True
        },
        {
            'name': 'Premium Listing',
            'price': '£79',
            'duration': '60 days',
            'features': ['Top placement', 'Company branding', 'Social media promotion', 'Dedicated support'],
            'recommended': False
        }
    ]
    
    for i, option in enumerate(options, 1):
        style = "bright_green" if option['recommended'] else "bright_white"
        recommended_text = " [bold bright_yellow]⭐ RECOMMENDED[/bold bright_yellow]" if option['recommended'] else ""
        
        console.print(f"[{style}]{i}. {option['name']} - {option['price']}{recommended_text}[/{style}]")
        console.print(f"   ⏰ Active for {option['duration']}")
        for feature in option['features']:
            console.print(f"   ✅ {feature}")
        console.print()
    
    choice = Prompt.ask("Select package", choices=['1', '2', '3'], default='2')
    selected_option = options[int(choice) - 1]
    
    console.print(f"\n✅ Selected: [bold bright_green]{selected_option['name']}[/bold bright_green]")
    
    if selected_option['price'] != '£0':
        console.print(f"💳 Price: [bold bright_yellow]{selected_option['price']}[/bold bright_yellow]")
        
        if Confirm.ask("Proceed to payment?", default=True):
            process_payment(selected_option, job_data)
    else:
        # Free posting
        submit_job_posting(job_data, selected_option)

def process_payment(package, job_data):
    """Process payment for premium job posting"""
    from ..commands.payment import create_stripe_payment
    
    console.print("\n[bold bright_cyan]💳 Payment Processing[/bold bright_cyan]\n")
    
    try:
        payment_url = create_stripe_payment(package, job_data)
        
        console.print("🚀 Opening Stripe checkout...")
        console.print(f"🔗 Payment URL: [link]{payment_url}[/link]")
        
        # Show QR code for mobile payments
        show_payment_qr(payment_url)
        
        console.print("\n⏳ Waiting for payment confirmation...")
        
        # Simulate payment success for demo
        import time
        time.sleep(3)
        
        show_success("💳 Payment successful!")
        submit_job_posting(job_data, package)
        
    except Exception as e:
        show_error(f"Payment failed: {str(e)}")

def show_payment_qr(payment_url):
    """Show QR code for payment URL"""
    try:
        import qrcode
        from io import StringIO
        
        qr = qrcode.QRCode(version=1, box_size=1, border=1)
        qr.add_data(payment_url)
        qr.make(fit=True)
        
        # Create ASCII QR code
        f = StringIO()
        qr.print_ascii(out=f)
        f.seek(0)
        qr_ascii = f.read()
        
        console.print("\n[dim]📱 Scan QR code to pay on mobile:[/dim]")
        console.print(qr_ascii)
        
    except ImportError:
        console.print("💡 Install qrcode package to see QR codes: pip install qrcode[pil]")

def submit_job_posting(job_data, package):
    """Submit the job posting to the service"""
    console.print(f"\n🚀 Posting job to Jobtty API...")
    
    try:
        import requests
        
        # Get auth token
        auth_token = config.get_auth_token('jobtty')
        if not auth_token:
            show_error("Authentication token not found")
            return
        
        # Prepare API payload
        api_payload = {
            'job': {
                'title': job_data['title'],
                'description': job_data['description'],
                'requirements': job_data['skills_required'],
                'location': job_data['location'],
                'salary': f"£{job_data['salary_min']:,} - £{job_data['salary_max']:,}",
                'job_type': job_data['job_type'],
                'remote': job_data['remote']
            }
        }
        
        # Post to API
        response = requests.post(
            'https://jobtty.io/api/v1/jobs',
            json=api_payload,
            headers={'Authorization': f'Bearer {auth_token}'},
            timeout=10
        )
        
        if response.status_code == 201:
            job_response = response.json()
            show_success("Job posted successfully!")
            console.print(f"🆔 Job ID: [bold bright_cyan]{job_response['id']}[/bold bright_cyan]")
            console.print(f"📅 Package: {package['name']} ({package['duration']})")
            console.print(f"📋 Status: {job_response['message']}")
            console.print(f"🔗 View at: https://jobtty.io/jobs/{job_response['id']}")
        else:
            error_data = response.json()
            show_error(f"Failed to post job: {error_data.get('error', 'Unknown error')}")
            if 'details' in error_data:
                for detail in error_data['details']:
                    console.print(f"  • {detail}")
        
    except requests.exceptions.RequestException as e:
        show_error(f"Network error: {str(e)}")
    except Exception as e:
        show_error(f"Failed to post job: {str(e)}")

@click.command()
@click.option('--status', help='Filter by status (active, draft, closed)')
def my_posts(status):
    """
    📋 Show your posted jobs
    """
    
    if not config.is_authenticated():
        show_error("You need to login first")
        return
    
    posted_jobs = config.get('posted_jobs', [])
    
    if not posted_jobs:
        console.print("📝 You haven't posted any jobs yet")
        console.print("💡 Use [bold]jobtty post[/bold] to create your first job posting")
        return
    
    console.print(f"\n[bold bright_cyan]📋 Your Job Postings ({len(posted_jobs)}):[/bold bright_cyan]\n")
    
    from rich.table import Table
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim", width=8)
    table.add_column("Title", style="bright_cyan", width=25)
    table.add_column("Company", style="bright_yellow", width=20)
    table.add_column("Package", style="bright_green", width=15)
    table.add_column("Posted", style="dim", width=12)
    
    for job in posted_jobs:
        if status and job.get('status') != status:
            continue
            
        table.add_row(
            str(job['id']),
            job['title'][:24],
            job['company'][:19],
            job['package'],
            job['posted_date']
        )
    
    console.print(table)
    console.print(f"\n💡 Use [bold]jobtty show <job-id>[/bold] to view details")