"""
Saved Search System for Jobtty
Real-time job notifications directly in terminal
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import json
import hashlib

class NotificationFrequency(Enum):
    INSTANT = "instant"      # Immediately when new job appears
    HOURLY = "hourly"        # Every hour digest
    DAILY = "daily"          # Daily digest
    WEEKLY = "weekly"        # Weekly digest

class SearchScope(Enum):
    JOBTTY = "jobtty"        # Only JobTTY jobs
    EXTERNAL = "external"    # External APIs (Indeed, LinkedIn, etc.)
    ALL = "all"              # Both sources

@dataclass
class SavedSearch:
    """Saved search with notification preferences"""
    id: str
    name: str
    query: str
    location: Optional[str] = None
    remote_ok: bool = True
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    skills: List[str] = field(default_factory=list)
    company_size: Optional[str] = None
    experience_level: Optional[str] = None
    
    # Notification settings
    notifications_enabled: bool = True
    notification_frequency: NotificationFrequency = NotificationFrequency.INSTANT
    search_scope: SearchScope = SearchScope.ALL
    
    # Tracking
    created_at: datetime = field(default_factory=datetime.now)
    last_checked: Optional[datetime] = None
    last_notification: Optional[datetime] = None
    total_matches: int = 0
    new_matches_today: int = 0
    
    # Advanced filters
    exclude_companies: List[str] = field(default_factory=list)
    keywords_required: List[str] = field(default_factory=list)
    keywords_excluded: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage"""
        return {
            "id": self.id,
            "name": self.name,
            "query": self.query,
            "location": self.location,
            "remote_ok": self.remote_ok,
            "min_salary": self.min_salary,
            "max_salary": self.max_salary,
            "skills": self.skills,
            "company_size": self.company_size,
            "experience_level": self.experience_level,
            "notifications_enabled": self.notifications_enabled,
            "notification_frequency": self.notification_frequency.value,
            "search_scope": self.search_scope.value,
            "created_at": self.created_at.isoformat(),
            "last_checked": self.last_checked.isoformat() if self.last_checked else None,
            "last_notification": self.last_notification.isoformat() if self.last_notification else None,
            "total_matches": self.total_matches,
            "new_matches_today": self.new_matches_today,
            "exclude_companies": self.exclude_companies,
            "keywords_required": self.keywords_required,
            "keywords_excluded": self.keywords_excluded
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SavedSearch':
        """Create from dictionary"""
        search = cls(
            id=data["id"],
            name=data["name"],
            query=data["query"],
            location=data.get("location"),
            remote_ok=data.get("remote_ok", True),
            min_salary=data.get("min_salary"),
            max_salary=data.get("max_salary"),
            skills=data.get("skills", []),
            company_size=data.get("company_size"),
            experience_level=data.get("experience_level"),
            notifications_enabled=data.get("notifications_enabled", True),
            notification_frequency=NotificationFrequency(data.get("notification_frequency", "instant")),
            search_scope=SearchScope(data.get("search_scope", "all")),
            total_matches=data.get("total_matches", 0),
            new_matches_today=data.get("new_matches_today", 0),
            exclude_companies=data.get("exclude_companies", []),
            keywords_required=data.get("keywords_required", []),
            keywords_excluded=data.get("keywords_excluded", [])
        )
        
        if data.get("created_at"):
            search.created_at = datetime.fromisoformat(data["created_at"])
        if data.get("last_checked"):
            search.last_checked = datetime.fromisoformat(data["last_checked"])
        if data.get("last_notification"):
            search.last_notification = datetime.fromisoformat(data["last_notification"])
            
        return search
    
    def generate_search_hash(self) -> str:
        """Generate unique hash for search criteria"""
        search_string = f"{self.query}_{self.location}_{self.min_salary}_{self.max_salary}_{','.join(sorted(self.skills))}"
        return hashlib.md5(search_string.encode()).hexdigest()[:8]
    
    def matches_job(self, job: Dict) -> bool:
        """Check if a job matches this saved search"""
        
        # Basic query match
        if self.query and self.query.lower() not in job.get("title", "").lower() and \
           self.query.lower() not in job.get("description", "").lower():
            return False
        
        # Location filter
        if self.location and not self.remote_ok:
            job_location = job.get("location", "").lower()
            if self.location.lower() not in job_location:
                return False
        
        # Salary filter
        job_salary = job.get("salary_max") or job.get("salary_min", 0)
        if self.min_salary and job_salary < self.min_salary:
            return False
        if self.max_salary and job_salary > self.max_salary:
            return False
        
        # Required keywords
        if self.keywords_required:
            job_text = f"{job.get('title', '')} {job.get('description', '')}".lower()
            if not all(keyword.lower() in job_text for keyword in self.keywords_required):
                return False
        
        # Excluded keywords
        if self.keywords_excluded:
            job_text = f"{job.get('title', '')} {job.get('description', '')}".lower()
            if any(keyword.lower() in job_text for keyword in self.keywords_excluded):
                return False
        
        # Excluded companies
        company_data = job.get("company", "")
        if isinstance(company_data, dict):
            company_name = company_data.get("name", "").lower()
        else:
            company_name = str(company_data).lower()
        
        if any(excluded.lower() in company_name for excluded in self.exclude_companies):
            return False
        
        return True
    
    def should_notify_now(self) -> bool:
        """Check if we should send notification based on frequency"""
        
        if not self.notifications_enabled:
            return False
        
        if not self.last_notification:
            return True  # First notification
        
        time_since_last = datetime.now() - self.last_notification
        
        if self.notification_frequency == NotificationFrequency.INSTANT:
            return True
        elif self.notification_frequency == NotificationFrequency.HOURLY:
            return time_since_last >= timedelta(hours=1)
        elif self.notification_frequency == NotificationFrequency.DAILY:
            return time_since_last >= timedelta(days=1)
        elif self.notification_frequency == NotificationFrequency.WEEKLY:
            return time_since_last >= timedelta(weeks=1)
        
        return False

@dataclass
class JobMatch:
    """A job that matches a saved search"""
    job_id: str
    search_id: str
    job_data: Dict
    match_score: float
    matched_at: datetime = field(default_factory=datetime.now)
    notification_sent: bool = False
    user_action: Optional[str] = None  # viewed, applied, dismissed
    
    def to_notification_format(self) -> Dict:
        """Format for terminal notification display"""
        job = self.job_data
        company_data = job.get("company", "")
        
        if isinstance(company_data, dict):
            company_name = company_data.get("name", "Unknown Company")
        else:
            company_name = str(company_data) if company_data else "Unknown Company"
        
        return {
            "title": job.get("title", "Unknown Role"),
            "company": company_name,
            "location": job.get("location", "Not specified"),
            "salary": self._format_salary(job),
            "remote": job.get("remote", False),
            "posted_ago": self._time_ago(job.get("created_at")),
            "match_score": round(self.match_score * 100),
            "job_id": self.job_id,
            "company_logo": self._get_ascii_logo(company_name)
        }
    
    def _format_salary(self, job: Dict) -> str:
        """Format salary for display"""
        min_sal = job.get("salary_min")
        max_sal = job.get("salary_max")
        
        if min_sal and max_sal:
            return f"£{min_sal:,} - £{max_sal:,}"
        elif min_sal:
            return f"£{min_sal:,}+"
        elif max_sal:
            return f"Up to £{max_sal:,}"
        else:
            return "Competitive"
    
    def _time_ago(self, created_at: str) -> str:
        """Convert to human-readable time ago"""
        if not created_at:
            return "Unknown"
        
        try:
            job_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            diff = datetime.now() - job_time.replace(tzinfo=None)
            
            if diff.seconds < 300:  # 5 minutes
                return "Just posted!"
            elif diff.seconds < 3600:  # 1 hour
                return f"{diff.seconds // 60}m ago"
            elif diff.days == 0:
                return f"{diff.seconds // 3600}h ago"
            else:
                return f"{diff.days}d ago"
        except:
            return "Recently"
    
    def _get_ascii_logo(self, company_name: str) -> str:
        """Get ASCII art logo for company"""
        logos = {
            "google": """
   ▄▄▄▄▄▄▄▄▄▄▄
  ███████████████
  ███████████████
  ███████████████
   ▀▀▀▀▀▀▀▀▀▀▀
            """,
            "microsoft": """
  ████████████
  ████████████
  ████████████
  ████████████
            """,
            "amazon": """
   ▄▄▄▄▄▄▄▄▄▄▄
  ███████████████
  ███████████████
   ▀▀▀▀▀▀▀▀▀▀▀
            """,
            "meta": """
  ███   ███
  ████ ████
  ███████
  ███   ███
            """,
            "spotify": """
   ●●●●●●●●●
  ●●●●●●●●●●●
  ●●●●●●●●●●●
   ●●●●●●●●●
            """
        }
        
        # Simple logo selection based on company name
        for company, logo in logos.items():
            if company.lower() in company_name.lower():
                return logo.strip()
        
        # Default logo
        return """
   ████████
  ████████████
  ████████████
   ████████
        """.strip()

# Sample saved searches for demo
SAMPLE_SAVED_SEARCHES = [
    SavedSearch(
        id="search_rails_london",
        name="Senior Rails Developer - London",
        query="rails developer",
        location="London",
        remote_ok=True,
        min_salary=70000,
        max_salary=120000,
        skills=["ruby", "rails", "postgresql"],
        experience_level="senior",
        notification_frequency=NotificationFrequency.INSTANT,
        keywords_required=["senior", "rails"],
        exclude_companies=["consultancy", "outsourcing"]
    ),
    
    SavedSearch(
        id="search_flutter_remote",
        name="Flutter Developer - Remote",
        query="flutter developer",
        location=None,
        remote_ok=True,
        min_salary=60000,
        skills=["flutter", "dart", "mobile"],
        experience_level="mid-senior",
        notification_frequency=NotificationFrequency.HOURLY,
        keywords_required=["flutter"],
        keywords_excluded=["junior", "intern"]
    ),
    
    SavedSearch(
        id="search_startup_cto",
        name="CTO/Tech Lead Opportunities", 
        query="CTO OR tech lead OR engineering manager",
        location="London",
        remote_ok=True,
        min_salary=100000,
        skills=["leadership", "architecture", "scaling"],
        experience_level="principal",
        notification_frequency=NotificationFrequency.DAILY,
        keywords_required=["lead", "senior", "architecture"],
        exclude_companies=["agency"]
    )
]