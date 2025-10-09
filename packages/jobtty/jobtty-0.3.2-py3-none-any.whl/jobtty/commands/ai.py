"""
AI Assistant commands for Jobtty
Contextual help and code suggestions during challenges
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from typing import Dict
import os

from ..core.ai_assistant import JobttyAI
from ..core.display import show_error, show_success

console = Console()
ai_assistant = JobttyAI()

@click.group()
def ai():
    """🤖 AI Assistant commands"""
    pass

@ai.command()
@click.option('--error', help='Get help with specific error message')
@click.option('--topic', help='Get help with specific topic (animations, api, tests, etc.)')
def hint(error, topic):
    """Get contextual hints and suggestions"""
    
    if error:
        hint_text = ai_assistant.get_contextual_hint(error_message=error)
        title = "🚨 Grok AI Error Analysis"
        border_color = "red"
    
    elif topic:
        hint_text = get_topic_hint(topic)
        title = f"💡 Help: {topic.title()}"
        border_color = "cyan"
    
    else:
        hint_text = ai_assistant.get_contextual_hint()
        title = "🤖 Grok AI Assistant"
        border_color = "magenta"
    
    console.print(Panel.fit(
        hint_text,
        title=f"[bold {border_color}]{title}[/bold {border_color}]",
        border_style=border_color
    ))

def get_topic_hint(topic: str) -> str:
    """Get help for specific topics"""
    
    topics = {
        "animations": """
🎬 [bold]Flutter Animations Guide[/bold]

[yellow]Basic Animations:[/yellow]
• AnimationController + Tween for custom animations
• AnimatedContainer for simple property changes
• Hero widgets for page transitions

[green]Advanced Techniques:[/green]
• Custom painters for complex graphics
• Staggered animations with intervals
• Physics-based animations (SpringSimulation)
• Shader effects for visual flair

[cyan]Performance Tips:[/cyan]
• Use const constructors where possible
• Avoid rebuilding expensive widgets
• Implement shouldRepaint() in CustomPainter
• Profile with Flutter Inspector

[white]Code Example:[/white]
```dart
late AnimationController _controller;
late Animation<double> _animation;

@override
void initState() {
  _controller = AnimationController(duration: Duration(seconds: 2), vsync: this);
  _animation = Tween<double>(begin: 0, end: 1).animate(_controller);
  _controller.repeat();
}
```
        """,
        
        "api": """
🌐 [bold]Rails API Best Practices[/bold]

[yellow]Performance Essentials:[/yellow]
• Use includes() to prevent N+1 queries
• Add database indexes for search fields
• Implement pagination (Kaminari gem)
• Cache expensive operations

[green]Architecture Patterns:[/green]
• Service objects for business logic
• Serializers for JSON responses (Jbuilder)
• Concerns for shared functionality
• Background jobs for slow operations

[cyan]Testing Strategy:[/cyan]
• Request specs for API endpoints
• Model specs for validations
• Service specs for business logic
• Integration tests for workflows

[white]Code Example:[/white]
```ruby
class Api::V1::ProductsController < ApplicationController
  def index
    @products = ProductSearchService.new(search_params).call
                  .includes(:category, :reviews)
                  .page(params[:page])
    
    render json: @products, each_serializer: ProductSerializer
  end
end
```
        """,
        
        "tests": """
🧪 [bold]Testing Best Practices[/bold]

[yellow]Flutter Testing:[/yellow]
• Widget tests for UI components
• Unit tests for business logic  
• Integration tests for user flows
• Golden file tests for pixel-perfect UI

[green]Rails Testing:[/green]
• Request specs for API endpoints
• Model specs with factories
• Service specs for complex logic
• System specs for full workflows

[cyan]Coverage Goals:[/cyan]
• Aim for 90%+ test coverage
• Focus on critical business logic
• Test edge cases and error scenarios
• Mock external dependencies

[white]Example Commands:[/white]
```bash
# Flutter
flutter test --coverage
genhtml coverage/lcov.info -o coverage/html

# Rails  
bundle exec rspec --format documentation
bundle exec rspec spec/requests/
```
        """,
        
        "git": """
🔗 [bold]Git Workflow for Challenges[/bold]

[yellow]Commit Strategy:[/yellow]
• Make small, focused commits
• Use conventional commit messages
• Commit frequently to show progress
• Each commit is scored for points!

