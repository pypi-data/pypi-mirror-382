"""
Profile management commands for Jobtty.io
"""

import click
import os
from pathlib import Path
from rich.prompt import Prompt, Confirm
from rich.console import Console

from ..core.display import console, show_error, show_success, show_info
from ..core.config import JobttyConfig
from ..core.api_client import JobttyAPI

config = JobttyConfig()
api = JobttyAPI()

@click.group()
def profile():
    """
    👤 Manage your JobTTY profile
    """
    pass

@profile.command()
@click.argument('cv_path', required=False)
@click.option('--text', help='CV content as text instead of file')
def upload_cv(cv_path, text):
    """
    📄 Upload your CV to your profile
    
    Examples:
    jobtty profile upload-cv /path/to/cv.pdf
    jobtty profile upload-cv --text "My CV content here"
    """
    
    if not config.is_authenticated():
        show_error("🔐 You need to login first")
        if Confirm.ask("Login now?"):
            # Redirect to auth - user needs to login first
            console.print("💡 Please run: jobtty login")
        return
    
    console.print("\n[bold bright_cyan]📄 CV Upload[/bold bright_cyan]\n")
    
    if text:
        # Upload CV as text
        console.print("📝 Uploading CV as text...")
        try:
            result = api.upload_cv_text(text)
            show_success("✅ CV uploaded successfully!")
            console.print("💼 Your CV is now attached to your profile")
            console.print("🚀 You can now apply to jobs and your CV will be included automatically")
        except Exception as e:
            show_error(f"Failed to upload CV: {str(e)}")
            
    elif cv_path:
        # Upload CV file
        cv_file = Path(cv_path)
        
        if not cv_file.exists():
            show_error(f"❌ File not found: {cv_path}")
            return
            
        if not cv_file.suffix.lower() in ['.pdf', '.doc', '.docx', '.txt']:
            show_error("❌ Supported formats: PDF, DOC, DOCX, TXT")
            return
            
        console.print(f"📁 Uploading: {cv_file.name}")
        
        try:
            result = api.upload_cv_file(cv_path)
            show_success("✅ CV uploaded successfully!")
            console.print("💼 Your CV is now attached to your profile")
            console.print("🚀 You can now apply to jobs and your CV will be included automatically")
        except Exception as e:
            show_error(f"Failed to upload CV: {str(e)}")
    else:
        # Interactive mode
        choice = Prompt.ask(
            "How would you like to upload your CV?",
            choices=["file", "text"],
            default="file"
        )
        
        if choice == "file":
            cv_path = Prompt.ask("📁 Path to your CV file")
            # Recursive call with the path
            upload_cv.callback(cv_path, None)
        else:
            console.print("📝 Enter your CV content (press Ctrl+D when done):")
            cv_lines = []
            try:
                while True:
                    line = input()
                    cv_lines.append(line)
            except EOFError:
                pass
            
            cv_text = "\n".join(cv_lines)
            if cv_text.strip():
                # Recursive call with text
                upload_cv.callback(None, cv_text)
            else:
                show_error("❌ No CV content provided")

