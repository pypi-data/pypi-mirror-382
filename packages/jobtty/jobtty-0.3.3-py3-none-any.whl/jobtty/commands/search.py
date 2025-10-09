"""
Job search commands for Jobtty.io
"""

import re
from datetime import datetime

import click
from rich.prompt import Prompt, Confirm
from rich.table import Table

from ..core.display import console, create_jobs_table, show_job_details, show_error, show_success
from ..core.api_client import JobttyAPI
from ..core.config import JobttyConfig
from ..core.saved_searches import save_current_search

MAX_HISTORY_LENGTH = 50
COMMON_QUERY_TERMS = {
    'developer', 'engineer', 'senior', 'junior', 'lead', 'principal', 'remote',
    'job', 'jobs', 'role', 'the', 'and', 'with', 'for'
}

config = JobttyConfig()
api = JobttyAPI()


def parse_salary_range_from_text(text, ignore_reward=False):
    """Return (min, max) salary values extracted from text"""
    if not text:
        return None, None

    value_str = str(text)
    if ignore_reward and value_str.lower().find('reward') != -1:
        return None, None
    if ignore_reward and value_str.lower().find('bonus') != -1:
        return None, None

    sanitized = re.sub(r'[£€$]', '', value_str)
    sanitized = sanitized.replace(',', '').replace(' ', '')

    tokens = re.findall(r'\d+(?:\.\d+)?k?', sanitized, flags=re.IGNORECASE)
    if not tokens:
        return None, None

    values = []
    for token in tokens:
        lower_token = token.lower()
        if lower_token.endswith('k'):
            number_part = lower_token[:-1]
            try:
                values.append(int(float(number_part) * 1000))
            except ValueError:
                continue
        else:
            try:
                values.append(int(float(lower_token)))
            except ValueError:
                continue

    values = [val for val in values if val > 0]
    if not values:
        return None, None

    return min(values), max(values)


def parse_salary(salary_str) -> int:
    """Parse salary input to integer minimum"""
    if salary_str is None or str(salary_str) == 'Sentinel.UNSET':
        return 0

    if isinstance(salary_str, (int, float)):
        return int(salary_str)

    minimum, _ = parse_salary_range_from_text(salary_str, ignore_reward=False)
    return minimum or 0


def filter_jobs_by_salary(jobs, minimum):
    """Filter job list by minimum salary"""
    if minimum <= 0:
        return jobs

    filtered = []
    for job in jobs:
        job_min = job.get('salary_min')
        job_max = job.get('salary_max')

        if job_min is None and job_max is None:
            job_min, job_max = parse_salary_range_from_text(job.get('salary'), ignore_reward=True)

        if job_min is None and job_max is None:
            continue

        if (job_min and job_min >= minimum) or (job_max and job_max >= minimum):
            filtered.append(job)

    return filtered


def job_matches_query(job, query):
    """Ensure job data matches query tokens to keep results relevant"""
    if not query:
        return True

    haystack = " ".join([
        str(job.get('title', '')),
        str(job.get('description', '')),
        str(job.get('category', '')),
        str(job.get('company', ''))
    ]).lower()

    if not haystack.strip():
        return False

    normalized_query = re.sub(r'\s+', ' ', query.strip().lower())
    if normalized_query and normalized_query in haystack:
        return True

    tokens = [tok for tok in re.split(r'\W+', normalized_query) if tok]
    if not tokens:
        return True

    meaningful_tokens = [tok for tok in tokens if len(tok) >= 3 and tok not in COMMON_QUERY_TERMS]
    tokens_to_check = meaningful_tokens or tokens

    return any(token in haystack for token in tokens_to_check)


def _normalize_history_entries(raw_entries, transform=None):
    if not isinstance(raw_entries, list):
        return []

    normalized = []
    for entry in raw_entries:
        if isinstance(entry, dict):
            normalized.append(entry)
        elif transform:
            transformed = transform(entry)
            if transformed:
                normalized.append(transformed)
    return normalized


def get_normalized_search_history():
    raw_history = config.get('search_history', [])
    return _normalize_history_entries(
        raw_history,
        lambda value: {
            'query': value,
            'params': {},
            'results': None,
            'timestamp': None
        }
    )


