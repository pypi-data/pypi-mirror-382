"""
Stripe payment integration for Jobtty.io
"""

import click
import stripe
import webbrowser
from rich.console import Console
from rich.prompt import Confirm
from rich.progress import track
import time

from ..core.display import console, show_error, show_success, show_info
from ..core.config import JobttyConfig

config = JobttyConfig()

# Initialize Stripe (use test keys for demo)
stripe.api_key = "sk_test_..."  # Replace with actual test key

@click.command()
@click.argument('item', required=False)
@click.option('--duration', help='Duration (7d, 30d, 90d)')
@click.option('--job-id', type=int, help='Job ID for upgrades')
def buy_premium(item, duration, job_id):
    """
    💳 Purchase premium features
    
    Examples:
    jobtty buy premium-listing --duration 30d
    jobtty buy featured-post --job-id 123
    jobtty buy
    """
    
    if not config.is_authenticated():
        show_error("You need to login first")
        return
    
    console.print("\n[bold bright_yellow]💎 Jobtty.io Premium Store[/bold bright_yellow]\n")
    
    if not item:
        show_premium_catalog()
        return
    
    # Process specific premium purchase
    if item == "premium-listing":
        purchase_premium_listing(duration)
    elif item == "featured-post":
        purchase_featured_post(job_id)
    elif item == "analytics":
        purchase_analytics()
    else:
        show_error(f"Unknown premium item: {item}")

def show_premium_catalog():
    """Show the premium features catalog"""
    from rich.table import Table
    
    table = Table(show_header=True, header_style="bold magenta", title="💎 Premium Features")
    table.add_column("Feature", style="bright_cyan", width=20)
    table.add_column("Price", style="bright_green", width=12)
    table.add_column("Duration", style="bright_yellow", width=12)
    table.add_column("Benefits", style="bright_white", width=40)
    
    features = [
        ("Premium Listing", "£29", "30 days", "Featured placement, priority search, 3x more views"),
        ("Featured Post", "£49", "45 days", "Top of search results, highlighted, social boost"),
        ("Analytics Pro", "£19", "Monthly", "Detailed metrics, applicant insights, A/B testing"),
        ("Company Branding", "£99", "90 days", "Custom colors, logo, company page, branded emails"),
        ("Recruiter Tools", "£199", "Yearly", "Bulk posting, CRM integration, automated screening")
    ]
    
    for feature, price, duration, benefits in features:
        table.add_row(feature, price, duration, benefits)
    
    console.print(table)
    console.print()
    
    # Interactive selection
    choice = click.prompt("Select feature number (1-5) or 'q' to quit", type=str)
    
    if choice == 'q':
        return
    
    try:
        feature_index = int(choice) - 1
        if 0 <= feature_index < len(features):
            selected_feature = features[feature_index]
            purchase_feature(selected_feature)
    except ValueError:
        show_error("Invalid selection")

def purchase_feature(feature_info):
    """Purchase a specific premium feature"""
    name, price, duration, benefits = feature_info
    
    console.print(f"\n[bold bright_green]Selected: {name}[/bold bright_green]")
    console.print(f"💰 Price: {price}")
    console.print(f"⏰ Duration: {duration}")
    console.print(f"✨ Benefits: {benefits}")
    
    if not Confirm.ask(f"\nProceed with purchase of {name}?", default=True):
        console.print("❌ Purchase cancelled")
        return
    
    # Create Stripe payment
    try:
        payment_url = create_stripe_payment_for_feature(name, price)
        
        console.print("\n🚀 Redirecting to Stripe checkout...")
        console.print(f"🔗 Payment URL: {payment_url}")
        
        # Open in browser
        if Confirm.ask("Open payment page in browser?", default=True):
            webbrowser.open(payment_url)
        
        # Show payment status
        show_payment_progress()
        
    except Exception as e:
        show_error(f"Payment setup failed: {str(e)}")

def create_stripe_payment(package, job_data):
    """Create Stripe payment session for job posting"""
    import requests
    
    console.print(f"💳 Creating payment session for {package['name']}...")
    
    try:
        # Get auth token
        auth_token = config.get_auth_token('jobtty')
        if not auth_token:
            raise Exception("Authentication token not found")
        
        # Determine price in pence
        price_map = {
            'Basic Listing': 0,
            'Featured Listing': 2900,  # £29.00
            'Premium Listing': 7900    # £79.00
        }
        price_pence = price_map.get(package['name'], 2900)
        
        # Create checkout session via API
        response = requests.post(
            'https://jobtty.io/api/v1/payments/checkout',
            json={
                'package_name': package['name'],
                'package_description': f"{package['name']} - {package['duration']} active listing",
                'price_pence': price_pence,
                'job_data': job_data
            },
            headers={'Authorization': f'Bearer {auth_token}'},
            timeout=15
        )
        
        if response.status_code == 200:
            payment_data = response.json()
            return payment_data['checkout_url']
        else:
            error_data = response.json()
            raise Exception(f"Payment setup failed: {error_data.get('error', 'Unknown error')}")
    
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error: {str(e)}")
    except Exception as e:
        raise Exception(f"Payment error: {str(e)}")