@profile.command()
def show():
    """
    👁️ Show your profile information
    """
    
    user = {}

    if config.is_authenticated():
        try:
            profile_data = api.get_profile()
            user = profile_data.get('user', {})
        except Exception as e:
            show_error(f"Failed to get profile: {str(e)}")
    else:
        show_error("🔐 Not logged in. Showing local preferences only. Run: jobtty login to sync profile.")

    console.print("\n[bold bright_cyan]👤 Your Profile[/bold bright_cyan]\n")

    if user:
        console.print(f"📧 Email: {user.get('email', 'N/A')}")
        console.print(f"👤 Name: {user.get('name', 'N/A')}")
        console.print(f"📱 Phone: {user.get('phone', 'Not set')}")
        console.print(f"💼 CV Attached: {'✅ Yes' if user.get('cv_attached') else '❌ No'}")

        if not user.get('cv_attached'):
            console.print("\n💡 Upload your CV: jobtty profile upload-cv")
    else:
        console.print("📧 Email: Not available (offline mode)")
        console.print("👤 Name: Not available")

    console.print("\n[bold bright_cyan]🎯 Job Preferences[/bold bright_cyan]")

    preferred_countries = config.get('preferred_countries', [])
    preferred_cities = config.get('preferred_cities', [])
    relocate_pref = config.get('preference_relocate', False)
    visa_status = config.get('preference_visa_status', 'Not set')
    timezone_pref = config.get('preference_timezone', '') or 'Not set'
    languages_pref = config.get('preference_languages', [])
    include_remote = config.get('include_remote', True)
    location_filtering = config.get('use_location_filtering', True)

    countries_display = ', '.join(preferred_countries) if preferred_countries else 'None set'
    cities_display = ', '.join(preferred_cities) if preferred_cities else 'None set'
    languages_display = ', '.join(languages_pref) if languages_pref else 'Not set'
    relocate_display = 'Willing to relocate' if relocate_pref else 'Not willing to relocate'

    console.print(f"🌍 Preferred countries: {countries_display}")
    console.print(f"🏙️ Preferred cities: {cities_display}")
    console.print(f"✈️ Relocation: {relocate_display}")
    console.print(f"🛂 Visa status: {visa_status}")
    console.print(f"🕒 Timezone: {timezone_pref}")
    console.print(f"🗣️ Languages: {languages_display}")
    console.print(f"🔎 Smart location filtering: {'Enabled' if location_filtering else 'Disabled'}")
    console.print(f"💼 Include remote roles: {'Yes' if include_remote else 'No'}")

@profile.command()
def status():
    """
    📊 Show profile completion status
    """
    
    if not config.is_authenticated():
        show_error("🔐 You need to login first. Run: jobtty login")
        return
    
    try:
        profile_data = api.get_profile()
        user = profile_data.get('user', {})
        
        console.print("\n[bold bright_cyan]📊 Profile Status[/bold bright_cyan]\n")
        
        # Calculate completion
        completed_items = []
        total_items = [
            ("Email", user.get('email')),
            ("Name", user.get('name')),
            ("CV", user.get('cv_attached')),
        ]
        
        for item_name, item_value in total_items:
            status = "✅" if item_value else "❌"
            console.print(f"{status} {item_name}")
            if item_value:
                completed_items.append(item_name)
        
        completion_rate = len(completed_items) / len(total_items) * 100
        console.print(f"\n📈 Profile completion: {completion_rate:.0f}%")
        
        if completion_rate < 100:
            console.print("\n💡 Complete your profile to increase your job application success rate!")
            
    except Exception as e:
        show_error(f"Failed to get profile status: {str(e)}")

@profile.command()
@click.argument('action', type=click.Choice(['set', 'add', 'remove', 'list', 'clear']))
@click.argument('countries', required=False)
def countries(action, countries):
    """
    🌍 Manage your preferred countries for job search
    
    Examples:
    jobtty profile countries set "Poland,Germany,Netherlands"
    jobtty profile countries add "USA"
    jobtty profile countries remove "Germany"
    jobtty profile countries list
    jobtty profile countries clear
    """
    
    current_countries = config.get('preferred_countries', [])
    
    if action == 'list':
        console.print("\n[bold bright_cyan]🌍 Your Preferred Countries[/bold bright_cyan]\n")
        if current_countries:
            for i, country in enumerate(current_countries, 1):
                console.print(f"  {i}. {country}")
        else:
            console.print("  No preferred countries set")
        console.print(f"\n💡 Use: jobtty profile countries set \"Poland,Germany,USA\"")
        return
    
    if action == 'clear':
        config.set('preferred_countries', [])
        show_success("✅ Cleared all preferred countries")
        return
    
    if not countries:
        show_error("❌ Please specify countries")
        return
    
    # Parse countries input
    country_list = [c.strip() for c in countries.split(',')]
    
    if action == 'set':
        config.set('preferred_countries', country_list)
        show_success(f"✅ Set preferred countries: {', '.join(country_list)}")
    
    elif action == 'add':
        for country in country_list:
            if country not in current_countries:
                current_countries.append(country)
        config.set('preferred_countries', current_countries)
        show_success(f"✅ Added countries: {', '.join(country_list)}")
    
    elif action == 'remove':
        for country in country_list:
            if country in current_countries:
                current_countries.remove(country)
        config.set('preferred_countries', current_countries)
        show_success(f"✅ Removed countries: {', '.join(country_list)}")