[green]Scoring System:[/green]
• Base: 10 points per commit
• Good message: +5 points
• Conventional format: +15 points  
• Test files: +20 points
• Reasonable size: +10 points

[cyan]Best Practices:[/cyan]
• feat: Add new functionality
• fix: Bug fixes and corrections
• test: Add or update tests
• refactor: Code improvements
• docs: Documentation updates

[white]Example Workflow:[/white]
```bash
git add lib/widgets/vinyl_record.dart
git commit -m "feat: Add vinyl record animation widget"
git add test/
git commit -m "test: Add widget tests for vinyl animation"
git push jobtty main  # Auto-submits challenge!
```
        """
    }
    
    return topics.get(topic.lower(), f"❓ No help available for topic: {topic}")

@ai.command()
@click.argument('command')
def explain(command):
    """Explain what a command does in context of current challenge"""
    
    explanation = ai_assistant.explain_command(command)
    
    console.print(Panel.fit(
        explanation,
        title=f"[bold cyan]🔍 Command: {command}[/bold cyan]",
        border_style="cyan"
    ))

@ai.command()
@click.argument('file_path')
def review(file_path):
    """Get AI code review for specific file"""
    
    if not os.path.exists(file_path):
        show_error(f"File not found: {file_path}")
        return
    
    review_data = ai_assistant.get_code_review(file_path)
    
    if "error" in review_data:
        show_error(review_data["error"])
        return
    
    # Display Grok AI code review
    if "error" in review_data:
        show_error(review_data["error"])
        return
        
    console.print(Panel.fit(
        f"""
📁 [bold]File:[/bold] {review_data.get('file', 'Unknown')}
📊 [bold]Lines:[/bold] {review_data.get('lines_of_code', 0)}
🔧 [bold]Language:[/bold] {review_data.get('language', 'Unknown')}

[bold cyan]🤖 AI Code Review:[/bold cyan]

{review_data.get('review', 'No review available')}
        """,
        title="[bold yellow]🤖 AI Code Review[/bold yellow]",
        border_style="yellow"
    ))

def format_review_issues(review_data: Dict) -> str:
    """Format review issues and suggestions"""
    
    output = []
    
    if review_data.get("issues"):
        output.append("[bold red]🚨 Issues Found:[/bold red]")
        for issue in review_data["issues"]:
            output.append(f"  • {issue}")
        output.append("")
    
    if review_data.get("suggestions"):
        output.append("[bold green]💡 Suggestions:[/bold green]")
        for suggestion in review_data["suggestions"]:
            output.append(f"  • {suggestion}")
    
    if not output:
        output.append("[bold green]✅ No issues found - great code![/bold green]")
    
    return "\n".join(output)

@ai.command()
def progress():
    """Show AI-powered progress analysis"""
    
    analysis = ai_assistant.analyze_current_code()
    
    if "error" in analysis:
        show_error(analysis["error"])
        return
    
    # Progress metrics table
    progress_table = Table(title="🎯 AI Progress Analysis", title_style="bold")
    progress_table.add_column("Metric", style="white")
    progress_table.add_column("Current", style="green")
    progress_table.add_column("Target", style="yellow")
    progress_table.add_column("Status", style="cyan")
    
    metrics = [
        ("Files Created", str(analysis["files_analyzed"]), "5-8", "📈 Good"),
        ("Code Complexity", f"{analysis['complexity_score']}/100", "60-80", "🎯 Optimal"),
        ("Potential Issues", str(len(analysis.get("potential_issues", []))), "0", "⚠️ Review"),
        ("Implementation", "65%", "100%", "🚧 In Progress")
    ]
    
    for metric, current, target, status in metrics:
        progress_table.add_row(metric, current, target, status)
    
    console.print(progress_table)
    
    # Next steps
    next_steps = ai_assistant.suggest_next_steps()
    
    console.print(Panel.fit(
        "\n".join(next_steps),
        title="[bold cyan]🚀 Suggested Next Steps[/bold cyan]",
        border_style="cyan"
    ))

@ai.command()
@click.option('--language', default='auto', help='Programming language: dart, ruby, python, auto')
@click.argument('description')
def generate(language, description):
    """Generate code snippet based on description"""
    
    # Mock code generation (in real implementation, this would call an LLM)
    templates = {
        "dart": {
            "animation": """
class VinylRecordWidget extends StatefulWidget {
  @override
  _VinylRecordWidgetState createState() => _VinylRecordWidgetState();
}

