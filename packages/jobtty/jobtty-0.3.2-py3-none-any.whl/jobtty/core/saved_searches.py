"""
Saved Search Management System
Store, manage and execute saved job searches with notifications
"""

import os
import json
import uuid
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

from ..models.saved_search import SavedSearch, JobMatch, NotificationFrequency, SearchScope
from ..core.api_client import JobttyAPI

class SavedSearchManager:
    """Manages saved searches and notifications"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".jobtty"
        self.searches_file = self.config_dir / "saved_searches.json"
        self.matches_file = self.config_dir / "job_matches.json"
        
        # Ensure config directory exists
        self.config_dir.mkdir(exist_ok=True)
        
        self.api_client = JobttyAPI()
    
    def save_search(self, search_params: Dict) -> SavedSearch:
        """Save a new search with notification preferences"""
        
        search_id = f"search_{uuid.uuid4().hex[:8]}"
        
        saved_search = SavedSearch(
            id=search_id,
            name=search_params.get("name", f"Search for {search_params['query']}"),
            query=search_params["query"],
            location=search_params.get("location"),
            remote_ok=search_params.get("remote_ok", True),
            min_salary=search_params.get("min_salary"),
            max_salary=search_params.get("max_salary"),
            skills=search_params.get("skills", []),
            experience_level=search_params.get("experience_level"),
            notifications_enabled=search_params.get("notifications", True),
            notification_frequency=NotificationFrequency(search_params.get("frequency", "instant")),
            search_scope=SearchScope(search_params.get("scope", "all")),
            keywords_required=search_params.get("keywords_required", []),
            keywords_excluded=search_params.get("keywords_excluded", []),
            exclude_companies=search_params.get("exclude_companies", [])
        )
        
        # Save to file
        searches = self.load_all_searches()
        searches.append(saved_search)
        self._save_searches_to_file(searches)
        
        print(f"💾 Search saved with ID: {search_id}")
        return saved_search
    
    def load_all_searches(self) -> List[SavedSearch]:
        """Load all saved searches from file"""
        
        if not self.searches_file.exists():
            return []
        
        try:
            with open(self.searches_file, 'r') as f:
                data = json.load(f)
                return [SavedSearch.from_dict(search_data) for search_data in data]
        except Exception as e:
            print(f"❌ Error loading saved searches: {e}")
            return []
    
    def _save_searches_to_file(self, searches: List[SavedSearch]):
        """Save searches to file"""
        
        try:
            with open(self.searches_file, 'w') as f:
                json.dump([search.to_dict() for search in searches], f, indent=2)
        except Exception as e:
            print(f"❌ Error saving searches: {e}")
    
    def delete_search(self, search_id: str) -> bool:
        """Delete a saved search"""
        
        searches = self.load_all_searches()
        original_count = len(searches)
        
        searches = [s for s in searches if s.id != search_id]
        
        if len(searches) < original_count:
            self._save_searches_to_file(searches)
            print(f"🗑️ Search {search_id} deleted")
            return True
        else:
            print(f"❌ Search {search_id} not found")
            return False
    
    def update_search(self, search_id: str, updates: Dict) -> bool:
        """Update an existing saved search"""
        
        searches = self.load_all_searches()
        
        for i, search in enumerate(searches):
            if search.id == search_id:
                # Update fields
                for key, value in updates.items():
                    if hasattr(search, key):
                        setattr(search, key, value)
                
                self._save_searches_to_file(searches)
                print(f"✅ Search {search_id} updated")
                return True
        
        print(f"❌ Search {search_id} not found")
        return False
    
    def execute_search(self, search: SavedSearch) -> List[Dict]:
        """Execute a saved search and return matching jobs"""
        
        try:
            # Build search parameters
            params = {
                "q": search.query,
                "location": search.location,
                "remote": search.remote_ok,
                "min_salary": search.min_salary,
                "max_salary": search.max_salary,
                "skills": ",".join(search.skills) if search.skills else None
            }
            
            # Execute search via API
            if search.search_scope in [SearchScope.JOBTTY, SearchScope.ALL]:
                jobs = self.api_client.search_jobs("jobtty", params)
            else:
                jobs = []
            
            # TODO: Add external API searches (Indeed, LinkedIn, etc.)
            if search.search_scope in [SearchScope.EXTERNAL, SearchScope.ALL]:
                external_jobs = self._search_external_apis(params)
                jobs.extend(external_jobs)
            
            # Filter jobs against saved search criteria
            matching_jobs = [job for job in jobs if search.matches_job(job)]
            
            # Update search metadata
            search.last_checked = datetime.now()
            search.total_matches = len(matching_jobs)
            
            return matching_jobs
            
        except Exception as e:
            print(f"❌ Error executing search: {e}")
            return []
    
    def _search_external_apis(self, params: Dict) -> List[Dict]:
        """Search external job APIs (Indeed, LinkedIn, etc.)"""
        
        # Mock external API results for demo
        external_jobs = [
            {
                "id": "ext_001",
                "title": f"Senior {params.get('q', 'Developer')}",
                "company": "TechCorp Ltd",
                "location": params.get("location", "London"),
                "description": f"Exciting {params.get('q', 'development')} role with competitive salary",
                "salary": "£75K-95K",
                "salary_min": 75000,
                "salary_max": 95000,
                "remote": True,
                "type": "External",
                "created_at": datetime.now().isoformat(),
                "source": "Indeed"
            },
            {
                "id": "ext_002", 
                "title": f"Lead {params.get('q', 'Engineer')}",
                "company": "StartupX",
                "location": "Remote",
                "description": f"Join our growing team as a {params.get('q', 'developer')}",
                "salary": "£85K-110K",
                "salary_min": 85000,
                "salary_max": 110000,
                "remote": True,
                "type": "External",
                "created_at": datetime.now().isoformat(),
                "source": "LinkedIn"
            }
        ]
        
        return external_jobs
    
    def check_all_searches(self) -> List[JobMatch]:
        """Check all saved searches for new matches"""
        
        all_matches = []
        searches = self.load_all_searches()
        
        for search in searches:
            if not search.notifications_enabled:
                continue
            
            # Execute search
            jobs = self.execute_search(search)
            
            # Check for new matches
            existing_matches = self.load_matches_for_search(search.id)
            existing_job_ids = {match.job_id for match in existing_matches}
            
            new_jobs = [job for job in jobs if job["id"] not in existing_job_ids]
            
            # Create JobMatch objects for new jobs
            for job in new_jobs:
                match_score = self._calculate_match_score(search, job)
                
                job_match = JobMatch(
                    job_id=job["id"],
                    search_id=search.id,
                    job_data=job,
                    match_score=match_score
                )
                
                all_matches.append(job_match)
            
            # Update search stats
            if new_jobs:
                search.new_matches_today += len(new_jobs)
                self._save_searches_to_file(searches)
        
        # Save new matches
        if all_matches:
            self._save_matches_to_file(all_matches)
        
        return all_matches
    
    def _calculate_match_score(self, search: SavedSearch, job: Dict) -> float:
        """Calculate how well a job matches the search criteria"""
        
        score = 0.5  # Base score
        
        # Query relevance
        job_text = f"{job.get('title', '')} {job.get('description', '')}".lower()
        query_words = search.query.lower().split()
        
        for word in query_words:
            if word in job_text:
                score += 0.1
        
        # Salary match
        if search.min_salary and job.get("salary_min"):
            if job["salary_min"] >= search.min_salary:
                score += 0.2
        
        # Location preference
        if search.location:
            job_location = job.get("location", "").lower()
            if search.location.lower() in job_location:
                score += 0.1
            elif search.remote_ok and job.get("remote"):
                score += 0.05
        
        # Skills match
        if search.skills:
            for skill in search.skills:
                if skill.lower() in job_text:
                    score += 0.05
        
        # Recency bonus
        try:
            job_time = datetime.fromisoformat(job.get("created_at", "").replace('Z', '+00:00'))
            hours_ago = (datetime.now() - job_time.replace(tzinfo=None)).total_seconds() / 3600
            
            if hours_ago < 1:
                score += 0.2  # Very recent
            elif hours_ago < 24:
                score += 0.1  # Recent
        except:
            pass
        
        return min(score, 1.0)
    
    def load_matches_for_search(self, search_id: str) -> List[JobMatch]:
        """Load existing matches for a specific search"""
        
        if not self.matches_file.exists():
            return []
        
        try:
            with open(self.matches_file, 'r') as f:
                data = json.load(f)
                return [
                    JobMatch(
                        job_id=match_data["job_id"],
                        search_id=match_data["search_id"],
                        job_data=match_data["job_data"],
                        match_score=match_data["match_score"],
                        matched_at=datetime.fromisoformat(match_data["matched_at"]),
                        notification_sent=match_data.get("notification_sent", False),
                        user_action=match_data.get("user_action")
                    )
                    for match_data in data if match_data["search_id"] == search_id
                ]
        except Exception as e:
            print(f"❌ Error loading matches: {e}")
            return []
    
    def _save_matches_to_file(self, new_matches: List[JobMatch]):
        """Append new matches to file"""
        
        existing_matches = []
        if self.matches_file.exists():
            try:
                with open(self.matches_file, 'r') as f:
                    existing_matches = json.load(f)
            except:
                existing_matches = []
        
        # Add new matches
        for match in new_matches:
            match_data = {
                "job_id": match.job_id,
                "search_id": match.search_id,
                "job_data": match.job_data,
                "match_score": match.match_score,
                "matched_at": match.matched_at.isoformat(),
                "notification_sent": match.notification_sent,
                "user_action": match.user_action
            }
            existing_matches.append(match_data)
        
        # Save updated matches
        try:
            with open(self.matches_file, 'w') as f:
                json.dump(existing_matches, f, indent=2)
        except Exception as e:
            print(f"❌ Error saving matches: {e}")
    
    def get_pending_notifications(self) -> List[JobMatch]:
        """Get job matches that need notifications"""
        
        searches = self.load_all_searches()
        pending_notifications = []
        
        for search in searches:
            if not search.should_notify_now():
                continue
            
            matches = self.load_matches_for_search(search.id)
            unsent_matches = [m for m in matches if not m.notification_sent]
            
            for match in unsent_matches:
                pending_notifications.append(match)
        
        return pending_notifications
    
    def mark_notification_sent(self, job_match: JobMatch):
        """Mark a job match notification as sent"""
        
        # Load all matches
        if not self.matches_file.exists():
            return
        
        try:
            with open(self.matches_file, 'r') as f:
                all_matches = json.load(f)
            
            # Update the specific match
            for match_data in all_matches:
                if (match_data["job_id"] == job_match.job_id and 
                    match_data["search_id"] == job_match.search_id):
                    match_data["notification_sent"] = True
                    break
            
            # Save updated data
            with open(self.matches_file, 'w') as f:
                json.dump(all_matches, f, indent=2)
                
        except Exception as e:
            print(f"❌ Error updating notification status: {e}")
    
    def record_user_action(self, job_id: str, action: str):
        """Record user action on a job notification"""
        
        if not self.matches_file.exists():
            return
        
        try:
            with open(self.matches_file, 'r') as f:
                all_matches = json.load(f)
            
            # Update matches with this job_id
            for match_data in all_matches:
                if match_data["job_id"] == job_id:
                    match_data["user_action"] = action
                    match_data["action_timestamp"] = datetime.now().isoformat()
            
            # Save updated data
            with open(self.matches_file, 'w') as f:
                json.dump(all_matches, f, indent=2)
                
            print(f"📊 Action recorded: {action} for job {job_id}")
            
        except Exception as e:
            print(f"❌ Error recording action: {e}")
    
    def get_search_statistics(self) -> Dict:
        """Get statistics across all saved searches"""
        
        searches = self.load_all_searches()
        
        if not searches:
            return {"total_searches": 0}
        
        total_matches = sum(search.total_matches for search in searches)
        active_searches = len([s for s in searches if s.notifications_enabled])
        recent_matches = 0
        
        # Count matches from last 24 hours
        cutoff = datetime.now().timestamp() - (24 * 3600)
        
        try:
            if self.matches_file.exists():
                with open(self.matches_file, 'r') as f:
                    all_matches = json.load(f)
                    
                for match_data in all_matches:
                    match_time = datetime.fromisoformat(match_data["matched_at"]).timestamp()
                    if match_time >= cutoff:
                        recent_matches += 1
        except:
            pass
        
        return {
            "total_searches": len(searches),
            "active_searches": active_searches,
            "total_matches": total_matches,
            "matches_today": recent_matches,
            "avg_matches_per_search": round(total_matches / len(searches), 1),
            "notification_frequency_breakdown": {
                freq.value: len([s for s in searches if s.notification_frequency == freq])
                for freq in NotificationFrequency
            }
        }
    
    def cleanup_old_matches(self, days_to_keep: int = 30):
        """Clean up old job matches to keep file size manageable"""
        
        if not self.matches_file.exists():
            return
        
        cutoff = datetime.now().timestamp() - (days_to_keep * 24 * 3600)
        
        try:
            with open(self.matches_file, 'r') as f:
                all_matches = json.load(f)
            
            # Keep only recent matches
            recent_matches = []
            for match_data in all_matches:
                match_time = datetime.fromisoformat(match_data["matched_at"]).timestamp()
                if match_time >= cutoff:
                    recent_matches.append(match_data)
            
            # Save cleaned data
            with open(self.matches_file, 'w') as f:
                json.dump(recent_matches, f, indent=2)
            
            removed_count = len(all_matches) - len(recent_matches)
            if removed_count > 0:
                print(f"🧹 Cleaned up {removed_count} old job matches")
                
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")

# CLI helper functions
def save_current_search(query: str, options: Dict) -> str:
    """Save current search with options"""
    
    manager = SavedSearchManager()
    
    # Build search parameters
    search_params = {
        "query": query,
        "name": options.get("name"),
        "location": options.get("location"),
        "remote_ok": options.get("remote", True),
        "min_salary": options.get("min_salary"),
        "max_salary": options.get("max_salary"),
        "skills": options.get("skills", []),
        "notifications": options.get("notify", True),
        "frequency": options.get("frequency", "instant"),
        "scope": options.get("scope", "all")
    }
    
    saved_search = manager.save_search(search_params)
    return saved_search.id

def get_all_saved_searches() -> List[SavedSearch]:
    """Get all saved searches for display"""
    manager = SavedSearchManager()
    return manager.load_all_searches()

def execute_saved_search(search_id: str) -> List[Dict]:
    """Execute a specific saved search"""
    manager = SavedSearchManager()
    searches = manager.load_all_searches()
    
    for search in searches:
        if search.id == search_id:
            return manager.execute_search(search)
    
    return []