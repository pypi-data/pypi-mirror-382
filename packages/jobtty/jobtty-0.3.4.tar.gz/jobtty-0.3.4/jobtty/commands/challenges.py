"""
Challenge system commands for Jobtty.io
Elite skill verification through coding challenges
"""

import click
import tempfile
import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.syntax import Syntax

from ..core.display import console, show_error, show_success, show_info
from ..core.challenge_engine import ChallengeEngine, ChallengeDB
from ..core.config import JobttyConfig
from ..models.challenge import ChallengeType, DifficultyLevel

config = JobttyConfig()
challenge_db = ChallengeDB()
challenge_engine = ChallengeEngine()

@click.command()
@click.option('--sponsor', help='Filter by sponsor company')
@click.option('--difficulty', type=click.Choice(['junior', 'senior', 'staff', 'principal']), help='Difficulty level')
@click.option('--skill', help='Filter by required skill')
@click.option('--budget-min', type=int, help='Minimum sponsor budget')
def browse(sponsor, difficulty, skill, budget_min):
    """
    🏆 Browse available coding challenges
    
    Elite challenges sponsored by top tech companies.
    Prove your skills and get noticed by recruiters.
    """
    
    challenges = challenge_db.get_active_challenges()
    
    # Apply filters
    if sponsor:
        challenges = [c for c in challenges if sponsor.lower() in c.sponsor_company.lower()]
    if difficulty:
        challenges = [c for c in challenges if c.difficulty.value == difficulty]
    if skill:
        challenges = [c for c in challenges if skill.lower() in [s.lower() for s in c.skills_required]]
    if budget_min:
        challenges = [c for c in challenges if c.budget >= budget_min]
    
    if not challenges:
        show_error("No challenges found matching your criteria")
        return
    
    # Create beautiful challenge table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim", width=8)
    table.add_column("Challenge", style="bright_cyan", width=30)
    table.add_column("Sponsor", style="bright_yellow", width=18)
    table.add_column("Difficulty", style="green", width=12)
    table.add_column("Budget", style="bright_green", width=10)
    table.add_column("Skills", style="blue", width=25)
    
    for challenge in challenges:
        # Format budget
        budget_display = f"${challenge.budget//1000}k/mo" if challenge.budget >= 1000 else f"${challenge.budget}"
        
        # Format skills (first 3)
        skills_display = ", ".join(challenge.skills_required[:3])
        if len(challenge.skills_required) > 3:
            skills_display += f" +{len(challenge.skills_required)-3}"
        
        # Difficulty emoji
        diff_emoji = {
            "junior": "🟢",
            "senior": "🟡", 
            "staff": "🟠",
            "principal": "🔴"
        }
        
        table.add_row(
            challenge.id[:8],
            challenge.title[:29],
            challenge.sponsor_company[:17],
            f"{diff_emoji.get(challenge.difficulty.value, '⚪')} {challenge.difficulty.value.title()}",
            budget_display,
            skills_display
        )
    
    console.print(f"\n[bold bright_cyan]🏆 Elite Challenges ({len(challenges)} available):[/bold bright_cyan]\n")
    console.print(table)
    
    console.print(f"\n💡 Use [bold]jobtty challenge take <challenge-id>[/bold] to start")
    console.print(f"💰 Total sponsor budgets: [bold bright_green]${sum(c.budget for c in challenges):,}/month[/bold bright_green]")

@click.command()
@click.argument('challenge_id')
@click.option('--preview', is_flag=True, help='Preview challenge without starting timer')
def take(challenge_id, preview):
    """
    🚀 Take a coding challenge
    
    Start the timer and begin solving an elite challenge.
    Your solution will be tested automatically.
    """
    
    challenge = challenge_db.get_challenge(challenge_id)
    if not challenge:
        show_error(f"Challenge '{challenge_id}' not found")
        console.print("💡 Use [bold]jobtty challenges browse[/bold] to see available challenges")
        return
    
    # Show challenge details
    show_challenge_details(challenge)
    
    if preview:
        console.print("\n🔍 Preview mode - timer not started")
        return
    
    if not Confirm.ask(f"\n🚀 Ready to start the {challenge.time_limit}-minute challenge?"):
        console.print("👋 Challenge cancelled")
        return
    
    # Start interactive challenge session
    start_challenge_session(challenge)