def record_search_history(query, params, results_count):
    history = get_normalized_search_history()

    entry = {
        'query': query or '',
        'params': params or {},
        'results': results_count,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }

    history = [item for item in history if not (
        item.get('query') == entry['query'] and item.get('params') == entry['params']
    )]
    history.append(entry)

    config.set('search_history', history[-MAX_HISTORY_LENGTH:])


def get_normalized_application_history():
    raw_history = config.get('applied_history', [])
    return _normalize_history_entries(raw_history)


def record_application_history(job):
    if not job:
        return

    job_id = job.get('id')
    try:
        job_id = int(job_id)
    except (TypeError, ValueError):
        job_id = job.get('id')

    entry = {
        'job_id': job_id,
        'title': job.get('title', 'Unknown role'),
        'company': job.get('company', 'Unknown company'),
        'applied_at': datetime.utcnow().isoformat() + 'Z'
    }

    history = get_normalized_application_history()
    history = [item for item in history if item.get('job_id') != entry['job_id']]
    history.append(entry)

    config.set('applied_history', history[-MAX_HISTORY_LENGTH:])


def format_timestamp(timestamp_str):
    if not timestamp_str:
        return 'time unknown'

    try:
        sanitized = timestamp_str.replace('Z', '+00:00')
        dt = datetime.fromisoformat(sanitized)
        return dt.strftime('%Y-%m-%d %H:%M')
    except (ValueError, TypeError):
        return timestamp_str

