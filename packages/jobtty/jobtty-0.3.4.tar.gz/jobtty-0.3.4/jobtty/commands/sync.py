"""
Synchronization commands for JobTTY preferences
"""

import click
import requests
import json
from datetime import datetime

from ..core.display import console, show_error, show_success, show_info
from ..core.config import JobttyConfig

config = JobttyConfig()

@click.command()
@click.option('--force-upload', is_flag=True, help='Force upload local preferences to server')
@click.option('--force-download', is_flag=True, help='Force download server preferences to local')
def sync(force_upload, force_download):
    """
    🔄 Sync geographic preferences with web platform
    
    Examples:
    jobtty sync                    # Smart sync based on timestamps
    jobtty sync --force-upload     # Force upload local to server
    jobtty sync --force-download   # Force download server to local
    """
    
    if not config.is_authenticated():
        show_error("Please login first using: jobtty login")
        return
    
    console.print("\n[bold bright_cyan]🔄 JobTTY Preferences Sync[/bold bright_cyan]\n")
    
    try:
        # Get API endpoint
        api_base = config.get_api_endpoints()['jobtty']
        auth_token = config.get_auth_token('jobtty')
        
        if not auth_token:
            show_error("No authentication token found. Please login again.")
            return
        
        # Get user profile to find user ID
        profile_response = requests.get(
            f'{api_base}/auth/profile',
            headers={'Authorization': f'Bearer {auth_token}'},
            timeout=10
        )
        
        if profile_response.status_code != 200:
            show_error("Could not get user profile. Please login again.")
            return
        
        user_data = profile_response.json()
        user_id = user_data['user']['id']
        
        # Prepare sync data
        local_prefs = get_local_geographic_preferences()
        sync_url = f'{api_base}/users/{user_id}/sync_preferences'
        
        if force_upload:
            # Force upload local preferences to server
            result = upload_preferences_to_server(sync_url, auth_token, local_prefs)
        elif force_download:
            # Force download server preferences to local
            result = download_preferences_from_server(sync_url, auth_token)
        else:
            # Smart sync based on timestamps
            result = smart_sync_preferences(sync_url, auth_token, local_prefs)
        
        if result:
            show_success("Preferences synchronized successfully!")
            display_sync_result(result)
        else:
            show_error("Synchronization failed")
            
    except requests.RequestException as e:
        show_error(f"Network error: {str(e)}")
    except Exception as e:
        show_error(f"Sync failed: {str(e)}")

def get_local_geographic_preferences():
    """Get current local geographic preferences"""
    return {
        'preferred_countries': config.get('preferred_countries', []),
        'preferred_cities': config.get('preferred_cities', []),
        'use_location_filtering': config.get('use_location_filtering', True),
        'include_remote': config.get('include_remote', True),
        'show_relocation_jobs': config.get('show_relocation_jobs', False),
        'client_preferences_updated_at': config.get('preferences_updated_at')
    }

def upload_preferences_to_server(url, token, preferences):
    """Upload local preferences to server"""
    console.print("📤 Uploading local preferences to server...")
    
    response = requests.post(url, 
        json=preferences,
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        },
        timeout=15
    )
    
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            # Update local timestamp
            server_prefs = data['preferences']
            update_local_preferences_timestamp(server_prefs.get('preferences_updated_at'))
            return data
        else:
            show_error(f"Server error: {data.get('message', 'Unknown error')}")
            return None
    else:
        show_error(f"Upload failed: HTTP {response.status_code}")
        return None

def download_preferences_from_server(url, token):
    """Download server preferences to local"""
    console.print("📥 Downloading server preferences...")
    
    response = requests.post(url,
        headers={'Authorization': f'Bearer {token}'},
        timeout=15
    )
    
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            server_prefs = data['preferences']
            merge_server_preferences_to_local(server_prefs)
            return data
        else:
            show_error(f"Server error: {data.get('message', 'Unknown error')}")
            return None
    else:
        show_error(f"Download failed: HTTP {response.status_code}")
        return None