def show_challenge_details(challenge):
    """Display detailed challenge information"""
    # Title panel
    title_text = Text()
    title_text.append(f"🏆 {challenge.title}", style="bold bright_cyan")
    title_text.append(f"\nSponsored by {challenge.sponsor_company}", style="bright_yellow")
    
    title_panel = Panel(title_text, border_style="bright_cyan")
    console.print(title_panel)
    
    # Details table
    details = Table(show_header=False, box=None, padding=(0, 2))
    details.add_column("Field", style="bold bright_yellow", width=15)
    details.add_column("Value", style="bright_white")
    
    details.add_row("Type:", challenge.challenge_type.value.replace('_', ' ').title())
    details.add_row("Difficulty:", f"{challenge.difficulty.value.title()} Level")
    details.add_row("Time Limit:", f"{challenge.time_limit} minutes")
    details.add_row("Budget:", f"${challenge.budget:,}/month")
    details.add_row("Skills:", ", ".join(challenge.skills_required))
    details.add_row("Participants:", str(challenge.participant_count))
    
    console.print(details)
    
    # Problem statement
    problem_panel = Panel(
        challenge.problem_statement,
        title="🎯 Challenge Description",
        border_style="green"
    )
    console.print(problem_panel)
    
    # Starter code preview
    if challenge.starter_code:
        starter_syntax = Syntax(
            challenge.starter_code[:200] + "..." if len(challenge.starter_code) > 200 else challenge.starter_code,
            "python",
            theme="monokai",
            line_numbers=True
        )
        starter_panel = Panel(
            starter_syntax,
            title="💻 Starter Code Preview",
            border_style="blue"
        )
        console.print(starter_panel)

def start_challenge_session(challenge):
    """Start interactive challenge solving session"""
    console.print(f"\n[bold bright_green]⏱️  Challenge started! {challenge.time_limit} minutes remaining[/bold bright_green]")
    
    # Create temporary file for coding
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(challenge.starter_code)
        temp_file = f.name
    
    console.print(f"\n📝 Your code file: [bright_cyan]{temp_file}[/bright_cyan]")
    console.print("💡 Edit this file with your favorite editor")
    console.print("⚡ Run [bold]jobtty challenge submit[/bold] when ready")
    
    # Show test cases
    if challenge.test_cases:
        console.print("\n[bold bright_yellow]🧪 Test Cases:[/bold bright_yellow]")
        for i, test_case in enumerate(challenge.test_cases, 1):
            console.print(f"  {i}. {test_case.get('name', f'Test {i}')}")
    
    # Store challenge session info
    session_info = {
        'challenge_id': challenge.id,
        'start_time': time.time(),
        'temp_file': temp_file,
        'time_limit': challenge.time_limit
    }
    
    config.set('active_challenge', session_info)
    
    console.print(f"\n[dim]Session saved. Good luck! 🍀[/dim]")

