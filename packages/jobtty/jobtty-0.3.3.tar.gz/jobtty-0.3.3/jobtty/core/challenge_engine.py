"""
Challenge execution engine for Jobtty.io
Secure, sandboxed code execution with real-time feedback
"""

import tempfile
import json
import time
import subprocess
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from ..models.challenge import Challenge, ChallengeAttempt, DifficultyLevel, ChallengeStatus, SAMPLE_CHALLENGES

# Optional Docker import
try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    docker = None
    DOCKER_AVAILABLE = False

@dataclass
class ExecutionResult:
    """Result of code execution"""
    success: bool
    output: str
    error: str = ""
    execution_time: float = 0.0
    memory_usage: int = 0
    test_results: List[Dict] = None
    score: float = 0.0

class ChallengeEngine:
    """Secure challenge execution engine"""
    
    def __init__(self):
        self.docker_available = False
        self.docker_client = None
        
        if DOCKER_AVAILABLE:
            try:
                self.docker_client = docker.from_env()
                self.docker_available = True
            except Exception as e:
                self.docker_available = False
                # Only print warning in debug mode to avoid spam
                # print("⚠️  Docker not available - using local execution")
    
    def execute_challenge(self, challenge: Challenge, code: str, user_email: str) -> ChallengeAttempt:
        """Execute a challenge attempt"""
        start_time = time.time()
        
        if challenge.challenge_type.value == "coding":
            result = self._execute_python_challenge(code, challenge.test_cases)
        elif challenge.challenge_type.value == "infrastructure":
            result = self._execute_infrastructure_challenge(code, challenge.test_cases)
        elif challenge.challenge_type.value == "ai_integration":
            result = self._execute_ai_challenge(code, challenge.test_cases)
        else:
            result = ExecutionResult(False, "", "Unsupported challenge type")
        
        execution_time = time.time() - start_time
        
        # Calculate score based on test results
        score = self._calculate_score(result, challenge.difficulty)
        
        return ChallengeAttempt(
            id=f"attempt_{int(time.time())}_{user_email.split('@')[0]}",
            challenge_id=challenge.id,
            user_email=user_email,
            code_submission=code,
            score=score,
            execution_time=execution_time,
            test_results=result.test_results or [],
            feedback=self._generate_feedback(result, score)
        )
    
    def _execute_python_challenge(self, code: str, test_cases: List[Dict]) -> ExecutionResult:
        """Execute Python coding challenge"""
        if self.docker_available:
            return self._execute_in_docker(code, test_cases, "python:3.11-slim")
        else:
            return self._execute_locally_python(code, test_cases)
    
    def _execute_in_docker(self, code: str, test_cases: List[Dict], image: str) -> ExecutionResult:
        """Execute code in Docker container for security"""
        try:
            # Create temporary file with code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                f.write("\n\n# Test execution\n")
                f.write(self._generate_test_code(test_cases))
                code_file = f.name
            
            # Run in Docker with resource limits
            container = self.docker_client.containers.run(
                image,
                f"python {code_file}",
                remove=True,
                detach=False,
                mem_limit="128m",
                cpu_quota=50000,  # 0.5 CPU
                network_disabled=True,
                timeout=30,
                volumes={code_file: {'bind': code_file, 'mode': 'ro'}}
            )
            
            output = container.decode('utf-8')
            return ExecutionResult(True, output, execution_time=time.time())
            
        except Exception as e:
            # Handle Docker errors if docker is available
            error_msg = f"Execution failed: {str(e)}"
            if DOCKER_AVAILABLE and hasattr(e, 'stderr'):
                error_msg = f"Execution failed: {e.stderr.decode()}"
            return ExecutionResult(False, "", error_msg)
    
    def _execute_locally_python(self, code: str, test_cases: List[Dict]) -> ExecutionResult:
        """Fallback local execution (development only)"""
        try:
            # Create test code
            full_code = code + "\n\n" + self._generate_test_code(test_cases)
            
            # Execute with timeout
            result = subprocess.run(
                ["python3", "-c", full_code],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return ExecutionResult(
                    True, 
                    result.stdout, 
                    execution_time=time.time(),
                    test_results=self._parse_test_results(result.stdout)
                )
            else:
                return ExecutionResult(False, result.stdout, result.stderr)
                
        except subprocess.TimeoutExpired:
            return ExecutionResult(False, "", "Code execution timeout")
        except Exception as e:
            return ExecutionResult(False, "", f"Execution error: {str(e)}")
    
    def _generate_test_code(self, test_cases: List[Dict]) -> str:
        """Generate test execution code"""
        test_code = """
# Automated test execution
import json
test_results = []

"""
        for i, test_case in enumerate(test_cases):
            test_code += f"""
try:
    # Test case {i+1}: {test_case.get('name', f'test_{i+1}')}
    test_input = {json.dumps(test_case.get('input', {}))}
    expected = {json.dumps(test_case.get('expected', ''))}
    
    # Execute test (this depends on the challenge implementation)
    actual = run_test(test_input)  # User must implement this
    
    passed = actual == expected
    test_results.append({{
        "name": "{test_case.get('name', f'test_{i+1}')}",
        "passed": passed,
        "expected": expected,
        "actual": actual
    }})
    
except Exception as e:
    test_results.append({{
        "name": "{test_case.get('name', f'test_{i+1}')}",
        "passed": False,
        "error": str(e)
    }})

"""
        
        test_code += """
print("JOBTTY_TEST_RESULTS:" + json.dumps(test_results))
"""
        return test_code
    
    def _parse_test_results(self, output: str) -> List[Dict]:
        """Parse test results from output"""
        try:
            for line in output.split('\n'):
                if line.startswith("JOBTTY_TEST_RESULTS:"):
                    return json.loads(line.replace("JOBTTY_TEST_RESULTS:", ""))
            return []
        except:
            return []
    
    def _calculate_score(self, result: ExecutionResult, difficulty: DifficultyLevel) -> float:
        """Calculate challenge score"""
        if not result.success:
            return 0.0
        
        if not result.test_results:
            return 0.5  # Partial credit for running code
        
        # Calculate test pass rate
        passed_tests = sum(1 for test in result.test_results if test.get('passed', False))
        total_tests = len(result.test_results)
        
        if total_tests == 0:
            return 0.5
        
        base_score = passed_tests / total_tests
        
        # Adjust for difficulty
        difficulty_multiplier = {
            DifficultyLevel.JUNIOR: 1.0,
            DifficultyLevel.SENIOR: 1.2,
            DifficultyLevel.STAFF: 1.5,
            DifficultyLevel.PRINCIPAL: 2.0
        }
        
        final_score = min(base_score * difficulty_multiplier[difficulty], 1.0)
        return round(final_score, 2)
    
    def _generate_feedback(self, result: ExecutionResult, score: float) -> str:
        """Generate AI-powered feedback"""
        if score >= 0.9:
            return "🏆 Excellent work! Your solution demonstrates strong technical skills."
        elif score >= 0.7:
            return "✅ Good solution! Consider edge cases and optimization opportunities."
        elif score >= 0.5:
            return "⚠️ Partial solution. Review the requirements and test your edge cases."
        else:
            return "❌ Solution needs improvement. Check syntax errors and logic flow."
    
    def _execute_infrastructure_challenge(self, code: str, test_cases: List[Dict]) -> ExecutionResult:
        """Execute Terraform/Infrastructure challenges"""
        # For MVP, simulate infrastructure validation
        if "terraform" in code.lower() and "resource" in code.lower():
            return ExecutionResult(
                True, 
                "Terraform configuration valid",
                test_results=[{"name": "syntax_check", "passed": True}]
            )
        else:
            return ExecutionResult(False, "", "Invalid Terraform syntax")
    
    def _execute_ai_challenge(self, code: str, test_cases: List[Dict]) -> ExecutionResult:
        """Execute AI/ML challenges"""
        # For MVP, validate AI integration patterns
        ai_keywords = ["openai", "anthropic", "transformers", "langchain"]
        
        if any(keyword in code.lower() for keyword in ai_keywords):
            return ExecutionResult(
                True,
                "AI integration detected",
                test_results=[{"name": "ai_usage", "passed": True}]
            )
        else:
            return ExecutionResult(False, "", "No AI integration found")

# Challenge database (MVP - JSON file storage)
class ChallengeDB:
    """Simple file-based challenge storage for MVP"""
    
    def __init__(self, data_dir: str = "~/.jobtty/challenges"):
        import os
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
    
    def get_active_challenges(self) -> List[Challenge]:
        """Get all active challenges"""
        # For MVP, return sample challenges
        return [c for c in SAMPLE_CHALLENGES if c.status == ChallengeStatus.ACTIVE]
    
    def get_challenge(self, challenge_id: str) -> Optional[Challenge]:
        """Get specific challenge"""
        for challenge in SAMPLE_CHALLENGES:
            if challenge.id == challenge_id:
                return challenge
        return None
    
    def save_attempt(self, attempt: ChallengeAttempt):
        """Save challenge attempt"""
        import os
        attempt_file = os.path.join(self.data_dir, f"attempt_{attempt.id}.json")
        
        with open(attempt_file, 'w') as f:
            json.dump({
                'id': attempt.id,
                'challenge_id': attempt.challenge_id,
                'user_email': attempt.user_email,
                'score': attempt.score,
                'completed_at': attempt.completed_at.isoformat() if attempt.completed_at else None,
                'execution_time': attempt.execution_time,
                'test_results': attempt.test_results
            }, f, indent=2)
    
    def get_user_attempts(self, user_email: str) -> List[ChallengeAttempt]:
        """Get user's challenge attempts"""
        # For MVP, return empty list
        return []