@click.command()
@click.argument('query', required=False)
@click.option('--remote', is_flag=True, help='Remote jobs only')
@click.option('--location', help='Job location filter')
@click.option('--salary', help='Minimum salary (e.g., 80k, 120000)')
@click.option('--company', help='Filter by company name')
@click.option('--category', help='Filter by job category (ruby, python, javascript, etc.)')
@click.option('--categories', is_flag=True, help='Show available job categories')
@click.option('--limit', default=20, help='Number of results to show')
@click.option('--source', help='Search specific source (jobtty, external)')
@click.option('--save', '-s', is_flag=True, help='💾 Save this search for notifications')
@click.option('--notify', is_flag=True, help='🔔 Enable instant notifications (default: true)')
@click.option('--name', help='Custom name for saved search')
@click.option('--frequency', type=click.Choice(['instant', 'hourly', 'daily', 'weekly']), default='instant', help='Notification frequency')
@click.option('--country', help='Filter by country (overrides profile preferences)')
@click.option('--global', 'global_search', is_flag=True, help='🌍 Search globally (ignore location preferences)')
@click.option('--local-only', is_flag=True, help='🏠 Only show jobs in preferred countries/cities')
@click.option('--with-relocation', is_flag=True, help='✈️ Include jobs requiring relocation')
def search_jobs(query, remote, location, salary, company, category, categories, limit, source, save, notify, name, frequency, country, global_search, local_only, with_relocation):
    """
    🔍 Search for jobs across all platforms
    
    Examples:
    jobtty search "python developer"                  # Smart location filtering based on preferences
    jobtty search "flutter" --remote --salary 80k
    jobtty search --location "London" --company "Google"
    jobtty search --category=ruby                     # Filter by Ruby jobs
    jobtty search "rails developer" --save --notify  # 🚀 REVOLUTIONARY: Save & get terminal notifications!
    jobtty search "flutter" -s --frequency hourly     # Save with hourly notifications
    
    🌍 Geographic filtering options:
    jobtty search "ruby developer" --local-only      # Only preferred countries/cities
    jobtty search "python dev" --country Poland      # Specific country
    jobtty search "js dev" --global                  # Ignore location preferences  
    jobtty search "senior dev" --with-relocation     # Include relocation jobs
    """
    
    # Show available categories if requested
    if categories:
        console.print("\n[bold bright_cyan]📋 Available Job Categories:[/bold bright_cyan]\n")
        available_categories = [
            "ruby", "python", "javascript", "java", "go", "php", 
            "data", "design", "management", "devops", "mobile", "other"
        ]
        for cat in available_categories:
            console.print(f"  • {cat}")
        console.print(f"\n💡 Use: jobtty search --category=<name>")
        return
    
    # Validate category if provided
    if category:
        valid_categories = [
            "ruby", "python", "javascript", "java", "go", "php", 
            "data", "design", "management", "devops", "mobile", "other"
        ]
        if category.lower() not in [c.lower() for c in valid_categories]:
            show_error(f"Invalid category '{category}'. Use 'jobtty search --categories' to see available options")
            return
    
    if not query and not category and not company and not location and not remote:
        query = Prompt.ask("🔍 Enter search query", default="python developer")
    
    # Show search parameters
    if query:
        console.print(f"\n[bold bright_cyan]Searching for:[/bold bright_cyan] {query}")
    else:
        console.print(f"\n[bold bright_cyan]Searching jobs...[/bold bright_cyan]")
    
    # Show geographic filtering status
    if global_search:
        console.print("🌍 Global search (ignoring location preferences)")
    elif local_only:
        console.print("🏠 Local only (preferred locations)")
    elif country:
        console.print(f"🌍 Country: {country}")
    elif location:
        console.print(f"📍 Location: {location}")
    else:
        # Show if smart filtering is being applied
        use_filtering = config.get('use_location_filtering', True)
        preferred_countries = config.get('preferred_countries', [])
        preferred_cities = config.get('preferred_cities', [])
        
        if use_filtering and (preferred_countries or preferred_cities):
            locations = []
            if preferred_cities:
                locations.extend(preferred_cities)
            if preferred_countries:
                locations.extend(preferred_countries)
            
            include_remote = config.get('include_remote', True)
            if include_remote:
                locations.append("Remote")
            
            if locations:
                console.print(f"🎯 Smart filtering: {', '.join(locations[:3])}{'...' if len(locations) > 3 else ''}")
    
    if remote:
        console.print("🏠 Remote jobs only")
    if salary:
        console.print(f"💰 Min salary: {salary}")
    if company:
        console.print(f"🏢 Company: {company}")
    if category:
        console.print(f"🏷️  Category: {category}")
    if with_relocation:
        console.print("✈️ Including relocation jobs")
    
    console.print()
    
    # Build search parameters - only send non-default values to avoid backend filtering bugs
    search_params = {}
    salary_filter_min = None
    
    # Always include query if provided
    if query:
        search_params["query"] = query
    
    # Handle geographic filtering based on user preferences and command options
    geographic_location = apply_geographic_filtering(location, country, global_search, local_only, with_relocation)
    if geographic_location:
        search_params["location"] = geographic_location
    
    # Only include other parameters if explicitly set by user (not defaults)
    if remote:  # Only if explicitly True
        search_params["remote"] = remote
        
    if salary:  # Only if explicitly provided by user  
        parsed_salary = parse_salary(salary)
        if parsed_salary > 0:
            search_params["salary_min"] = parsed_salary
            salary_filter_min = parsed_salary
        
    if company:
        search_params["company"] = company
        
    if category:
        search_params["category"] = category
        
    # Only set limit if different from default
    if limit != 20:
        search_params["limit"] = limit
    
    if salary_filter_min is None:
        salary_filter_min = search_params.get("salary_min")

    # JobTTY uses single source now
    
    # Search JobTTY API (single source)
    all_jobs = []
    
    with console.status("Searching jobs...", spinner="dots"):
        try:
            jobs = api.search_jobs('jobtty', search_params)
            for job in jobs:
                job['source'] = 'jobtty'
            all_jobs = jobs

            # Client-side category filtering (backend doesn't support it yet)
            if category:
                all_jobs = [job for job in all_jobs if (job.get('category') or '').lower() == category.lower()]

            if query:
                all_jobs = [job for job in all_jobs if job_matches_query(job, query)]

            if salary_filter_min:
                all_jobs = filter_jobs_by_salary(all_jobs, salary_filter_min)
        except Exception as e:
            console.print(f"[dim red]Search failed: {str(e)}[/dim red]")

    history_params = {k: v for k, v in search_params.items() if k != 'query'}
    record_search_history(query, history_params, len(all_jobs))

    if not all_jobs:
        # Smart error message with personalized suggestions
        error_msg = "No jobs found matching your criteria."
        
        suggestions = []
        
        # Suggest removing location filter if specific location was used
        if location and location.lower() not in ['remote', 'any']:
            suggestions.append(f"Try removing location filter: [cyan]jobtty search \"{query}\"[/cyan]")
            suggestions.append(f"Or try broader location: [cyan]jobtty search \"{query}\" --location Remote[/cyan]")
        
        # Suggest removing category filter
        if category:
            suggestions.append(f"Try without category filter: [cyan]jobtty search \"{query}\"[/cyan]")
        
        # Suggest removing company filter
        if company:
            suggestions.append(f"Try broader search: [cyan]jobtty search \"{query}\"[/cyan]")
        
        # Suggest removing salary filter
        if salary:
            suggestions.append(f"Try without salary filter: [cyan]jobtty search \"{query}\"[/cyan]")
        
        # Suggest broader search terms
        if query and len(query.split()) > 1:
            broader_query = query.split()[0]  # Take first word
            suggestions.append(f"Try broader terms: [cyan]jobtty search \"{broader_query}\"[/cyan]")
        
        # Always suggest checking companies and categories
        suggestions.append("Check available companies: [cyan]jobtty companies[/cyan]")
        suggestions.append("Browse job categories: [cyan]jobtty search --categories[/cyan]")
        
        show_error(error_msg)
        console.print("\n💡 [bold]Suggestions:[/bold]")
        for i, suggestion in enumerate(suggestions[:4], 1):  # Show max 4 suggestions
            console.print(f"   {i}. {suggestion}")
        
        return
    
    # Sort by relevance/date
    all_jobs.sort(key=lambda x: x.get('posted_date', ''), reverse=True)
    all_jobs = all_jobs[:limit]
    
    # Display results with fallback support
    try:
        from ..core.fallback_display import safe_print_jobs
        safe_print_jobs(all_jobs)
    except ImportError:
        # Fallback to original display
        console.print(f"\n[bold bright_green]Found {len(all_jobs)} jobs:[/bold bright_green]\n")
        jobs_table = create_jobs_table(all_jobs)
        console.print(jobs_table)
    
    # Handle saved search
    if save or notify:
        save_search_with_options(query, remote, location, salary, company, category, source, notify, name, frequency)
    
    # Interactive job selection
    console.print(f"\n💡 Type [bold]jobtty show <job-id>[/bold] to view details")
    console.print(f"💡 Type [bold]jobtty save <job-id>[/bold] to bookmark")