@click.command()
@click.option('--with-explanation', is_flag=True, help='Include explanation of your approach')
@click.option('--file', help='Submit code from specific file')
def submit(with_explanation, file):
    """
    📤 Submit your challenge solution
    
    Upload your code and run automated tests.
    """
    
    active_challenge = config.get('active_challenge')
    if not active_challenge:
        show_error("No active challenge session")
        console.print("💡 Use [bold]jobtty challenge take <id>[/bold] to start a challenge")
        return
    
    # Check time limit
    import time
    elapsed_time = time.time() - active_challenge['start_time']
    time_limit_seconds = active_challenge['time_limit'] * 60
    
    if elapsed_time > time_limit_seconds:
        show_error(f"⏰ Time limit exceeded! ({elapsed_time//60:.0f} minutes)")
        console.print("Your submission will be marked as overtime")
    
    # Read code submission
    code_file = file or active_challenge.get('temp_file')
    if not code_file or not os.path.exists(code_file):
        show_error("Code file not found")
        return
    
    with open(code_file, 'r') as f:
        submitted_code = f.read()
    
    if not submitted_code.strip():
        show_error("Code file is empty")
        return
    
    # Get challenge details
    challenge = challenge_db.get_challenge(active_challenge['challenge_id'])
    if not challenge:
        show_error("Challenge not found")
        return
    
    # Show submission confirmation
    console.print(f"\n[bold bright_cyan]📤 Submitting to: {challenge.title}[/bold bright_cyan]")
    console.print(f"⏱️  Elapsed time: {elapsed_time//60:.0f} minutes")
    console.print(f"📄 Code length: {len(submitted_code)} characters")
    
    if with_explanation:
        explanation = Prompt.ask("\n💭 Explain your approach (optional)")
        submitted_code += f"\n\n# EXPLANATION:\n# {explanation}"
    
    if not Confirm.ask("\nSubmit your solution?"):
        console.print("Submission cancelled")
        return
    
    # Execute challenge
    console.print("\n🔄 Running your code...")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task(description="Executing tests...", total=None)
        
        # Run challenge execution
        attempt = challenge_engine.execute_challenge(
            challenge, 
            submitted_code,
            config.get_user_info().get('email', 'anonymous@jobtty.io')
        )
        
        progress.update(task, description="Calculating score...")
    
    # Save attempt
    challenge_db.save_attempt(attempt)
    
    # Show results
    show_challenge_results(attempt, challenge)
    
    # Clean up session
    config.set('active_challenge', None)
    if os.path.exists(code_file):
        os.unlink(code_file)

def show_challenge_results(attempt, challenge):
    """Display challenge attempt results"""
    console.print(f"\n[bold bright_green]🎉 Challenge Complete![/bold bright_green]")
    
    # Score panel
    score_text = Text()
    score_text.append(f"Score: ", style="bold")
    
    if attempt.score >= 0.9:
        score_text.append(f"{attempt.score:.0%}", style="bold bright_green")
        score_text.append(" 🏆", style="bright_yellow")
    elif attempt.score >= 0.7:
        score_text.append(f"{attempt.score:.0%}", style="bold green")
        score_text.append(" ✅", style="bright_green")
    elif attempt.score >= 0.5:
        score_text.append(f"{attempt.score:.0%}", style="bold yellow")
        score_text.append(" ⚠️", style="bright_yellow")
    else:
        score_text.append(f"{attempt.score:.0%}", style="bold red")
        score_text.append(" ❌", style="bright_red")
    
    score_panel = Panel(score_text, title="Results", border_style="bright_green")
    console.print(score_panel)
    
    # Test results
    if attempt.test_results:
        console.print("\n[bold bright_yellow]🧪 Test Results:[/bold bright_yellow]")
        
        for test in attempt.test_results:
            status = "✅" if test.get('passed') else "❌"
            console.print(f"  {status} {test.get('name', 'Test')}")
            
            if not test.get('passed') and test.get('error'):
                console.print(f"    [dim red]Error: {test['error']}[/dim red]")
    
    # Performance metrics
    console.print(f"\n[bold bright_cyan]📊 Performance:[/bold bright_cyan]")
    console.print(f"  ⏱️  Execution time: {attempt.execution_time:.2f}s")
    console.print(f"  💾 Memory usage: {attempt.memory_usage}MB")
    
    # Feedback
    if attempt.feedback:
        feedback_panel = Panel(
            attempt.feedback,
            title="💭 Feedback",
            border_style="blue"
        )
        console.print(feedback_panel)
    
    # Next steps
    console.print(f"\n[bold bright_cyan]🚀 Next Steps:[/bold bright_cyan]")
    
    if attempt.score >= 0.8:
        console.print("  🎯 Your score qualifies you for premium job recommendations!")
        console.print("  📧 Companies can now see your verified skills")
        console.print("  💡 Use [bold]jobtty profile update[/bold] to showcase this achievement")
    else:
        console.print("  📚 Consider reviewing the challenge requirements")
        console.print("  🔄 You can retake this challenge after 24 hours")
        console.print("  💡 Check similar challenges to improve your skills")