@profile.command()
@click.argument('action', type=click.Choice(['set', 'add', 'remove', 'list', 'clear']))
@click.argument('cities', required=False)
def cities(action, cities):
    """
    🏙️ Manage your preferred cities for job search
    
    Examples:
    jobtty profile cities set "Rzeszów,Kraków,Warsaw"
    jobtty profile cities add "London"
    jobtty profile cities remove "Berlin"
    jobtty profile cities list
    jobtty profile cities clear
    """
    
    current_cities = config.get('preferred_cities', [])
    
    if action == 'list':
        console.print("\n[bold bright_cyan]🏙️ Your Preferred Cities[/bold bright_cyan]\n")
        if current_cities:
            for i, city in enumerate(current_cities, 1):
                console.print(f"  {i}. {city}")
        else:
            console.print("  No preferred cities set")
        console.print(f"\n💡 Use: jobtty profile cities set \"Rzeszów,Kraków,London\"")
        return
    
    if action == 'clear':
        config.set('preferred_cities', [])
        show_success("✅ Cleared all preferred cities")
        return
    
    if not cities:
        show_error("❌ Please specify cities")
        return
    
    # Parse cities input
    city_list = [c.strip() for c in cities.split(',')]
    
    if action == 'set':
        config.set('preferred_cities', city_list)
        show_success(f"✅ Set preferred cities: {', '.join(city_list)}")
    
    elif action == 'add':
        for city in city_list:
            if city not in current_cities:
                current_cities.append(city)
        config.set('preferred_cities', current_cities)
        show_success(f"✅ Added cities: {', '.join(city_list)}")
    
    elif action == 'remove':
        for city in city_list:
            if city in current_cities:
                current_cities.remove(city)
        config.set('preferred_cities', current_cities)
        show_success(f"✅ Removed cities: {', '.join(city_list)}")

@profile.command()
@click.argument('setting', type=click.Choice(['relocate', 'visa-status', 'timezone', 'language']))
@click.argument('value', required=False)
def preferences(setting, value):
    """
    ⚙️ Manage job search preferences
    
    Examples:
    jobtty profile preferences relocate true
    jobtty profile preferences visa-status "EU-citizen"
    jobtty profile preferences timezone "Europe/Warsaw"
    jobtty profile preferences language "Polish,English"
    """
    
    if not value:
        # Show current value
        current_value = config.get(f'preference_{setting.replace("-", "_")}', 'Not set')
        console.print(f"\n[bold bright_cyan]⚙️ {setting.title()}[/bold bright_cyan]: {current_value}\n")
        return
    
    if setting == 'relocate':
        relocate_value = value.lower() in ['true', 'yes', '1', 'on']
        config.set('preference_relocate', relocate_value)
        status = "willing" if relocate_value else "not willing"
        show_success(f"✅ You are {status} to relocate for job opportunities")
    
    elif setting == 'visa-status':
        valid_statuses = ['EU-citizen', 'US-citizen', 'Visa-required', 'Work-permit']
        if value in valid_statuses:
            config.set('preference_visa_status', value)
            show_success(f"✅ Set visa status: {value}")
        else:
            show_error(f"❌ Valid options: {', '.join(valid_statuses)}")
    
    elif setting == 'timezone':
        config.set('preference_timezone', value)
        show_success(f"✅ Set preferred timezone: {value}")
    
    elif setting == 'language':
        languages = [lang.strip() for lang in value.split(',')]
        config.set('preference_languages', languages)
        show_success(f"✅ Set languages: {', '.join(languages)}")