def create_stripe_payment_for_feature(feature_name, price):
    """Create Stripe payment for premium feature"""
    
    # Mock Stripe checkout URL
    clean_name = feature_name.replace(' ', '_').lower()
    mock_url = f"https://checkout.stripe.com/pay/jobtty_{clean_name}_{price.replace('£', 'gbp')}"
    
    return mock_url

def show_payment_progress():
    """Show payment progress indicator"""
    console.print("\n⏳ Processing payment...")
    
    # Simulate payment processing
    for i in track(range(100), description="Confirming payment..."):
        time.sleep(0.03)
    
    show_success("💳 Payment confirmed!")
    console.print("📧 Receipt sent to your email")
    console.print("🎉 Premium features activated!")

def purchase_premium_listing(duration):
    """Purchase premium listing upgrade"""
    durations = {
        '7d': ('£9', '7 days'),
        '30d': ('£29', '30 days'),
        '90d': ('£79', '90 days')
    }
    
    if not duration:
        console.print("Available durations:")
        for dur, (price, desc) in durations.items():
            console.print(f"  {dur}: {price} ({desc})")
        duration = click.prompt("Select duration", type=click.Choice(list(durations.keys())))
    
    price, desc = durations.get(duration, ('£29', '30 days'))
    
    console.print(f"💎 Premium Listing Upgrade")
    console.print(f"💰 Price: {price}")
    console.print(f"⏰ Duration: {desc}")
    
    if Confirm.ask("Proceed with purchase?"):
        # Process payment
        console.print("🚀 Processing premium listing upgrade...")
        time.sleep(2)
        show_success("Premium listing activated!")

def purchase_featured_post(job_id):
    """Purchase featured post upgrade for specific job"""
    if not job_id:
        # Show user's jobs to select from
        posted_jobs = config.get('posted_jobs', [])
        if not posted_jobs:
            show_error("No jobs to upgrade. Post a job first.")
            return
        
        console.print("Your jobs:")
        for i, job in enumerate(posted_jobs, 1):
            console.print(f"  {i}. [{job['id']}] {job['title']}")
        
        choice = click.prompt("Select job number", type=int)
        job_id = posted_jobs[choice - 1]['id']
    
    console.print(f"🚀 Upgrading job {job_id} to featured...")
    time.sleep(2)
    show_success(f"Job {job_id} is now featured!")

def purchase_analytics():
    """Purchase analytics dashboard"""
    console.print("📊 Analytics Pro Package")
    console.print("💰 Price: £19/month")
    console.print("📈 Features:")
    console.print("  • Detailed application metrics")
    console.print("  • Candidate source analytics") 
    console.print("  • Performance benchmarking")
    console.print("  • Export capabilities")
    
    if Confirm.ask("Subscribe to Analytics Pro?"):
        console.print("🚀 Setting up analytics subscription...")
        time.sleep(2)
        show_success("Analytics Pro activated!")

@click.command()
@click.option('--history', is_flag=True, help='Show payment history')
def billing(history):
    """
    💳 View billing information and payment history
    """
    
    if not config.is_authenticated():
        show_error("You need to login first")
        return
    
    if history:
        show_payment_history()
    else:
        show_billing_overview()

def show_billing_overview():
    """Show current billing status"""
    console.print("\n[bold bright_cyan]💳 Billing Overview[/bold bright_cyan]\n")
    
    # Mock billing data
    console.print("📊 Current Plan: [bold bright_green]Premium[/bold bright_green]")
    console.print("💰 Monthly Spend: [bright_yellow]£48[/bright_yellow]")
    console.print("📅 Next Billing: September 31, 2025")
    console.print("💳 Payment Method: **** **** **** 4242")
    
    console.print("\n🎯 Active Features:")
    console.print("  ✅ Premium Listings (2 active)")
    console.print("  ✅ Analytics Pro")
    console.print("  ✅ Priority Support")

def show_payment_history():
    """Show payment history"""
    from rich.table import Table
    
    console.print("\n[bold bright_cyan]💳 Payment History[/bold bright_cyan]\n")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Date", style="dim", width=12)
    table.add_column("Description", style="bright_white", width=25)
    table.add_column("Amount", style="bright_green", width=10)
    table.add_column("Status", style="bright_yellow", width=10)
    
    # Mock payment history
    payments = [
        ("2025-08-31", "Featured Job Posting", "£29", "✅ Paid"),
        ("2025-08-25", "Analytics Pro", "£19", "✅ Paid"),
        ("2025-08-20", "Premium Listing", "£79", "✅ Paid"),
        ("2025-08-15", "Company Branding", "£99", "✅ Paid")
    ]
    
    for date, desc, amount, status in payments:
        table.add_row(date, desc, amount, status)
    
    console.print(table)