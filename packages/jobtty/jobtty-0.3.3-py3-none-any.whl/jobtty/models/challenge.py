"""
Challenge system models for Jobtty.io
Elite skill verification through coding challenges
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum

class ChallengeType(Enum):
    CODING = "coding"
    INFRASTRUCTURE = "infrastructure" 
    AI_INTEGRATION = "ai_integration"
    SYSTEM_DESIGN = "system_design"
    DEBUGGING = "debugging"

class DifficultyLevel(Enum):
    JUNIOR = "junior"
    SENIOR = "senior"
    STAFF = "staff"
    PRINCIPAL = "principal"

class ChallengeStatus(Enum):
    ACTIVE = "active"
    DRAFT = "draft"
    COMPLETED = "completed"
    EXPIRED = "expired"

@dataclass
class Challenge:
    """Core challenge model"""
    id: str
    title: str
    description: str
    challenge_type: ChallengeType
    difficulty: DifficultyLevel
    sponsor_company: str
    budget: int  # Monthly sponsor budget
    skills_required: List[str]
    time_limit: int  # minutes
    status: ChallengeStatus
    created_at: datetime
    expires_at: datetime
    
    # Challenge content
    problem_statement: str
    starter_code: str = ""
    test_cases: List[Dict] = field(default_factory=list)
    expected_output: str = ""
    
    # Metadata
    participant_count: int = 0
    completion_rate: float = 0.0
    average_score: float = 0.0
    tags: List[str] = field(default_factory=list)

@dataclass 
class ChallengeAttempt:
    """User's attempt at a challenge"""
    id: str
    challenge_id: str
    user_email: str
    code_submission: str
    score: float
    completed_at: Optional[datetime] = None
    execution_time: float = 0.0
    test_results: List[Dict] = field(default_factory=list)
    feedback: str = ""
    
    # Performance metrics
    memory_usage: int = 0
    cpu_time: float = 0.0
    lines_of_code: int = 0
    
@dataclass
class SponsorCampaign:
    """Sponsor challenge campaign"""
    id: str
    company_name: str
    contact_email: str
    monthly_budget: int
    target_skills: List[str]
    challenge_ids: List[str] = field(default_factory=list)
    
    # Analytics
    total_participants: int = 0
    top_performers: List[str] = field(default_factory=list)
    hiring_conversions: int = 0
    roi_score: float = 0.0
    
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None