@click.command()
@click.argument('job_id', type=int)
@click.option('--details', is_flag=True, help='Show full job details')
@click.option('--apply', is_flag=True, help='Apply to this job')
def show_job(job_id, details, apply):
    """
    👁️  Show detailed job information
    
    Examples:
    jobtty show 42
    jobtty show 42 --apply
    """
    
    try:
        job = api.get_job_details(job_id)
        
        if not job:
            show_error(f"Job {job_id} not found")
            return
        
        show_job_details(job)
        
        # Only prompt for apply if --apply flag wasn't used and we're in interactive mode
        if apply:
            apply_to_job(job)
        elif not apply:
            # Check if we're in interactive mode before prompting
            try:
                import sys
                if sys.stdin.isatty():
                    response = Prompt.ask("\n🚀 Would you like to apply?", choices=['y', 'n'], default='n')
                    if response == 'y':
                        apply_to_job(job)
                else:
                    # Non-interactive mode, just show the job details
                    console.print("\n💡 Use [bold]jobtty show <job-id> --apply[/bold] to apply to this job")
            except (EOFError, KeyboardInterrupt):
                # Handle input errors gracefully
                console.print("\n💡 Use [bold]jobtty show <job-id> --apply[/bold] to apply to this job")
            
    except Exception as e:
        show_error(f"Failed to fetch job details: {str(e)}")

