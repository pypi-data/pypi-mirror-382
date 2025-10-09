"""
Cleanup commands for JobTTY CLI
Remove duplicates, optimize storage, and maintain data integrity
"""

import click
import json
from pathlib import Path
from typing import List, Dict, Set
from datetime import datetime
from difflib import SequenceMatcher

from ..core.display import console, show_success, show_error, show_info
from ..core.saved_searches import SavedSearchManager
from ..models.saved_search import SavedSearch


def similarity(a: str, b: str) -> float:
    """Calculate similarity between two strings (0.0 to 1.0)"""
    return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()


def find_duplicate_groups(searches: List[SavedSearch], threshold: float = 0.8) -> List[List[SavedSearch]]:
    """Group searches that are similar enough to be considered duplicates"""
    
    duplicate_groups = []
    processed_ids = set()
    
    for i, search in enumerate(searches):
        if search.id in processed_ids:
            continue
            
        # Find all searches similar to this one
        similar_searches = [search]
        processed_ids.add(search.id)
        
        for j, other_search in enumerate(searches[i+1:], i+1):
            if other_search.id in processed_ids:
                continue
                
            # Check query similarity
            query_sim = similarity(search.query, other_search.query)
            
            # Check location similarity (if both have locations)
            location_sim = 1.0
            if search.location and other_search.location:
                location_sim = similarity(search.location, other_search.location)
            elif search.location != other_search.location:
                location_sim = 0.3  # Reduced penalty for different locations
            
            # Smart duplicate detection:
            # 1. Exact query matches (regardless of location)
            # 2. High query similarity with location consideration
            # 3. Query contains the other query (like "flutter developer" vs "flutter")
            
            is_duplicate = False
            
            # Case 1: Exact query match (ignoring case/whitespace)
            if search.query.lower().strip() == other_search.query.lower().strip():
                is_duplicate = True
            
            # Case 2: One query contains the other (semantic similarity)
            elif (search.query.lower().strip() in other_search.query.lower().strip() or 
                  other_search.query.lower().strip() in search.query.lower().strip()):
                # If one is subset of another, they're likely duplicates
                shorter = min(search.query, other_search.query, key=len).lower().strip()
                longer = max(search.query, other_search.query, key=len).lower().strip()
                if len(shorter) >= 3 and shorter in longer:  # Minimum 3 chars to avoid false positives
                    is_duplicate = True
            
            # Case 3: Combined similarity score
            else:
                combined_sim = (query_sim * 0.8) + (location_sim * 0.2)  # More weight on query
                if combined_sim >= threshold:
                    is_duplicate = True
            
            if is_duplicate:
                similar_searches.append(other_search)
                processed_ids.add(other_search.id)
        
        # Only add to groups if there are duplicates
        if len(similar_searches) > 1:
            duplicate_groups.append(similar_searches)
    
    return duplicate_groups


def choose_best_search(duplicate_group: List[SavedSearch]) -> SavedSearch:
    """Choose the best search from a group of duplicates"""
    
    # Scoring criteria:
    # 1. Most total matches (indicates it's working well)
    # 2. Most recent activity (last_checked)
    # 3. Has notifications enabled
    # 4. More specific criteria (salary, skills, etc.)
    
    best_search = duplicate_group[0]
    best_score = 0
    
    for search in duplicate_group:
        score = 0
        
        # Activity score (0-40 points)
        score += min(search.total_matches * 2, 40)
        
        # Recency score (0-20 points)
        if search.last_checked:
            try:
                last_check = datetime.fromisoformat(search.last_checked)
                hours_ago = (datetime.now() - last_check).total_seconds() / 3600
                if hours_ago < 24:
                    score += 20
                elif hours_ago < 168:  # 1 week
                    score += 10
            except:
                pass
        
        # Notifications enabled (10 points)
        if search.notifications_enabled:
            score += 10
        
        # Specificity bonus (0-20 points)
        specificity = 0
        if search.min_salary:
            specificity += 5
        if search.location:
            specificity += 5
        if search.skills:
            specificity += 5
        if search.keywords_required:
            specificity += 5
        score += specificity
        
        # Quality bonus (0-10 points)
        if search.name and search.name != f"Search for {search.query}":
            score += 5  # Custom name indicates user cares about this search
        
        if len(search.query.split()) > 1:
            score += 5  # Multi-word queries are usually more specific
        
        if score > best_score:
            best_score = score
            best_search = search
    
    return best_search