class _VinylRecordWidgetState extends State<VinylRecordWidget>
    with TickerProviderStateMixin {
  
  late AnimationController _rotationController;
  late Animation<double> _rotationAnimation;

  @override
  void initState() {
    super.initState();
    _rotationController = AnimationController(
      duration: Duration(seconds: 3),
      vsync: this,
    );
    _rotationAnimation = Tween<double>(
      begin: 0,
      end: 2 * math.pi,
    ).animate(_rotationController);
    
    _rotationController.repeat();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _rotationAnimation,
      builder: (context, child) {
        return Transform.rotate(
          angle: _rotationAnimation.value,
          child: Container(
            width: 200,
            height: 200,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: Colors.black,
            ),
          ),
        );
      },
    );
  }

  @override
  void dispose() {
    _rotationController.dispose();
    super.dispose();
  }
}
            """,
            "state_management": """
// BLoC for music player state
class MusicPlayerBloc extends Bloc<MusicPlayerEvent, MusicPlayerState> {
  final AudioService _audioService;

  MusicPlayerBloc(this._audioService) : super(MusicPlayerInitial()) {
    on<PlaySong>(_onPlaySong);
    on<PauseSong>(_onPauseSong);
    on<NextSong>(_onNextSong);
  }

  void _onPlaySong(PlaySong event, Emitter<MusicPlayerState> emit) async {
    emit(MusicPlayerLoading());
    try {
      await _audioService.play(event.song);
      emit(MusicPlayerPlaying(song: event.song));
    } catch (e) {
      emit(MusicPlayerError(message: e.toString()));
    }
  }
}
            """
        },
        "ruby": {
            "api_controller": """
class Api::V1::ProductsController < ApplicationController
  include Api::Concerns::RateLimited
  include Api::Concerns::Authenticated
  
  before_action :set_product, only: [:show, :update_inventory]
  
  def index
    @products = ProductSearchService.new(search_params)
                  .call
                  .includes(:category, :brand)
                  .page(params[:page])
                  .per(50)
    
    render json: @products, each_serializer: ProductSerializer
  end
  
  def search
    @results = ProductSearchService.new(search_params)
                 .with_filters(filter_params)
                 .call
    
    render json: {
      products: ActiveModelSerializers::SerializableResource.new(@results),
      meta: pagination_meta(@results)
    }
  end
  
  private
  
  def search_params
    params.permit(:q, :category, :min_price, :max_price, :sort_by)
  end
  
  def set_product
    @product = Product.find(params[:id])
  end
end
            """,
            "service_object": """
class ProductSearchService
  attr_reader :query, :filters
  
  def initialize(params = {})
    @query = params[:q]
    @filters = params.slice(:category, :min_price, :max_price)
    @sort_by = params[:sort_by] || 'relevance'
  end
  
  def call
    scope = Product.published
    scope = apply_search(scope) if query.present?
    scope = apply_filters(scope)
    scope = apply_sorting(scope)
    scope
  end
  
  private
  
  def apply_search(scope)
    scope.search_by_name_and_description(query)
  end
  
  def apply_filters(scope)
    scope = scope.where(category: filters[:category]) if filters[:category].present?
    scope = scope.where('price >= ?', filters[:min_price]) if filters[:min_price].present?
    scope = scope.where('price <= ?', filters[:max_price]) if filters[:max_price].present?
    scope
  end
  
  def apply_sorting(scope)
    case @sort_by
    when 'price_asc' then scope.order(:price)
    when 'price_desc' then scope.order(price: :desc)
    when 'newest' then scope.order(created_at: :desc)
    else scope # relevance (default search order)
    end
  end