def apply_to_job(job, quick=False):
    """Apply to a job through the terminal"""
    console.print(f"\n[bold bright_yellow]📝 Applying to: {job['title']}[/bold bright_yellow]")
    
    if not config.is_authenticated():
        console.print("🔐 You need to login first")
        try:
            # Try interactive login confirmation
            should_login = Confirm.ask("Login now?")
        except (EOFError, KeyboardInterrupt):
            # Non-interactive context, provide helpful message
            console.print("\n💡 To apply for jobs, please login first:")
            console.print("   jobtty login")
            console.print("   Then run: jobtty show {} --apply".format(job['id']))
            return
            
        if should_login:
            # Import and call the login function
            from .auth import login
            import click
            
            try:
                # Call login function with no email parameter (will prompt)
                login(email=None)
            except Exception as e:
                console.print(f"Login failed: {e}")
                return
            
            # Check if login was successful
            if not config.is_authenticated():
                console.print("❌ Login was not completed. Please try again.")
                return
        else:
            return
    
    # Collect application data
    if quick:
        cover_letter = "I am interested in this position and would like to discuss further."
    else:
        try:
            cover_letter = Prompt.ask(
                "Cover letter (optional)", 
                default="I am interested in this position and would like to discuss further."
            )
        except (EOFError, KeyboardInterrupt):
            # Non-interactive context - use default
            cover_letter = "I am interested in this position and would like to discuss further."
    
    try:
        result = api.apply_to_job(job['id'], {
            'cover_letter': cover_letter,
            'source': job.get('source')
        })
        
        show_success(f"✅ Application submitted successfully!")
        console.print(f"📧 Confirmation sent to your email")
        console.print(f"🆔 Application ID: {result.get('application_id')}")
        record_application_history(job)
        
    except Exception as e:
        show_error(f"Failed to submit application: {str(e)}")

@click.command()
@click.option('--saved', is_flag=True, help='Show saved/bookmarked jobs')
@click.option('--recent', is_flag=True, help='Show recent searches')
@click.option('--applied', is_flag=True, help='Show jobs you applied to')
def list_jobs(saved, recent, applied):
    """
    📋 List saved jobs, recent searches, or applications
    """
    
    if saved:
        show_saved_jobs()
    elif recent:
        show_recent_searches()
    elif applied:
        show_applied_jobs()
    else:
        # Default to recent jobs
        show_recent_searches()

def show_saved_jobs():
    """Show user's saved/bookmarked jobs"""
    saved_jobs = config.get('saved_jobs', [])
    
    if not saved_jobs:
        console.print("📝 No saved jobs yet")
        console.print("💡 Use [bold]jobtty save <job-id>[/bold] to bookmark jobs")
        return
    
    console.print(f"[bold bright_cyan]📚 Your Saved Jobs ({len(saved_jobs)}):[/bold bright_cyan]\n")
    
    for job_id in saved_jobs:
        try:
            job = api.get_job_details(job_id)
            console.print(f"🔖 [{job_id}] {job['title']} at {job['company']}")
        except:
            console.print(f"❌ [{job_id}] Job no longer available")

def show_recent_searches():
    """Show recent search history"""
    history = get_normalized_search_history()

    if not history:
        console.print("🔍 No recent searches")
        return

    console.print("[bold bright_cyan]🕐 Recent Searches:[/bold bright_cyan]\n")

    for i, entry in enumerate(reversed(history[-10:]), 1):
        query = entry.get('query') or '(no query)'
        params = entry.get('params') or {}
        filters = [f"{key}={value}" for key, value in params.items() if value not in (None, '', False)]
        filters_text = f" [{', '.join(filters)}]" if filters else ''
        results_info = entry.get('results')
        results_text = f" · {results_info} results" if results_info is not None else ''
        timestamp_text = format_timestamp(entry.get('timestamp'))
        console.print(f"{i}. {query}{filters_text}{results_text} ({timestamp_text})")

