#!/usr/bin/env python3
"""
Jobtty.io - Terminal Job Board CLI
Main entry point for the command-line interface
"""

import click
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
import sys
import os

from .core.display import show_startup_banner, show_matrix_effect, console, show_error, show_success
from .core.config import JobttyConfig
from .commands import search, auth, searches, daemon, companies, profile, cleanup, sync

# Global console
console = Console()
app_config = JobttyConfig()

@click.group(invoke_without_command=True)
@click.option('--version', is_flag=True, help='Show version information')
@click.option('--no-banner', is_flag=True, help='Skip startup banner')
@click.option('--fast', is_flag=True, help='Fast mode - skip animations')
@click.pass_context
def main(ctx, version, no_banner, fast):
    """
    🚀 JobTTY - Terminal Job Board
    
    Find your next role from the command line.
    The modern way to search and apply for tech jobs.
    """
    
    if version:
        from . import __version__
        show_startup_banner()
        console.print(f"\nJobTTY v{__version__}")
        console.print("Made with ❤️  by Croscom Software")
        console.print("🌐 https://jobtty.io")
        return
    
    # If no command provided, show interactive menu
    if ctx.invoked_subcommand is None:
        if not no_banner:
            if not fast:  # Skip matrix effect in fast mode
                show_matrix_effect()
            show_startup_banner()
        
        show_interactive_menu()

def show_interactive_menu():
    """Show interactive terminal menu"""
    console.print("\n[bold bright_cyan]What would you like to do?[/bold bright_cyan]\n")
    
    options = [
        ("1", "🔍 Search Jobs", "search"),
        ("2", "👤 Login/Account", "auth"),
        ("3", "⚙️  Configuration", "config"),
        ("q", "🚪 Quit", "quit")
    ]
    
    for key, description, _ in options:
        console.print(f"  [{key}] {description}")
    
    console.print()
    choice = Prompt.ask("Enter your choice", choices=[opt[0] for opt in options])
    
    if choice == "q":
        console.print("👋 See you later! Happy job hunting!")
        sys.exit(0)
    elif choice == "1":
        # Quick search
        query = Prompt.ask("Search for jobs")
        ctx = click.Context(search.search_jobs)
        ctx.invoke(search.search_jobs, query=query)
    elif choice == "2":
        show_auth_menu()
    elif choice == "3":
        show_config_menu()

def show_premium_options():
    """Show premium features menu"""
    console.print("\n[bold bright_yellow]💎 Premium Features[/bold bright_yellow]\n")
    console.print("1. Featured Job Posting (£29/month)")
    console.print("2. Priority Placement (£49/month)")
    console.print("3. Company Branding (£99/month)")
    console.print("4. Analytics Dashboard (£19/month)")
    console.print()
    
    if Confirm.ask("Would you like to purchase premium features?"):
        console.print("🚀 Opening Stripe checkout...")
        # TODO: Implement Stripe flow

def show_auth_menu():
    """Show authentication menu"""
    if app_config.is_authenticated():
        user_info = app_config.get_user_info()
        console.print(f"\n✅ Logged in as: [bright_green]{user_info.get('email', 'Unknown')}[/bright_green]")
        
        if Confirm.ask("Would you like to logout?"):
            app_config.logout()
            show_success("Logged out successfully!")
    else:
        console.print("\n🔐 You are not logged in")
        if Confirm.ask("Would you like to login?"):
            email = Prompt.ask("Email")
            password = Prompt.ask("Password", password=True)
            
            # Use the same auth function as the login command
            from .commands.auth import authenticate_real
            console.print(f"\n🔄 Logging into jobtty...")
            
            try:
                success, token = authenticate_real(email, password)
                
                if success:
                    # Store authentication token securely
                    app_config.set_auth_token('jobtty', token)
                    
                    # Store user info
                    user_info = {
                        'email': email,
                        'service': 'jobtty',
                        'first_name': email.split('@')[0].capitalize(),
                        'last_name': 'User'
                    }
                    app_config.set_user_info(user_info)
                    
                    show_success("Logged into JobTTY successfully!")
                    console.print(f"👤 Welcome, [bright_green]{email}[/bright_green]!")
                    
                else:
                    # Error messages are already shown by authenticate_real()
                    pass
                    
            except Exception as e:
                show_error(f"Login failed: {str(e)}")

def show_config_menu():
    """Show configuration menu"""
    console.print("\n[bold bright_cyan]⚙️  Configuration[/bold bright_cyan]\n")
    
    current_config = app_config.get_all_settings()
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Setting", style="bright_yellow")
    table.add_column("Current Value", style="bright_white")
    
    for key, value in current_config.items():
        table.add_row(key, str(value))
    
    console.print(table)

# Add individual commands
main.add_command(search.search_jobs, name="search")
main.add_command(search.show_job, name="show")
main.add_command(search.list_jobs, name="list")
main.add_command(search.save_job, name="save")
main.add_command(search.apply_job, name="apply")
main.add_command(auth.login, name="login")
main.add_command(auth.register, name="register")
main.add_command(auth.logout, name="logout")
main.add_command(auth.whoami, name="whoami")

# Removed bloat features for v0.3.0 FOCUS:
# - Challenge system (challenges, submit, leaderboard, sponsor)
# - AI Assistant (ai, hint, explain)
# - Collaboration (pair, recruit)
# - Git integration
# - Shell integration
# - Premium features (buy, billing, dashboard)

# Saved Search commands
main.add_command(searches.searches, name="searches")

# Profile commands
main.add_command(profile.profile, name="profile")

# Background Daemon commands
main.add_command(daemon.daemon, name="daemon")


# Company commands
main.add_command(companies.companies, name="companies")
main.add_command(companies.company, name="company")

# Cleanup commands
main.add_command(cleanup.cleanup_searches, name="cleanup-searches")
main.add_command(cleanup.cleanup_matches, name="cleanup-matches")
main.add_command(cleanup.cleanup_all, name="cleanup")

# Sync commands
main.add_command(sync.sync, name="sync")
main.add_command(sync.status, name="status")

@main.command()
@click.option('--location', help='Set default location')
@click.option('--currency', help='Set currency (GBP, USD, EUR)')
@click.option('--show', is_flag=True, help='Show current configuration')
def config(location, currency, show):
    """Configure Jobtty settings"""
    if show:
        show_config_menu()
        return
    
    if location:
        app_config.set('location', location)
        show_success(f"Location set to: {location}")
    
    if currency:
        app_config.set('currency', currency)
        show_success(f"Currency set to: {currency}")

@main.command()
def clear():
    """Clear the terminal"""
    console.clear()
    show_startup_banner()

if __name__ == "__main__":
    main()