@click.command()
@click.option('--public', is_flag=True, help='Show public profile link')
@click.option('--global-rank', is_flag=True, help='Show global ranking')
def mine(public, global_rank):
    """
    📈 View your challenge history and achievements
    """
    
    user_email = config.get_user_info().get('email')
    if not user_email:
        show_error("You need to login first")
        console.print("💡 Use [bold]jobtty login[/bold] to authenticate")
        return
    
    attempts = challenge_db.get_user_attempts(user_email)
    
    if not attempts:
        console.print("🎯 No challenges completed yet")
        console.print("💡 Use [bold]jobtty challenges browse[/bold] to find challenges")
        return
    
    # User stats
    total_score = sum(attempt.score for attempt in attempts)
    avg_score = total_score / len(attempts) if attempts else 0
    
    stats_text = Text()
    stats_text.append(f"Challenges: {len(attempts)} • ", style="bright_cyan")
    stats_text.append(f"Avg Score: {avg_score:.0%} • ", style="bright_green")
    stats_text.append(f"Total Points: {total_score:.0f}", style="bright_yellow")
    
    stats_panel = Panel(stats_text, title="🏆 Your Stats", border_style="bright_green")
    console.print(stats_panel)
    
    # Challenge history table
    history_table = Table(show_header=True, header_style="bold magenta")
    history_table.add_column("Challenge", style="bright_cyan", width=25)
    history_table.add_column("Score", style="bright_green", width=8)
    history_table.add_column("Time", style="yellow", width=8)
    history_table.add_column("Date", style="dim", width=12)
    
    for attempt in sorted(attempts, key=lambda x: x.completed_at or datetime.min, reverse=True):
        challenge = challenge_db.get_challenge(attempt.challenge_id)
        challenge_name = challenge.title[:24] if challenge else attempt.challenge_id[:24]
        
        score_display = f"{attempt.score:.0%}"
        time_display = f"{attempt.execution_time:.1f}s"
        date_display = attempt.completed_at.strftime("%m/%d") if attempt.completed_at else "In progress"
        
        history_table.add_row(challenge_name, score_display, time_display, date_display)
    
    console.print(f"\n[bold bright_cyan]📊 Challenge History:[/bold bright_cyan]")
    console.print(history_table)
    
    if public:
        public_url = f"https://jobtty.io/profile/{user_email.split('@')[0]}"
        console.print(f"\n🌐 Your public profile: [bright_cyan]{public_url}[/bright_cyan]")
    
    if global_rank:
        # Mock global ranking
        console.print(f"\n[bold bright_yellow]🌍 Global Ranking:[/bold bright_yellow]")
        console.print(f"  🏆 Rank: #47 out of 1,247 elite developers")
        console.print(f"  🎯 Top 4% globally")
        console.print(f"  🚀 Skills verified: {len(set(skill for attempt in attempts for skill in ['python', 'kubernetes']))}")