# Sample challenges for MVP
SAMPLE_CHALLENGES = [
    Challenge(
        id="google-k8s-scale-2024",
        title="Kubernetes Auto-Scaling Challenge",
        description="Build a smart auto-scaler for microservices that optimizes for cost and performance",
        challenge_type=ChallengeType.INFRASTRUCTURE,
        difficulty=DifficultyLevel.SENIOR,
        sponsor_company="Google Cloud",
        budget=25000,
        skills_required=["kubernetes", "terraform", "monitoring", "cost-optimization"],
        time_limit=120,
        status=ChallengeStatus.ACTIVE,
        created_at=datetime(2024, 12, 1),
        expires_at=datetime(2024, 12, 31),
        problem_statement="""
Design and implement a Kubernetes auto-scaler that:
1. Monitors application metrics (CPU, memory, custom metrics)
2. Predicts traffic patterns using historical data
3. Scales proactively to prevent performance issues
4. Optimizes for cost by right-sizing resources
5. Handles scale-to-zero for non-critical services

Your solution should handle real-world scenarios like:
- Black Friday traffic spikes
- Gradual load increases
- Memory leak detection and response
- Multi-zone scaling with availability considerations
        """,
        starter_code="""# Kubernetes Auto-Scaler
import kubernetes
from datetime import datetime, timedelta

class SmartAutoScaler:
    def __init__(self, namespace='default'):
        self.k8s_client = kubernetes.client.AppsV1Api()
        self.namespace = namespace
        
    def analyze_metrics(self, deployment_name):
        # TODO: Implement metric collection
        pass
        
    def predict_load(self, historical_data):
        # TODO: Implement traffic prediction
        pass
        
    def scale_deployment(self, deployment_name, replicas):
        # TODO: Implement scaling logic
        pass

# Your implementation here
""",
        test_cases=[
            {
                "name": "handles_traffic_spike",
                "input": {"current_cpu": 85, "prediction": "high_load"},
                "expected": "scale_up_triggered"
            },
            {
                "name": "optimizes_cost",
                "input": {"current_cpu": 20, "prediction": "low_load"},
                "expected": "scale_down_triggered"
            }
        ],
        tags=["devops", "cloud", "kubernetes", "scaling"]
    ),
    
    Challenge(
        id="openai-prompt-optimization-2024",
        title="AI Prompt Engineering Challenge",
        description="Optimize LLM prompts for maximum accuracy and minimal token usage",
        challenge_type=ChallengeType.AI_INTEGRATION,
        difficulty=DifficultyLevel.SENIOR,
        sponsor_company="OpenAI",
        budget=15000,
        skills_required=["prompt-engineering", "llm", "optimization", "python"],
        time_limit=90,
        status=ChallengeStatus.ACTIVE,
        created_at=datetime(2024, 12, 1),
        expires_at=datetime(2024, 12, 31),
        problem_statement="""
Create a prompt optimization system that:
1. Takes a base prompt and optimizes it for accuracy
2. Minimizes token usage while maintaining quality
3. Handles different LLM models (GPT-4, Claude, Gemini)
4. Provides A/B testing framework for prompts
5. Measures quality metrics automatically

Test scenarios:
- Code generation prompts
- Data extraction from unstructured text
- Creative writing with constraints
- Technical documentation generation
        """,
        starter_code="""# AI Prompt Optimizer
import openai
from typing import Dict, List

class PromptOptimizer:
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
        
    def optimize_prompt(self, base_prompt: str, target_task: str) -> str:
        # TODO: Implement prompt optimization
        pass
        
    def measure_quality(self, prompt: str, test_cases: List[Dict]) -> float:
        # TODO: Implement quality scoring
        pass
        
    def reduce_tokens(self, prompt: str) -> str:
        # TODO: Implement token reduction
        pass

# Your implementation here
""",
        test_cases=[
            {
                "name": "code_generation_accuracy",
                "target_task": "generate_react_component",
                "quality_threshold": 0.85
            },
            {
                "name": "token_efficiency",
                "max_tokens": 100,
                "min_quality": 0.80
            }
        ],
        tags=["ai", "llm", "prompt-engineering", "optimization"]
    ),
    
    Challenge(
        id="flutter-animation-mastery-2025",
        title="Flutter Animation & Performance Challenge",
        description="Build a smooth, performant mobile app with complex animations and state management",
        challenge_type=ChallengeType.CODING,
        difficulty=DifficultyLevel.SENIOR,
        sponsor_company="Spotify",
        budget=20000,
        skills_required=["flutter", "dart", "animations", "state-management", "performance"],
        time_limit=150,
        status=ChallengeStatus.ACTIVE,
        created_at=datetime(2025, 1, 1),
        expires_at=datetime(2025, 1, 31),
        problem_statement="""
Build a Flutter music player interface that demonstrates:

1. **Complex Animations**: 
   - Vinyl record spinning animation that syncs with playback
   - Waveform visualization that responds to audio in real-time
   - Smooth page transitions with hero animations
   - Pull-to-refresh with custom physics

2. **Performance Optimization**:
   - Handle playlists with 10,000+ songs without lag
   - Efficient image caching and loading
   - 60fps animations even on low-end devices
   - Memory usage under 150MB

3. **State Management**:
   - BLoC pattern implementation
   - Offline-first architecture with sync
   - Real-time updates across multiple screens
   - Background playback state persistence

4. **Testing Requirements**:
   - Widget tests for all custom animations
   - Integration tests for audio playback
   - Performance benchmarks and golden file tests

BONUS POINTS:
- Custom shader effects for visualizations
- Accessibility support (screen readers, haptic feedback)
- Cross-platform compatibility (iOS + Android)
        """,
        starter_code="""// Flutter Music Player Challenge
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

class MusicPlayerApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Jobtty Music Challenge',
      theme: ThemeData.dark(),
      home: MusicPlayerScreen(),
    );
  }
}

class MusicPlayerScreen extends StatefulWidget {
  @override
  _MusicPlayerScreenState createState() => _MusicPlayerScreenState();
}

class _MusicPlayerScreenState extends State<MusicPlayerScreen> 
    with TickerProviderStateMixin {
  
  // TODO: Implement animation controllers
  // TODO: Add audio service integration
  // TODO: Implement BLoC state management
  // TODO: Add performance optimizations
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
          // TODO: Vinyl record animation widget
          // TODO: Waveform visualization
          // TODO: Playlist with virtual scrolling
          // TODO: Custom player controls
        ],
      ),
    );
  }
}

// Your implementation here
""",
        test_cases=[
            {
                "name": "animation_performance",
                "test": "60fps during vinyl rotation",
                "points": 25
            },
            {
                "name": "memory_efficiency", 
                "test": "Under 150MB with 10k songs",
                "points": 20
            },
            {
                "name": "state_persistence",
                "test": "Playback state survives app restart",
                "points": 15
            },
            {
                "name": "accessibility_compliance",
                "test": "Full screen reader support",
                "points": 20
            },
            {
                "name": "cross_platform",
                "test": "Identical behavior iOS/Android",
                "points": 20
            }
        ],
        tags=["flutter", "dart", "mobile", "animations", "performance", "music"]
    ),
    
    Challenge(
        id="rails-api-architecture-2025", 
        title="Rails API Architecture & Scale Challenge",
        description="Design a high-performance Rails API that handles millions of requests with elegant code",
        challenge_type=ChallengeType.SYSTEM_DESIGN,
        difficulty=DifficultyLevel.STAFF,
        sponsor_company="Shopify",
        budget=30000,
        skills_required=["rails", "ruby", "postgresql", "redis", "api-design", "performance"],
        time_limit=180,
        status=ChallengeStatus.ACTIVE,
        created_at=datetime(2025, 1, 1),
        expires_at=datetime(2025, 1, 31),
        problem_statement="""
Build a Rails API for a global e-commerce platform that handles:

1. **High-Volume API Design**:
   - Product catalog with 1M+ products
   - Real-time inventory updates across warehouses
   - Search with sub-100ms response times
   - Rate limiting and authentication
   - Versioning strategy for mobile apps

2. **Performance Requirements**:
   - Handle 10,000 RPS without breaking
   - Database queries under 50ms average
   - Memory usage under 512MB per worker
   - Cache hit ratio above 85%

3. **Code Quality**:
   - Service objects and clean architecture
   - Comprehensive test coverage (90%+)
   - API documentation with examples
   - Error handling and monitoring integration

4. **Scalability Features**:
   - Background job processing (Sidekiq)
   - Multi-tenant architecture
   - Read replicas and connection pooling
   - Graceful degradation under load

BONUS POINTS:
- GraphQL implementation alongside REST
- Real-time features with ActionCable
- Advanced caching strategies (Russian Doll, fragment)
- Database sharding preparation
        """,
        starter_code="""# Rails E-commerce API Challenge
# Gemfile additions needed:
# gem 'sidekiq'
# gem 'redis'
# gem 'pg_search'
# gem 'jbuilder'

class Api::V1::ProductsController < ApplicationController
  include Api::Concerns::RateLimited
  include Api::Concerns::Authenticated
  
  # TODO: Implement high-performance product search
  def index
    # Handle millions of products efficiently
  end
  
  # TODO: Real-time inventory management
  def update_inventory
    # Update stock levels across warehouses
  end
  
  # TODO: Advanced filtering and sorting
  def search
    # Sub-100ms search with relevance scoring
  end
  
  private
  
  # TODO: Implement caching strategy
  # TODO: Add performance monitoring
  # TODO: Optimize database queries
end

# app/services/product_search_service.rb
class ProductSearchService
  # TODO: Implement elasticsearch/opensearch integration
  # TODO: Add faceted search
  # TODO: Implement relevance scoring
end

# app/models/product.rb
class Product < ApplicationRecord
  # TODO: Add performance optimizations
  # TODO: Implement caching layers
  # TODO: Add search indexing
end

# Your implementation here
""",
        test_cases=[
            {
                "name": "api_performance",
                "test": "10,000 RPS load test passes",
                "points": 30
            },
            {
                "name": "database_optimization",
                "test": "All queries under 50ms",
                "points": 25
            },
            {
                "name": "code_architecture",
                "test": "Clean service objects and concerns",
                "points": 20
            },
            {
                "name": "test_coverage",
                "test": "90%+ test coverage with realistic scenarios",
                "points": 15
            },
            {
                "name": "monitoring_integration",
                "test": "APM and error tracking configured",
                "points": 10
            }
        ],
        tags=["rails", "ruby", "api", "performance", "postgresql", "ecommerce"]
    )
]