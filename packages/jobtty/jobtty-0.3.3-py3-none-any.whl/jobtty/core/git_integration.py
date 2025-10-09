"""
Git-Native Workflow Integration for Jobtty
Automatic progress tracking through git commits
"""

import subprocess
import json
import os
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
# Optional git import
try:
    import git
    GIT_AVAILABLE = True
except ImportError:
    git = None
    GIT_AVAILABLE = False

from dataclasses import dataclass

@dataclass
class GitProgress:
    """Git-based progress tracking"""
    session_id: str
    challenge_id: str
    repo_path: str
    commits: List[Dict] = None
    branch_name: str = "main"
    total_score: int = 0
    
    def __post_init__(self):
        if self.commits is None:
            self.commits = []

class JobttyGitIntegration:
    """Handles git workflow integration for challenges"""
    
    def __init__(self, workspace_dir: str = None):
        self.workspace_dir = workspace_dir or os.path.expanduser("~/.jobtty/challenges")
        Path(self.workspace_dir).mkdir(parents=True, exist_ok=True)
        
    def create_challenge_repo(self, challenge_id: str, session_id: str, starter_code: str) -> str:
        """Create a new git repo for the challenge with starter code"""
        
        if not GIT_AVAILABLE:
            print("❌ Git challenges require 'GitPython' package")
            print("💡 Install with: pip3 install GitPython")
            print("🔧 Or use non-git challenges: jobtty challenges --list")
            return None
        
        repo_path = os.path.join(self.workspace_dir, f"{challenge_id}_{session_id}")
        
        # Create repo directory
        os.makedirs(repo_path, exist_ok=True)
        
        # Initialize git repo
        repo = git.Repo.init(repo_path)
        
        # Create starter files based on challenge type
        if "flutter" in challenge_id.lower():
            self._create_flutter_structure(repo_path, starter_code)
        elif "rails" in challenge_id.lower():
            self._create_rails_structure(repo_path, starter_code)
        else:
            # Generic structure
            with open(os.path.join(repo_path, "README.md"), "w") as f:
                f.write(f"# Jobtty Challenge: {challenge_id}\n\n")
                f.write("## Getting Started\n\n")
                f.write("Complete the challenge by implementing the required functionality.\n")
                f.write("Your progress is automatically tracked through git commits.\n")
        
        # Initial commit
        repo.git.add(".")
        repo.git.commit("-m", f"🚀 Initialize Jobtty challenge: {challenge_id}")
        
        # Add jobtty remote for submission
        try:
            repo.create_remote("jobtty", f"https://api.jobtty.io/git/{session_id}")
        except:
            pass  # Remote might already exist
        
        print(f"📁 Challenge repository created: {repo_path}")
        return repo_path
    
    def _create_flutter_structure(self, repo_path: str, starter_code: str):
        """Create Flutter project structure"""
        
        # Create pubspec.yaml
        pubspec = """
name: jobtty_flutter_challenge
description: Jobtty Flutter Challenge Submission
version: 1.0.0+1

environment:
  sdk: '>=3.0.0 <4.0.0'
  flutter: ">=3.10.0"

dependencies:
  flutter:
    sdk: flutter
  flutter_bloc: ^8.1.3
  equatable: ^2.0.5
  just_audio: ^0.9.34
  cached_network_image: ^3.2.3

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^2.0.0
  bloc_test: ^9.1.4
  integration_test:
    sdk: flutter

flutter:
  uses-material-design: true
  assets:
    - assets/images/
    - assets/audio/
"""
        
        with open(os.path.join(repo_path, "pubspec.yaml"), "w") as f:
            f.write(pubspec.strip())
        
        # Create lib structure
        lib_dir = os.path.join(repo_path, "lib")
        os.makedirs(lib_dir, exist_ok=True)
        
        # Main app file
        with open(os.path.join(lib_dir, "main.dart"), "w") as f:
            f.write(starter_code)
        
        # Create subdirectories
        for subdir in ["blocs", "models", "widgets", "services", "utils"]:
            os.makedirs(os.path.join(lib_dir, subdir), exist_ok=True)
        
        # Create test structure
        test_dir = os.path.join(repo_path, "test")
        os.makedirs(test_dir, exist_ok=True)
        
        # Basic test file
        with open(os.path.join(test_dir, "widget_test.dart"), "w") as f:
            f.write("""
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:jobtty_flutter_challenge/main.dart';

void main() {
  testWidgets('Music player smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(MusicPlayerApp());
    
    // TODO: Add your widget tests here
    // Points awarded for comprehensive test coverage
  });
}
""")
    
    def _create_rails_structure(self, repo_path: str, starter_code: str):
        """Create Rails API project structure"""
        
        # Create Gemfile
        gemfile = """
source 'https://rubygems.org'
git_source(:github) { |repo| "https://github.com/#{repo}.git" }

ruby '3.1.0'

gem 'rails', '~> 7.1.0'
gem 'pg', '~> 1.1'
gem 'puma', '~> 5.0'
gem 'bootsnap', '>= 1.4.4', require: false
gem 'rack-cors'

# Challenge-specific gems
gem 'sidekiq'
gem 'redis'
gem 'pg_search'
gem 'jbuilder'
gem 'kaminari'

group :development, :test do
  gem 'byebug', platforms: [:mri, :mingw, :x64_mingw]
  gem 'rspec-rails'
  gem 'factory_bot_rails'
  gem 'faker'
end

group :development do
  gem 'listen', '~> 3.3'
  gem 'spring'
  gem 'bullet'
  gem 'rack-mini-profiler'
end

group :test do
  gem 'database_cleaner-active_record'
  gem 'shoulda-matchers'
  gem 'webmock'
end
"""
        
        with open(os.path.join(repo_path, "Gemfile"), "w") as f:
            f.write(gemfile.strip())
        
        # Create app structure
        app_dir = os.path.join(repo_path, "app")
        for subdir in ["controllers/api/v1", "models", "services", "serializers", "jobs"]:
            os.makedirs(os.path.join(app_dir, subdir), exist_ok=True)
        
        # Create starter controller
        controller_path = os.path.join(app_dir, "controllers/api/v1/products_controller.rb")
        with open(controller_path, "w") as f:
            f.write(starter_code)
        
        # Create config structure
        config_dir = os.path.join(repo_path, "config")
        os.makedirs(config_dir, exist_ok=True)
        
        # Basic routes.rb
        with open(os.path.join(config_dir, "routes.rb"), "w") as f:
            f.write("""
Rails.application.routes.draw do
  namespace :api do
    namespace :v1 do
      resources :products do
        collection do
          get :search
          patch :update_inventory
        end
      end
    end
  end
  
  # Jobtty integration endpoints
  post '/jobtty/progress', to: 'jobtty#track_progress'
  get '/jobtty/health', to: 'jobtty#health_check'
end
""")
        
        # Create spec structure for testing
        spec_dir = os.path.join(repo_path, "spec")
        os.makedirs(os.path.join(spec_dir, "requests/api/v1"), exist_ok=True)
        
        # RSpec configuration
        with open(os.path.join(spec_dir, "rails_helper.rb"), "w") as f:
            f.write("""
require 'spec_helper'
ENV['RAILS_ENV'] ||= 'test'
require_relative '../config/environment'
abort("Rails running in production!") if Rails.env.production?
require 'rspec/rails'

# TODO: Add your API tests here
# Points awarded for comprehensive test coverage and realistic scenarios
""")
    
    def track_commit(self, repo_path: str, session_id: str) -> Dict:
        """Track a new commit and calculate score"""
        
        if not GIT_AVAILABLE:
            return {"error": "GitPython not available"}
        
        try:
            repo = git.Repo(repo_path)
            latest_commit = repo.head.commit
            
            # Calculate commit score
            score = self._calculate_commit_score(repo, latest_commit)
            
            commit_data = {
                "hash": latest_commit.hexsha[:8],
                "message": latest_commit.message.strip(),
                "author": str(latest_commit.author),
                "timestamp": datetime.fromtimestamp(latest_commit.committed_date).isoformat(),
                "files_changed": len(latest_commit.stats.files),
                "insertions": latest_commit.stats.total["insertions"],
                "deletions": latest_commit.stats.total["deletions"],
                "score": score,
                "session_id": session_id
            }
            
            print(f"📊 Commit tracked: +{score} points")
            return commit_data
            
        except Exception as e:
            print(f"❌ Error tracking commit: {e}")
            return {}
    
    def _calculate_commit_score(self, repo, commit) -> int:
        """Calculate score for a git commit"""
        score = 10  # Base score
        
        # Message quality
        message = commit.message.strip()
        if len(message) > 20:
            score += 5
        if any(word in message.lower() for word in ["test", "fix", "refactor", "optimize"]):
            score += 10
        if message.startswith(("feat:", "fix:", "test:", "refactor:")):
            score += 15  # Conventional commits
        
        # Code changes
        stats = commit.stats
        insertions = stats.total["insertions"]
        deletions = stats.total["deletions"]
        
        # Reasonable change size
        if 10 <= insertions <= 200:
            score += 10
        elif insertions > 200:
            score -= 5  # Too large commits
        
        # File diversity
        files_changed = len(stats.files)
        if files_changed <= 5:
            score += files_changed * 2
        
        # Test files bonus
        for filename in stats.files:
            if "test" in filename or "spec" in filename:
                score += 20
        
        return max(score, 0)
    
    def auto_submit_on_push(self, repo_path: str, session_id: str) -> bool:
        """Auto-submit challenge when pushed to jobtty remote"""
        
        if not GIT_AVAILABLE:
            print("❌ Git submission requires 'GitPython' package")
            return False
        
        try:
            repo = git.Repo(repo_path)
            
            # Check if pushed to jobtty remote
            for remote in repo.remotes:
                if remote.name == "jobtty":
                    # Get all commits since initial
                    commits = list(repo.iter_commits())
                    total_score = sum(self._calculate_commit_score(repo, commit) for commit in commits[:-1])
                    
                    submission_data = {
                        "session_id": session_id,
                        "total_commits": len(commits) - 1,  # Exclude initial commit
                        "total_score": total_score,
                        "final_hash": repo.head.commit.hexsha,
                        "submitted_at": datetime.now().isoformat(),
                        "repo_size": self._get_repo_size(repo_path)
                    }
                    
                    # Save submission data
                    submission_file = os.path.join(repo_path, ".jobtty_submission.json")
                    with open(submission_file, "w") as f:
                        json.dump(submission_data, f, indent=2)
                    
                    print(f"""
🎉 Challenge automatically submitted!

📊 Final Score: {total_score} points
📝 Total Commits: {len(commits) - 1}
🏆 Submission ID: {session_id}

Your solution is now being evaluated by our AI system.
Results will be available in your dashboard within 5 minutes.

🔗 View results: jobtty results {session_id}
                    """)
                    
                    return True
            
            return False
            
        except Exception as e:
            print(f"❌ Auto-submission failed: {e}")
            return False
    
    def _get_repo_size(self, repo_path: str) -> Dict:
        """Calculate repository size metrics"""
        total_files = 0
        total_lines = 0
        
        for root, dirs, files in os.walk(repo_path):
            # Skip .git directory
            if '.git' in root:
                continue
                
            for file in files:
                if file.endswith(('.dart', '.rb', '.py', '.js', '.ts')):
                    total_files += 1
                    try:
                        with open(os.path.join(root, file), 'r') as f:
                            total_lines += len(f.readlines())
                    except:
                        pass
        
        return {
            "total_files": total_files,
            "total_lines": total_lines,
            "avg_lines_per_file": total_lines // max(total_files, 1)
        }
    
    def setup_git_hooks(self, repo_path: str, session_id: str):
        """Setup git hooks for automatic progress tracking"""
        
        hooks_dir = os.path.join(repo_path, ".git", "hooks")
        
        # Post-commit hook
        post_commit_hook = f"""#!/bin/bash
# Jobtty automatic progress tracking

# Track commit in collaboration system
python3 -c "
import sys
sys.path.append('{os.path.dirname(__file__)}/../../../')
from jobtty.core.git_integration import JobttyGitIntegration

git_tracker = JobttyGitIntegration()
commit_data = git_tracker.track_commit('{repo_path}', '{session_id}')
print(f'📊 Jobtty: Commit tracked (+{{commit_data.get(\"score\", 0)}} points)')
"
"""
        
        hook_path = os.path.join(hooks_dir, "post-commit")
        with open(hook_path, "w") as f:
            f.write(post_commit_hook)
        
        # Make executable
        os.chmod(hook_path, 0o755)
        
        # Pre-push hook for auto-submission
        pre_push_hook = f"""#!/bin/bash
# Jobtty auto-submission on push to jobtty remote

remote="$1"
url="$2"

if [[ "$remote" == "jobtty" ]]; then
    echo "🚀 Pushing to Jobtty - auto-submitting challenge..."
    
    python3 -c "
import sys
sys.path.append('{os.path.dirname(__file__)}/../../../')
from jobtty.core.git_integration import JobttyGitIntegration

git_tracker = JobttyGitIntegration()
git_tracker.auto_submit_on_push('{repo_path}', '{session_id}')
"
fi
"""
        
        pre_push_path = os.path.join(hooks_dir, "pre-push")
        with open(pre_push_path, "w") as f:
            f.write(pre_push_hook)
        
        os.chmod(pre_push_path, 0o755)
        
        print("🪝 Git hooks configured for automatic tracking")
    
    def get_progress_summary(self, repo_path: str) -> Dict:
        """Get current progress summary from git history"""
        
        if not GIT_AVAILABLE:
            return {"error": "GitPython not available"}
        
        try:
            repo = git.Repo(repo_path)
            commits = list(repo.iter_commits())
            
            if not commits:
                return {"error": "No commits found"}
            
            # Calculate metrics
            total_score = 0
            file_changes = {}
            test_commits = 0
            
            for commit in commits[:-1]:  # Skip initial commit
                score = self._calculate_commit_score(repo, commit)
                total_score += score
                
                # Track file changes
                for filename in commit.stats.files:
                    file_changes[filename] = file_changes.get(filename, 0) + 1
                
                # Count test commits
                if any(word in commit.message.lower() for word in ["test", "spec"]):
                    test_commits += 1
            
            return {
                "total_commits": len(commits) - 1,
                "total_score": total_score,
                "files_modified": len(file_changes),
                "most_changed_file": max(file_changes.items(), key=lambda x: x[1])[0] if file_changes else None,
                "test_commits": test_commits,
                "test_coverage": round((test_commits / max(len(commits) - 1, 1)) * 100, 1),
                "latest_commit": {
                    "hash": commits[0].hexsha[:8],
                    "message": commits[0].message.strip(),
                    "time_ago": self._time_ago(commits[0].committed_date)
                }
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _time_ago(self, timestamp: int) -> str:
        """Convert timestamp to human-readable time ago"""
        now = datetime.now().timestamp()
        diff = now - timestamp
        
        if diff < 60:
            return f"{int(diff)}s ago"
        elif diff < 3600:
            return f"{int(diff/60)}m ago"
        else:
            return f"{int(diff/3600)}h ago"

# CLI helper functions
def init_challenge_workspace(challenge_id: str, session_id: str, starter_code: str) -> str:
    """Initialize challenge workspace with git integration"""
    if not GIT_AVAILABLE:
        print("❌ Git challenges require 'GitPython' package")
        print("💡 Install with: pip3 install GitPython")
        print("🔧 Or use standard challenges: jobtty challenges --list")
        return None
        
    git_integration = JobttyGitIntegration()
    repo_path = git_integration.create_challenge_repo(challenge_id, session_id, starter_code)
    if repo_path:
        git_integration.setup_git_hooks(repo_path, session_id)
    return repo_path

def show_git_progress(repo_path: str):
    """Show current git-based progress"""
    if not GIT_AVAILABLE:
        print("❌ Git progress requires 'GitPython' package")
        print("💡 Install with: pip3 install GitPython")
        return
        
    git_integration = JobttyGitIntegration()
    progress = git_integration.get_progress_summary(repo_path)
    
    if "error" in progress:
        print(f"❌ {progress['error']}")
        return
    
    from rich.console import Console
    from rich.panel import Panel
    
    console = Console()
    
    console.print(Panel.fit(
        f"""
📊 [bold]Git Progress Summary[/bold]

[green]✅ Commits:[/green] {progress['total_commits']}
[yellow]⭐ Score:[/yellow] {progress['total_score']} points
[blue]📁 Files Modified:[/blue] {progress['files_modified']}
[cyan]🧪 Test Coverage:[/cyan] {progress['test_coverage']}%

[white]Latest Commit:[/white]
[dim]{progress['latest_commit']['hash']}[/dim] - {progress['latest_commit']['message']}
[dim]{progress['latest_commit']['time_ago']}[/dim]

[bold cyan]🚀 Push to submit:[/bold cyan] [white]git push jobtty main[/white]
        """,
        title="[bold magenta]📈 Challenge Progress[/bold magenta]",
        border_style="magenta"
    ))