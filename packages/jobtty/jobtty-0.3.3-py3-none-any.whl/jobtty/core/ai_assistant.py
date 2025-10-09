"""
AI Code Assistant for Jobtty Terminal
Powered by Grok AI for real contextual help
"""

import os
import json
import subprocess
import requests
from typing import List, Dict, Optional, Any
from datetime import datetime
from pathlib import Path
import ast
import re

class JobttyAI:
    """AI assistant powered by Grok API"""
    
    def __init__(self):
        self.context_history = []
        self.current_challenge = None
        self.workspace_path = None
        self.api_key = os.getenv('GROK_API_KEY') or os.getenv('GROQ_API_KEY') or os.getenv('XAI_API_KEY')
        # Use Groq API if key starts with "gsk_"
        if self.api_key and self.api_key.startswith('gsk_'):
            self.base_url = "https://api.groq.com/openai/v1"
            self.is_groq = True
        else:
            self.base_url = "https://api.x.ai/v1"
            self.is_groq = False
        
    def _call_grok_api(self, messages: List[Dict], max_tokens: int = 1000) -> Optional[str]:
        """Make API call to Grok"""
        if not self.api_key:
            return None
            
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.3-70b-versatile" if self.is_groq else "grok-2-1212",
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": 0.7
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                error_details = ""
                try:
                    error_details = f" - {response.json().get('error', {}).get('message', '')}"
                except:
                    pass
                return f"API Error: {response.status_code}{error_details}"
                
        except Exception as e:
            return f"Connection Error: {str(e)}"
    
    def set_challenge_context(self, challenge_id: str, workspace_path: str):
        """Set current challenge context for AI assistance"""
        self.current_challenge = challenge_id
        self.workspace_path = workspace_path
        
        print(f"🤖 Grok AI activated for challenge: {challenge_id}")
        print(f"💡 Type 'jobtty hint' for contextual help")
    
    def get_contextual_hint(self, error_message: str = None) -> str:
        """Get contextual help using Grok AI"""
        if not self.api_key:
            return "❌ Grok API key not configured. Set GROK_API_KEY environment variable."
        
        if error_message:
            messages = [
                {"role": "system", "content": "You are a helpful programming assistant. Provide concise solutions for coding errors."},
                {"role": "user", "content": f"Help me fix this error in my code: {error_message}"}
            ]
        else:
            messages = [
                {"role": "system", "content": "You are a helpful programming assistant for developers job hunting and coding."},
                {"role": "user", "content": "Give me a helpful coding tip or job search advice."}
            ]
        
        result = self._call_grok_api(messages, max_tokens=500)
        return result or "❌ Could not get AI assistance right now"
    
    def explain_command(self, command: str) -> str:
        """Explain a command using Grok AI"""
        if not self.api_key:
            return "❌ Grok API key not configured"
        
        messages = [
            {"role": "system", "content": "You are a helpful command-line expert. Explain commands concisely."},
            {"role": "user", "content": f"Explain what this command does and how to use it: {command}"}
        ]
        
        result = self._call_grok_api(messages, max_tokens=300)
        return result or f"❌ Could not explain command: {command}"
    
    def get_code_review(self, file_path: str) -> Dict[str, Any]:
        """Get AI code review using Grok"""
        if not self.api_key:
            return {"error": "Grok API key not configured"}
        
        try:
            with open(file_path, 'r') as f:
                code_content = f.read()
        except Exception as e:
            return {"error": f"Could not read file: {str(e)}"}
        
        file_extension = Path(file_path).suffix
        language = {".dart": "Dart/Flutter", ".rb": "Ruby/Rails", ".py": "Python"}.get(file_extension, "Unknown")
        
        messages = [
            {"role": "system", "content": f"You are an expert {language} code reviewer. Provide constructive feedback on code quality, potential issues, and suggestions for improvement. Be concise but helpful."},
            {"role": "user", "content": f"Review this {language} code:\n\n```{language.lower()}\n{code_content}\n```"}
        ]
        
        review_text = self._call_grok_api(messages, max_tokens=800)
        
        if not review_text or review_text.startswith("❌"):
            return {"error": review_text or "Could not analyze code"}
        
        # Parse the review into structured format
        return {
            "file": file_path,
            "lines_of_code": len(code_content.split('\n')),
            "language": language,
            "review": review_text,
            "score": 85  # Default score since Grok doesn't provide numeric scores
        }
    
    def suggest_next_steps(self) -> List[str]:
        """Get next step suggestions using Grok AI"""
        if not self.api_key:
            return ["❌ Grok API key not configured"]
        
        context = f"Working on: {self.current_challenge or 'general development'}"
        
        messages = [
            {"role": "system", "content": "You are a helpful development coach. Suggest 3-5 concrete next steps for a developer."},
            {"role": "user", "content": f"I'm {context}. What should I focus on next?"}
        ]
        
        suggestions = self._call_grok_api(messages, max_tokens=400)
        
        if not suggestions or suggestions.startswith("❌"):
            return ["Continue working on your current task", "Run tests", "Commit your changes"]
        
        # Split into bullet points
        return [line.strip("• -").strip() for line in suggestions.split('\n') if line.strip() and ('•' in line or '-' in line)][:5]
    
    def analyze_current_code(self) -> Dict[str, Any]:
        """Basic code analysis without AI"""
        if not self.workspace_path:
            return {"error": "No active challenge workspace"}
        
        analysis = {
            "files_analyzed": 0,
            "complexity_score": 75,  # Default
            "potential_issues": [],
            "suggestions": []
        }
        
        # Count code files
        for file_path in Path(self.workspace_path).rglob("*"):
            if file_path.suffix in ['.dart', '.rb', '.py', '.js', '.ts']:
                analysis["files_analyzed"] += 1
                
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                        analysis.update(self._analyze_file_content(content, file_path.suffix))
                except:
                    continue
        
        return analysis
    
    def _analyze_file_content(self, content: str, file_type: str) -> Dict:
        """Analyze individual file content"""
        
        issues = []
        suggestions = []
        
        lines = content.split('\n')
        total_lines = len(lines)
        
        if file_type == '.dart':
            # Flutter/Dart specific analysis
            if 'StatefulWidget' in content and 'dispose' not in content:
                issues.append("Missing dispose() method in StatefulWidget")
                suggestions.append("Add dispose() to clean up animation controllers")
            
            if 'AnimationController' in content and 'vsync' not in content:
                issues.append("AnimationController without vsync")
                suggestions.append("Add TickerProviderStateMixin for animation vsync")
            
            if total_lines > 200:
                suggestions.append("Consider breaking large widgets into smaller components")
            
            # Check for performance patterns
            if 'ListView.builder' not in content and 'ListView(' in content:
                suggestions.append("Use ListView.builder for better performance with large lists")
        
        elif file_type == '.rb':
            # Rails specific analysis
            if 'def index' in content and 'includes(' not in content:
                issues.append("Potential N+1 query in index action")
                suggestions.append("Add .includes() to eager load associations")
            
            if 'where(' in content and 'limit(' not in content:
                suggestions.append("Consider adding pagination with .limit() for large datasets")
            
            if total_lines > 100 and 'private' not in content:
                suggestions.append("Add private methods to improve code organization")
            
            # Check for Rails best practices
            if '@' in content and 'controller' in self.workspace_path.lower():
                instance_vars = re.findall(r'@\w+', content)
                if len(instance_vars) > 3:
                    suggestions.append("Consider using service objects for complex controller logic")
        
        return {
            "potential_issues": issues,
            "suggestions": suggestions,
            "complexity_score": min(total_lines // 10, 100)
        }
    
    def get_contextual_hint(self, error_message: str = None) -> str:
        """Get contextual help using Grok AI"""
        if not self.api_key:
            return "❌ Grok API key not configured. Set GROK_API_KEY environment variable."
        
        if error_message:
            messages = [
                {"role": "system", "content": "You are a helpful programming assistant. Provide concise solutions for coding errors."},
                {"role": "user", "content": f"Help me fix this error in my code: {error_message}"}
            ]
        else:
            messages = [
                {"role": "system", "content": "You are a helpful programming assistant for developers job hunting and coding."},
                {"role": "user", "content": "Give me a helpful coding tip or job search advice."}
            ]
        
        result = self._call_grok_api(messages, max_tokens=500)
        return result or "❌ Could not get AI assistance right now"
    
    def _get_error_hint(self, error_message: str) -> str:
        """Get hint for specific error message"""
        
        error_lower = error_message.lower()
        
        if "modulenotfounderror" in error_lower:
            return "📦 Module missing - check your dependencies and imports"
        elif "syntaxerror" in error_lower:
            return "🔧 Syntax error - check brackets, quotes, and indentation"
        elif "attributeerror" in error_lower:
            return "🎯 Attribute error - verify object methods and properties"
        elif "nosuchmethod" in error_lower:
            return "🔍 Method not found - check spelling and class inheritance"
        elif "compilation failed" in error_lower:
            return "⚡ Compilation failed - check syntax and type errors"
        else:
            return f"❌ Error detected: {error_message[:100]}..."
    
    def _get_flutter_hints(self, analysis: Dict) -> List[str]:
        """Flutter-specific hints"""
        hints = []
        
        if analysis["files_analyzed"] < 5:
            hints.append("🏗️ Consider organizing code into separate widgets and models")
        
        if analysis["complexity_score"] > 50:
            hints.append("🎯 Break complex widgets into smaller, reusable components")
        
        hints.extend([
            "💡 Flutter Pro Tips:",
            "  • Use const constructors for performance",
            "  • Implement proper disposal for animation controllers", 
            "  • Add widget tests for custom animations",
            "  • Use ListView.builder for large lists"
        ])
        
        return hints
    
    def _get_rails_hints(self, analysis: Dict) -> List[str]:
        """Rails-specific hints"""
        hints = []
        
        if analysis["files_analyzed"] < 6:
            hints.append("🏗️ Consider adding service objects and concerns for better architecture")
        
        hints.extend([
            "💡 Rails Performance Tips:",
            "  • Use .includes() to avoid N+1 queries",
            "  • Add database indexes for frequently queried fields",
            "  • Implement caching for expensive operations",
            "  • Use background jobs for slow tasks"
        ])
        
        return hints
    
    def suggest_next_steps(self) -> List[str]:
        """Suggest next steps based on current progress"""
        
        analysis = self.analyze_current_code()
        steps = []
        
        if analysis["files_analyzed"] == 0:
            steps.append("1. 📝 Create your main implementation file")
            steps.append("2. 🏗️ Set up basic project structure")
            steps.append("3. 🧪 Write initial tests")
        
        elif analysis["files_analyzed"] < 3:
            steps.append("1. 🎯 Implement core functionality")
            steps.append("2. 🧪 Add comprehensive tests")
            steps.append("3. 📊 Add performance monitoring")
        
        else:
            steps.append("1. 🔧 Refactor and optimize existing code")
            steps.append("2. 🧪 Increase test coverage")
            steps.append("3. 📝 Add documentation and comments")
            steps.append("4. 🚀 Final testing and submission")
        
        return steps
    
    