def show_applied_jobs():
    """Show jobs user has applied to"""
    history = get_normalized_application_history()

    remote_applications = []
    if config.is_authenticated():
        try:
            remote_applications = api.get_user_applications() or []
        except Exception:
            remote_applications = []

    remote_index = {}
    for app in remote_applications:
        if isinstance(app, dict):
            job_data = app.get('job') or {}
            job_id = job_data.get('id') or app.get('job_id')
            if job_id:
                try:
                    job_id_int = int(job_id)
                    remote_index[job_id_int] = app
                    remote_index[str(job_id_int)] = app
                except (TypeError, ValueError):
                    remote_index[str(job_id)] = app

    if history:
        console.print(f"[bold bright_cyan]📨 Your Applications ({len(history)}):[/bold bright_cyan]\n")

        for i, entry in enumerate(reversed(history[-10:]), 1):
            job_id = entry.get('job_id')
            title = entry.get('title', 'Unknown role')
            company_name = entry.get('company', 'Unknown company')
            applied_at = format_timestamp(entry.get('applied_at'))

            status = 'submitted'
            if job_id and job_id in remote_index:
                status = remote_index[job_id].get('status', status)

            console.print(f"{i}. [{job_id}] {title} at {company_name} · Status: {status} · Applied: {applied_at}")

        if not remote_index and config.is_authenticated() and not remote_applications:
            console.print("\n[dim]Unable to sync application statuses from API (offline mode).[/dim]")
        return

    if remote_applications:
        console.print(f"[bold bright_cyan]📨 Your Applications ({len(remote_applications)}):[/bold bright_cyan]\n")

        app_table = Table(show_header=True, header_style="bold magenta")
        app_table.add_column("Job", style="bright_cyan", width=25)
        app_table.add_column("Company", style="bright_yellow", width=20)
        app_table.add_column("Status", style="bright_green", width=12)
        app_table.add_column("Applied", style="dim", width=12)

        for app in remote_applications:
            job_data = app.get('job') or {}
            job_title = job_data.get('title', 'Unknown job')
            company_name = job_data.get('company_name', 'Unknown company')
            status = app.get('status', 'submitted')
            status_style = "green" if status == 'approved' else "yellow"
            applied_date = app.get('created_at', '')[:10]
            app_table.add_row(
                job_title[:24],
                company_name[:19],
                f"[{status_style}]{status}[/{status_style}]",
                applied_date
            )

        console.print(app_table)
        console.print("\n[dim]Apply to jobs with: jobtty show <job-id> --apply[/dim]")
    else:
        console.print("📄 No applications yet")
        console.print("💡 Apply to your first job with: jobtty show <job-id> --apply")

@click.command()
@click.argument('job_id', type=int)
def save_job(job_id):
    """
    🔖 Save/bookmark a job for later
    """
    saved_jobs = config.get('saved_jobs', [])
    
    if job_id in saved_jobs:
        console.print(f"📌 Job {job_id} is already saved")
        return
    
    saved_jobs.append(job_id)
    config.set('saved_jobs', saved_jobs)
    
    show_success(f"🔖 Job {job_id} saved successfully!")
    console.print("💡 Use [bold]jobtty list --saved[/bold] to see all saved jobs")

def save_search_with_options(query, remote, location, salary, company, category, source, notify, name, frequency):
    """Save current search with notification options"""
    
    # Build search options
    search_options = {
        "query": query,
        "location": location,
        "remote": remote,
        "min_salary": parse_salary(salary) if salary else None,
        "company": company,
        "category": category,
        "source": source,
        "notify": True if notify else True,  # Default to true
        "name": name or f"Search for {query}",
        "frequency": frequency,
        "scope": "all"
    }
    
    # Save the search
    search_id = save_current_search(query, search_options)
    
    console.print(f"\n🎉 [bold bright_green]Search saved![/bold bright_green]")
    console.print(f"📝 Search ID: [cyan]{search_id}[/cyan]")
    console.print(f"🔔 Notifications: [yellow]{frequency}[/yellow]")
    console.print(f"\n[bold bright_yellow]🚀 REVOLUTIONARY FEATURE ACTIVATED![/bold bright_yellow]")
    console.print(f"[dim]You'll now get job notifications directly in your terminal while coding![/dim]")
    console.print(f"\n💡 Manage searches: [bold]jobtty searches list[/bold]")