@click.command()
@click.option('--dry-run', is_flag=True, help='Show what would be cleaned without making changes')
@click.option('--threshold', type=float, default=0.7, help='Similarity threshold for duplicates (0.0-1.0)')
@click.option('--backup', is_flag=True, default=True, help='Create backup before cleanup')
def cleanup_searches(dry_run, threshold, backup):
    """
    🧹 Clean up duplicate saved searches
    
    Removes duplicate saved searches based on query similarity,
    keeping the most active and recent ones.
    
    Examples:
    jobtty cleanup-searches                    # Clean with defaults
    jobtty cleanup-searches --dry-run         # Preview changes
    jobtty cleanup-searches --threshold 0.9   # Stricter matching
    """
    
    console.print(f"\n[bold bright_cyan]🧹 JobTTY Search Cleanup[/bold bright_cyan]\n")
    
    manager = SavedSearchManager()
    
    # Load all searches
    all_searches = manager.load_all_searches()
    
    if not all_searches:
        show_info("No saved searches found to clean up")
        return
    
    console.print(f"📊 Found {len(all_searches)} saved searches")
    
    # Create backup if requested
    if backup and not dry_run:
        backup_file = manager.config_dir / f"saved_searches_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            import shutil
            shutil.copy2(manager.searches_file, backup_file)
            console.print(f"💾 Backup created: {backup_file.name}")
        except Exception as e:
            show_error(f"Failed to create backup: {e}")
            return
    
    # Find duplicate groups
    duplicate_groups = find_duplicate_groups(all_searches, threshold)
    
    if not duplicate_groups:
        show_success("✅ No duplicates found! Your searches are already optimized.")
        return
    
    console.print(f"\n🔍 Found {len(duplicate_groups)} groups of duplicate searches:")
    
    searches_to_keep = []
    searches_to_remove = []
    
    # Process each duplicate group
    for i, group in enumerate(duplicate_groups, 1):
        console.print(f"\n[bold yellow]Group {i}:[/bold yellow] {len(group)} similar searches")
        
        # Show all searches in the group
        for search in group:
            activity_indicator = "🔥" if search.total_matches > 5 else "💤" if search.total_matches == 0 else "📊"
            notifications = "🔔" if search.notifications_enabled else "🔕"
            
            console.print(f"  {activity_indicator} {notifications} [cyan]{search.query}[/cyan]")
            console.print(f"    └─ ID: {search.id}, Matches: {search.total_matches}, Location: {search.location or 'Any'}")
        
        # Choose the best one
        best_search = choose_best_search(group)
        searches_to_keep.append(best_search)
        
        for search in group:
            if search.id != best_search.id:
                searches_to_remove.append(search)
        
        console.print(f"  ✅ [bold green]Keeping:[/bold green] [cyan]{best_search.query}[/cyan] (ID: {best_search.id})")
        console.print(f"  🗑️  [dim]Removing {len(group) - 1} duplicates[/dim]")
    
    # Also keep all non-duplicate searches
    all_duplicate_ids = {search.id for group in duplicate_groups for search in group}
    unique_searches = [search for search in all_searches if search.id not in all_duplicate_ids]
    searches_to_keep.extend(unique_searches)
    
    # Show summary
    console.print(f"\n[bold bright_yellow]📋 Cleanup Summary:[/bold bright_yellow]")
    console.print(f"  • Original searches: {len(all_searches)}")
    console.print(f"  • After cleanup: {len(searches_to_keep)}")
    console.print(f"  • Searches removed: {len(searches_to_remove)}")
    console.print(f"  • Space saved: ~{len(searches_to_remove) * 600} bytes")
    
    if dry_run:
        console.print(f"\n[bold bright_blue]🔍 DRY RUN - No changes made[/bold bright_blue]")
        console.print("Remove --dry-run flag to apply these changes")
        return
    
    # Apply the cleanup
    try:
        manager._save_searches_to_file(searches_to_keep)
        show_success(f"✅ Cleanup completed! Removed {len(searches_to_remove)} duplicate searches.")
        
        console.print("\n💡 [bold]Pro Tips:[/bold]")
        console.print("   • Use specific queries to avoid duplicates: 'Senior Ruby Developer London'")
        console.print("   • Set different notification frequencies for different searches")
        console.print("   • Use custom names for important searches")
        console.print("   • Run cleanup monthly: [cyan]jobtty cleanup-searches[/cyan]")
        
    except Exception as e:
        show_error(f"Failed to save cleaned searches: {e}")


@click.command()
@click.option('--days', type=int, default=30, help='Remove matches older than N days')
def cleanup_matches(days):
    """
    🧹 Clean up old job matches to save space
    
    Removes job matches older than specified days to keep
    the job matches file manageable.
    """
    
    console.print(f"\n[bold bright_cyan]🧹 JobTTY Match Cleanup[/bold bright_cyan]\n")
    
    manager = SavedSearchManager()
    
    if not manager.matches_file.exists():
        show_info("No job matches file found - nothing to clean")
        return
    
    # Get file size before cleanup
    file_size_before = manager.matches_file.stat().st_size
    
    console.print(f"📁 Match file size: {file_size_before:,} bytes")
    console.print(f"🗓️  Removing matches older than {days} days...")
    
    # Perform cleanup
    manager.cleanup_old_matches(days)
    
    # Show results
    if manager.matches_file.exists():
        file_size_after = manager.matches_file.stat().st_size
        space_saved = file_size_before - file_size_after
        
        if space_saved > 0:
            show_success(f"✅ Cleanup completed!")
            console.print(f"💾 Space saved: {space_saved:,} bytes ({space_saved/1024:.1f} KB)")
            console.print(f"📊 New file size: {file_size_after:,} bytes")
        else:
            show_info("No old matches found to remove")
    else:
        show_info("Match file removed (was empty after cleanup)")


@click.command()
def cleanup_all():
    """
    🧹 Run all cleanup operations (searches + matches)
    
    Comprehensive cleanup that removes duplicate searches
    and old job matches.
    """
    
    console.print(f"\n[bold bright_cyan]🧹 JobTTY Complete Cleanup[/bold bright_cyan]\n")
    
    # Run search cleanup
    from click.testing import CliRunner
    runner = CliRunner()
    
    console.print("[bold]Step 1: Cleaning duplicate searches...[/bold]")
    result1 = runner.invoke(cleanup_searches, ['--backup'])
    
    console.print("\n[bold]Step 2: Cleaning old job matches...[/bold]")
    result2 = runner.invoke(cleanup_matches, ['--days', '30'])
    
    console.print(f"\n[bold bright_green]🎉 Complete cleanup finished![/bold bright_green]")
    console.print("Your JobTTY data is now optimized and duplicate-free!")


# Register commands in cli.py