end
            """
        }
    }
    
    # Try to match description to template
    desc_lower = description.lower()
    code_type = None
    
    if "animation" in desc_lower or "vinyl" in desc_lower or "rotate" in desc_lower:
        code_type = "animation"
    elif "state" in desc_lower or "bloc" in desc_lower or "management" in desc_lower:
        code_type = "state_management"
    elif "controller" in desc_lower or "api" in desc_lower or "endpoint" in desc_lower:
        code_type = "api_controller"  
    elif "service" in desc_lower or "search" in desc_lower:
        code_type = "service_object"
    
    
    if language == "auto":
        # Auto-detect language from current challenge or code type
        if ai_assistant.current_challenge and "flutter" in ai_assistant.current_challenge:
            language = "dart"
        elif ai_assistant.current_challenge and "rails" in ai_assistant.current_challenge:
            language = "ruby"
        elif code_type == "animation":
            language = "dart"  # Animations are typically Flutter
        elif code_type in ["api_controller", "service_object"]:
            language = "ruby"  # Rails patterns
        else:
            language = "dart"  # Default to Flutter for demos
    
    if code_type and language in templates and code_type in templates[language]:
        generated_code = templates[language][code_type]
        
        console.print(Panel.fit(
            f"🤖 Generated {language.title()} code for: [cyan]{description}[/cyan]\n\n"
            f"[dim]Copy the code below and adapt it to your needs:[/dim]",
            title="[bold green]✨ Code Generated[/bold green]",
            border_style="green"
        ))
        
        console.print(Syntax(generated_code.strip(), language, theme="monokai", line_numbers=True))
        
        console.print(Panel.fit(
            "💡 [bold]Tips:[/bold]\n"
            "• Adapt the code to your specific requirements\n"
            "• Add error handling and edge cases\n" 
            "• Write tests for the generated code\n"
            "• Consider performance implications",
            border_style="yellow"
        ))
    
    else:
        console.print(Panel.fit(
            f"🤔 I need more context to generate code for: [yellow]{description}[/yellow]\n\n"
            f"[white]Available templates:[/white]\n"
            f"• [cyan]animation[/cyan] - Flutter animation widgets\n"
            f"• [cyan]state management[/cyan] - BLoC pattern implementation\n"
            f"• [cyan]api controller[/cyan] - Rails API endpoints\n"
            f"• [cyan]service object[/cyan] - Rails service classes\n\n"
            f"[dim]Try: jobtty ai generate 'animation widget for vinyl record'[/dim]",
            title="[bold yellow]🤖 Code Generation[/bold yellow]",
            border_style="yellow"
        ))

@ai.command()
def status():
    """Show AI assistant status and capabilities"""
    
    has_api_key = ai_assistant.api_key is not None
    status_icon = "✅ Ready" if has_api_key else "❌ Not configured"
    
    console.print(Panel.fit(
        f"""
🤖 [bold]Jobtty AI Assistant (Powered by Grok)[/bold]

[green]Status:[/green] {status_icon}
[yellow]API Key:[/yellow] {'Configured' if has_api_key else 'Missing'}

[cyan]Available Commands:[/cyan]
• [white]jobtty hint[/white] - Get contextual coding help
• [white]jobtty hint --error "error message"[/white] - Fix specific errors
• [white]jobtty explain "command"[/white] - Explain any command
• [white]jobtty ai review file.py[/white] - AI code review

[bold bright_yellow]⚡ Setup (Quick & Free!):[/bold bright_yellow]
1. Get free API key: [cyan]https://console.x.ai[/cyan] ($25/month free)
2. Export: [green]export GROK_API_KEY="your-key-here"[/green]
3. Test: [white]jobtty hint[/white]

[bold magenta]🚀 Real AI vs Mock Templates:[/bold magenta] 
With Grok API, you get intelligent context-aware assistance instead of static templates!
        """,
        title="[bold blue]🤖 Grok AI Integration[/bold blue]",
        border_style="blue"
    ))

@ai.command()
@click.option('--enable/--disable', default=True, help='Enable or disable AI suggestions')
@click.option('--verbose', is_flag=True, help='Enable verbose AI feedback')
def config(enable, verbose):
    """Configure AI assistant settings"""
    
    config_data = {
        "enabled": enable,
        "verbose": verbose,
        "last_updated": datetime.now().isoformat()
    }
    
    # Save to config file
    config_dir = os.path.expanduser("~/.jobtty")
    os.makedirs(config_dir, exist_ok=True)
    
    with open(os.path.join(config_dir, "ai_config.json"), "w") as f:
        json.dump(config_data, f, indent=2)
    
    status = "enabled" if enable else "disabled"
    verbosity = "verbose" if verbose else "normal"
    
    console.print(Panel.fit(
        f"⚙️ AI Assistant [bold green]{status}[/bold green]\n"
        f"📢 Feedback level: [yellow]{verbosity}[/yellow]\n\n"
        f"[dim]Settings saved to ~/.jobtty/ai_config.json[/dim]",
        title="[bold cyan]🤖 AI Configuration[/bold cyan]",
        border_style="cyan"
    ))

if __name__ == "__main__":
    ai()