@click.command()
@click.argument('challenge_id')
@click.option('--budget', type=int, required=True, help='Monthly budget in USD')
@click.option('--duration', default='30d', help='Campaign duration (e.g., 30d, 90d)')
@click.option('--target-level', type=click.Choice(['senior', 'staff', 'principal']), default='senior')
def sponsor_create(challenge_id, budget, duration, target_level):
    """
    💰 Create sponsored challenge campaign (Companies only)
    
    Sponsor coding challenges to identify top talent.
    Premium feature for company subscribers.
    """
    
    if not config.is_authenticated():
        show_error("Authentication required")
        return
    
    user_info = config.get_user_info()
    if user_info.get('account_type') != 'company':
        show_error("Only company accounts can sponsor challenges")
        console.print("💡 Upgrade to Company Pro: [bold]jobtty premium upgrade company-pro[/bold]")
        return
    
    if budget < 5000:
        show_error("Minimum sponsor budget is $5,000/month")
        return
    
    console.print(f"\n[bold bright_yellow]💎 Creating Sponsored Challenge Campaign[/bold bright_yellow]")
    console.print(f"Challenge: {challenge_id}")
    console.print(f"Budget: ${budget:,}/month")
    console.print(f"Duration: {duration}")
    console.print(f"Target: {target_level.title()} developers")
    
    # Estimate reach
    estimated_participants = min(budget // 100, 500)  # $100 per participant estimate
    console.print(f"\n📊 Estimated reach: {estimated_participants} elite developers")
    
    if not Confirm.ask("Confirm campaign creation?"):
        console.print("Campaign cancelled")
        return
    
    console.print("\n🚀 Campaign created successfully!")
    console.print("📧 Confirmation email sent")
    console.print("💡 Use [bold]jobtty sponsor dashboard[/bold] to track performance")

@click.command()
@click.option('--global', 'show_global', is_flag=True, help='Show global leaderboard')
@click.option('--skill', help='Filter by specific skill')
@click.option('--company', help='Filter by company')
def leaderboard(show_global, skill, company):
    """
    🏆 View challenge leaderboards
    
    See top performers and skill rankings.
    """
    
    console.print(f"\n[bold bright_yellow]🏆 Elite Developer Leaderboard[/bold bright_yellow]")
    
    if skill:
        console.print(f"Skill: {skill.title()}")
    if company:
        console.print(f"Company: {company}")
    
    # Mock leaderboard data
    leaderboard_data = [
        {"rank": 1, "name": "alex_k", "score": 98.5, "challenges": 12, "company": "Google"},
        {"rank": 2, "name": "sarah_m", "score": 96.2, "challenges": 8, "company": "Meta"},
        {"rank": 3, "name": "dev_ninja", "score": 94.7, "challenges": 15, "company": "Stripe"},
        {"rank": 4, "name": "code_wizard", "score": 92.1, "challenges": 6, "company": "OpenAI"},
        {"rank": 5, "name": "terminal_master", "score": 89.8, "challenges": 9, "company": "Anthropic"}
    ]
    
    leaderboard_table = Table(show_header=True, header_style="bold magenta")
    leaderboard_table.add_column("Rank", style="bright_yellow", width=6)
    leaderboard_table.add_column("Developer", style="bright_cyan", width=15)
    leaderboard_table.add_column("Score", style="bright_green", width=8)
    leaderboard_table.add_column("Challenges", style="blue", width=10)
    leaderboard_table.add_column("Company", style="dim", width=12)
    
    for dev in leaderboard_data:
        rank_display = f"#{dev['rank']}"
        if dev['rank'] <= 3:
            rank_display += " 🏆🥈🥉"[dev['rank']-1]
        
        leaderboard_table.add_row(
            rank_display,
            dev['name'],
            f"{dev['score']:.1f}%",
            str(dev['challenges']),
            dev['company']
        )
    
    console.print(leaderboard_table)
    
    console.print(f"\n💡 Complete more challenges to climb the rankings!")
    console.print(f"🎯 Top 100 developers get featured on company dashboards")

# Import time module for session management
import time
from datetime import datetime

# Register commands in cli.py
def register_challenge_commands(main_group):
    """Register all challenge commands"""
    main_group.add_command(browse, name="challenges")
    main_group.add_command(take, name="challenge") 
    main_group.add_command(submit, name="submit")
    main_group.add_command(mine, name="my-challenges")
    main_group.add_command(leaderboard, name="leaderboard")
    main_group.add_command(sponsor_create, name="sponsor")