def smart_sync_preferences(url, token, local_prefs):
    """Smart sync based on timestamps"""
    console.print("🤖 Smart sync: checking which preferences are newer...")
    
    response = requests.post(url,
        json=local_prefs,
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        },
        timeout=15
    )
    
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            action = data.get('action', 'unknown')
            server_prefs = data['preferences']
            
            if action == 'download':
                # Server has newer preferences
                merge_server_preferences_to_local(server_prefs)
            elif action == 'upload':
                # Client preferences were uploaded
                update_local_preferences_timestamp(server_prefs.get('preferences_updated_at'))
            # For 'get' action, no changes needed
            
            return data
        else:
            show_error(f"Server error: {data.get('message', 'Unknown error')}")
            return None
    else:
        show_error(f"Sync failed: HTTP {response.status_code}")
        return None

def merge_server_preferences_to_local(server_prefs):
    """Merge server preferences into local config"""
    console.print("🔄 Merging server preferences to local config...")
    
    # Update local config with server values
    config.set('preferred_countries', server_prefs.get('preferred_countries', []))
    config.set('preferred_cities', server_prefs.get('preferred_cities', []))
    config.set('use_location_filtering', server_prefs.get('use_location_filtering', True))
    config.set('include_remote', server_prefs.get('include_remote', True))
    config.set('show_relocation_jobs', server_prefs.get('show_relocation_jobs', False))
    
    # Update timestamp
    update_local_preferences_timestamp(server_prefs.get('preferences_updated_at'))

def update_local_preferences_timestamp(timestamp):
    """Update local preferences timestamp"""
    if timestamp:
        config.set('preferences_updated_at', timestamp)

def display_sync_result(result):
    """Display sync result in a nice format"""
    action = result.get('action', 'unknown')
    message = result.get('message', '')
    prefs = result.get('preferences', {})
    
    console.print(f"\n✨ [bold green]{message}[/bold green]")
    
    if action == 'upload':
        console.print("📤 [yellow]Local preferences uploaded to server[/yellow]")
    elif action == 'download':
        console.print("📥 [yellow]Server preferences downloaded to local[/yellow]")
    elif action == 'get':
        console.print("📋 [yellow]Preferences retrieved (no changes needed)[/yellow]")
    
    # Show current preferences
    console.print("\n📍 [bold]Current Geographic Preferences:[/bold]")
    
    countries = prefs.get('preferred_countries', [])
    cities = prefs.get('preferred_cities', [])
    
    if countries:
        console.print(f"   🌍 Countries: {', '.join(countries)}")
    if cities:
        console.print(f"   🏙️  Cities: {', '.join(cities)}")
    
    console.print(f"   🔍 Location filtering: {'✅' if prefs.get('use_location_filtering') else '❌'}")
    console.print(f"   🌐 Include remote: {'✅' if prefs.get('include_remote') else '❌'}")
    console.print(f"   ✈️  Show relocation jobs: {'✅' if prefs.get('show_relocation_jobs') else '❌'}")
    
    if prefs.get('preferences_updated_at'):
        console.print(f"\n🕒 Last updated: {prefs['preferences_updated_at']}")

@click.command()
def status():
    """
    📊 Show synchronization status
    """
    
    if not config.is_authenticated():
        show_error("Please login first using: jobtty login")
        return
    
    console.print("\n[bold bright_cyan]📊 JobTTY Sync Status[/bold bright_cyan]\n")
    
    # Show local preferences
    local_prefs = get_local_geographic_preferences()
    
    console.print("[bold]Local Preferences:[/bold]")
    countries = local_prefs.get('preferred_countries', [])
    cities = local_prefs.get('preferred_cities', [])
    
    if countries:
        console.print(f"   🌍 Countries: {', '.join(countries)}")
    else:
        console.print("   🌍 Countries: [dim]None set[/dim]")
        
    if cities:
        console.print(f"   🏙️  Cities: {', '.join(cities)}")
    else:
        console.print("   🏙️  Cities: [dim]None set[/dim]")
    
    console.print(f"   🔍 Location filtering: {'✅' if local_prefs.get('use_location_filtering') else '❌'}")
    console.print(f"   🌐 Include remote: {'✅' if local_prefs.get('include_remote') else '❌'}")
    console.print(f"   ✈️  Show relocation jobs: {'✅' if local_prefs.get('show_relocation_jobs') else '❌'}")
    
    last_sync = local_prefs.get('client_preferences_updated_at')
    if last_sync:
        console.print(f"\n🕒 Last sync: {last_sync}")
    else:
        console.print("\n🕒 [yellow]Never synced with server[/yellow]")
    
    console.print(f"\n💡 [dim]Use 'jobtty sync' to synchronize with web platform[/dim]")