def apply_geographic_filtering(location, country, global_search, local_only, with_relocation):
    """
    Apply smart geographic filtering based on user preferences and command options
    
    Priority order:
    1. Global search flag (--global) - ignore all geographic preferences
    2. Explicit location/country options - override preferences
    3. Local-only flag (--local-only) - only use preferred locations
    4. Default: use location preferences from config
    """
    
    # If global search requested, ignore all geographic filtering
    if global_search:
        return None
    
    # If explicit location provided, use it directly
    if location:
        return location
    
    # If explicit country provided, use it
    if country:
        return country
    
    # If local-only flag is set, build location from preferences
    if local_only:
        preferred_countries = config.get('preferred_countries', [])
        preferred_cities = config.get('preferred_cities', [])
        
        # Combine cities and countries into location filter
        locations = []
        if preferred_cities:
            locations.extend(preferred_cities)
        if preferred_countries:
            locations.extend(preferred_countries)
        
        if locations:
            return ",".join(locations)  # API can handle comma-separated locations
        return None
    
    # Default behavior: apply smart location filtering if enabled in config
    use_location_filtering = config.get('use_location_filtering', True)
    show_relocation_jobs = config.get('show_relocation_jobs', False)
    
    if not use_location_filtering:
        return None
    
    # Don't show relocation jobs unless explicitly requested
    if not with_relocation and not show_relocation_jobs:
        preferred_countries = config.get('preferred_countries', [])
        preferred_cities = config.get('preferred_cities', [])
        
        # Build smart location filter
        locations = []
        if preferred_cities:
            locations.extend(preferred_cities)
        if preferred_countries:
            locations.extend(preferred_countries)
        
        # Always include remote if configured
        include_remote = config.get('include_remote', True)
        if include_remote:
            locations.append("Remote")
        
        if locations:
            return ",".join(locations)
    
    return None

def parse_salary(salary_str) -> int:
    """Parse salary string to integer"""
    # Handle None, empty strings, and Click Sentinel objects
    if not salary_str or str(salary_str) == 'Sentinel.UNSET':
        return 0
    
    # Convert to string to handle any type of input
    salary_str = str(salary_str)
    
    # Remove common characters
    clean = salary_str.lower().replace('k', '000').replace(',', '').replace('£', '').replace('$', '')
    
    try:
        return int(clean)
    except ValueError:
        return 0

@click.command()
@click.argument('job_id')
@click.option('--quick', is_flag=True, help='Skip confirmation prompts')
def apply_job(job_id, quick):
    """
    🚀 Quick apply to a job (used from notifications)
    """
    
    try:
        job = api.get_job_details(job_id)
        
        if not job:
            show_error(f"Job {job_id} not found")
            return
        
        console.print(f"\n[bold bright_yellow]🚀 Quick Apply:[/bold bright_yellow] {job['title']} at {job.get('company', 'Unknown')}")
        
        if not quick:
            try:
                if not Confirm.ask("Continue with application?"):
                    console.print("❌ Application cancelled")
                    return
            except (EOFError, KeyboardInterrupt):
                # Non-interactive context - proceed automatically
                console.print("🚀 Proceeding with application (non-interactive mode)")
                pass
        
        # Use existing apply function
        apply_to_job(job, quick=True)
        
        # Record action for analytics
        from ..core.saved_searches import SavedSearchManager
        manager = SavedSearchManager()
        manager.record_user_action(job_id, "applied")
        
    except Exception as e:
        show_error(f"Failed to apply: {str(e)}")

@click.command()
@click.argument('job_id')
@click.option('--reason', help='Dismissal reason for analytics')
def dismiss_job(job_id, reason):
    """
    👎 Dismiss a job notification (mark as not interested)
    """
    
    try:
        # Record dismissal action
        from ..core.saved_searches import SavedSearchManager
        manager = SavedSearchManager()
        manager.record_user_action(job_id, f"dismissed:{reason or 'not_interested'}")
        
        show_success(f"📝 Job {job_id} marked as not interested")
        console.print("💡 This helps improve your future notifications")
        
    except Exception as e:
        show_error(f"Failed to dismiss: {str(e)}")

# Commands are registered in cli.py
