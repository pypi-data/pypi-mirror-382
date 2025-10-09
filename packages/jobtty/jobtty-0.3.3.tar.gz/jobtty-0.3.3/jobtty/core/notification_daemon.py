"""
Background Notification Daemon
Monitors saved searches and sends real-time terminal notifications
THE REVOLUTIONARY FEATURE: Job alerts while coding!
"""

import os
import sys
import time
import signal
import asyncio
import subprocess
import multiprocessing
from pathlib import Path
from datetime import datetime
from typing import List, Dict

from .saved_searches import SavedSearchManager
from .display import console
from ..models.saved_search import JobMatch, NotificationFrequency

class JobNotificationDaemon:
    """Background daemon for terminal job notifications"""
    
    def __init__(self):
        self.manager = SavedSearchManager()
        self.is_running = False
        self.jobtty_dir = Path.home() / ".jobtty"
        self.jobtty_dir.mkdir(exist_ok=True)
        self.pid_file = self.jobtty_dir / "daemon.pid"
        self.log_file = self.jobtty_dir / "daemon.log"
        
        # Ensure config directory exists
        self.pid_file.parent.mkdir(exist_ok=True)
    
    def start(self, daemonize: bool = True):
        """Start the notification daemon"""
        
        if self.is_daemon_running():
            print("🟢 Notification daemon is already running")
            return
        
        if daemonize:
            self._daemonize()
        else:
            self._run_daemon()
    
    def stop(self):
        """Stop the notification daemon"""
        
        if not self.is_daemon_running():
            print("⚪ Notification daemon is not running")
            return
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            os.kill(pid, signal.SIGTERM)
            self.pid_file.unlink()
            print("🔴 Notification daemon stopped")
            
        except (ProcessLookupError, FileNotFoundError, ValueError):
            print("⚠️  Daemon process not found - cleaning up PID file")
            if self.pid_file.exists():
                self.pid_file.unlink()
    
    def status(self):
        """Check daemon status"""
        
        if self.is_daemon_running():
            print("🟢 Notification daemon is running")
            
            # Show recent activity
            if self.log_file.exists():
                print("\n📋 Recent activity:")
                with open(self.log_file, 'r') as f:
                    lines = f.readlines()
                    for line in lines[-5:]:
                        print(f"   {line.strip()}")
        else:
            print("🔴 Notification daemon is stopped")
            print("\n💡 Start with: jobtty daemon start")
    
    def is_daemon_running(self) -> bool:
        """Check if daemon is currently running"""
        
        if not self.pid_file.exists():
            return False
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Check if process exists
            os.kill(pid, 0)
            return True
            
        except (ProcessLookupError, FileNotFoundError, ValueError):
            # Clean up stale PID file
            if self.pid_file.exists():
                self.pid_file.unlink()
            return False
    
    def _daemonize(self):
        """Run as background daemon using subprocess (cross-platform)"""
        
        import subprocess
        import sys
        import platform
        
        # Create daemon runner script
        daemon_script = self.jobtty_dir / "daemon_runner.py"
        with open(daemon_script, 'w') as f:
            # Cross-platform Python script (no shebang on Windows)
            script_content = f'''import sys
sys.path.insert(0, r"{Path(__file__).parent.parent}")
from jobtty.core.notification_daemon import JobNotificationDaemon

if __name__ == "__main__":
    daemon = JobNotificationDaemon()
    daemon._run_daemon()
'''
            f.write(script_content)
        
        # Make executable on Unix systems only
        if platform.system() != 'Windows':
            daemon_script.chmod(0o755)
        
        # Cross-platform subprocess options
        subprocess_kwargs = {
            'stdout': subprocess.DEVNULL, 
            'stderr': subprocess.DEVNULL, 
            'stdin': subprocess.DEVNULL
        }
        
        # Unix-specific: start new session
        if platform.system() != 'Windows':
            subprocess_kwargs['start_new_session'] = True
        else:
            # Windows-specific: detach from console
            subprocess_kwargs['creationflags'] = subprocess.DETACHED_PROCESS
        
        # Start daemon as completely detached subprocess
        process = subprocess.Popen([
            sys.executable, str(daemon_script)
        ], **subprocess_kwargs)
        
        # Save PID 
        with open(self.pid_file, 'w') as f:
            f.write(str(process.pid))
        print(f"🚀 Notification daemon started (PID: {process.pid})")
        
        # Process is now fully detached - parent can exit immediately
    
    def _run_daemon_process(self):
        """Daemon process entry point"""
        # Redirect stdout/stderr to log file
        with open(self.log_file, 'a') as log:
            sys.stdout = log
            sys.stderr = log
            self._run_daemon()
    
    def _run_daemon(self):
        """Main daemon event loop"""
        
        self.is_running = True
        self._log("🚀 Jobtty notification daemon started")
        
        # Set up signal handlers
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)
        
        try:
            while self.is_running:
                self._check_for_new_jobs()
                time.sleep(30)  # Check every 30 seconds
                
        except Exception as e:
            self._log(f"❌ Daemon error: {e}")
        finally:
            self._log("🔴 Notification daemon stopped")
    
    def _handle_shutdown(self, signum, frame):
        """Handle shutdown signals"""
        self.is_running = False
        self._log("📤 Received shutdown signal")
    
    def _check_for_new_jobs(self):
        """Check all saved searches for new job matches"""
        
        try:
            new_matches = self.manager.check_all_searches()
            
            if new_matches:
                self._log(f"🔍 Found {len(new_matches)} new job matches")
                
                for match in new_matches:
                    if self._should_send_notification(match):
                        self._send_terminal_notification(match)
                        self.manager.mark_notification_sent(match)
            
        except Exception as e:
            self._log(f"❌ Error checking searches: {e}")
    
    def _should_send_notification(self, match: JobMatch) -> bool:
        """Check if we should send notification for this match"""
        
        # Get the saved search
        searches = self.manager.load_all_searches()
        search = next((s for s in searches if s.id == match.search_id), None)
        
        if not search or not search.notifications_enabled:
            return False
        
        # Check notification frequency rules
        return search.should_notify_now()
    
    def _send_terminal_notification(self, match: JobMatch):
        """Send terminal notification to all active terminals"""
        
        notification_data = match.to_notification_format()
        
        # Format the terminal notification
        notification_text = self._format_notification(notification_data)
        
        # Send to all active terminal sessions
        self._broadcast_to_terminals(notification_text)
        
        self._log(f"📢 Sent notification: {notification_data['title']} at {notification_data['company']}")
    
    def _format_notification(self, job_data: Dict) -> str:
        """Format job notification for terminal display"""
        
        # Get company-specific ASCII logo
        company = job_data['company'].lower()
        match_score = job_data.get('match_score', 95)  # Default to 95%
        
        if 'knowde' in company:
            ascii_logo = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  ██   ██ ███    ██  ██████  ██     ██ ██████  ███████                        ║
║  ██  ██  ████   ██ ██    ██ ██     ██ ██   ██ ██                             ║
║  █████   ██ ██  ██ ██    ██ ██  █  ██ ██   ██ █████                          ║
║  ██  ██  ██  ██ ██ ██    ██ ██ ███ ██ ██   ██ ██                             ║
║  ██   ██ ██   ████  ██████   ███ ███  ██████  ███████                        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║            🎯 NEW JOB ALERT! ({match_score}% MATCH)                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
        elif 'netguru' in company:
            ascii_logo = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  ███    ██ ███████ ████████  ██████  ██    ██ ██████  ██    ██               ║
║  ████   ██ ██         ██    ██       ██    ██ ██   ██ ██    ██               ║
║  ██ ██  ██ █████      ██    ██   ███ ██    ██ ██████  ██    ██               ║
║  ██  ██ ██ ██         ██    ██    ██ ██    ██ ██   ██ ██    ██               ║
║  ██   ████ ███████    ██     ██████   ██████  ██   ██  ██████                ║
╠══════════════════════════════════════════════════════════════════════════════╣
║            🎯 NEW JOB ALERT! ({match_score}% MATCH)                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
        elif 'google' in company or 'alphabet' in company:
            ascii_logo = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║   ██████   ██████   ██████   ██████  ██      ███████                         ║
║  ██        ██    ██ ██    ██ ██       ██      ██                             ║
║  ██   ███  ██    ██ ██    ██ ██   ███ ██      █████                          ║
║  ██    ██  ██    ██ ██    ██ ██    ██ ██      ██                             ║
║   ██████    ██████   ██████   ██████  ███████ ███████                        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║            🎯 NEW JOB ALERT! ({match_score}% MATCH)                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
        else:
            # Default JobTTY logo for unknown companies
            ascii_logo = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  ██████╗  ██████╗ ██████╗ ████████╗████████╗██╗   ██╗    ██╗ ██████╗ ██████╗  ║
║  ██╔═══██╗██╔══██╗██╔══██╗╚══██╔══╝╚══██╔══╝╚██╗ ██╔╝    ██║██╔═══██╗██╔══██╗ ║
║  ██║   ██║██████╔╝██████╔╝   ██║      ██║    ╚████╔╝     ██║██║   ██║██████╔╝ ║
║  ██║   ██║██╔══██╗██╔══██╗   ██║      ██║     ╚██╔╝ ██   ██║██║   ██║██╔══██╗ ║
║  ╚██████╔╝██████╔╝██████╔╝   ██║      ██║      ██║  ╚█████╔╝╚██████╔╝██████╔╝ ║
║   ╚═════╝ ╚═════╝ ╚═════╝    ╚═╝      ╚═╝      ╚═╝   ╚════╝  ╚═════╝ ╚═════╝  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║            🎯 NEW JOB ALERT! ({match_score}% MATCH)                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
        
        company_logo = job_data.get("company_logo", "")
        
        notification = f"""{ascii_logo}

🏢 COMPANY: {job_data['company']}
💼 POSITION: {job_data['title']}
📍 LOCATION: {job_data['location']} {'🏠 REMOTE FRIENDLY' if job_data['remote'] else ''}
💰 SALARY: {job_data['salary']}
⏰ POSTED: {job_data['posted_ago']}

╔══════════════════════════════════════════════════════════════════════════════╗
║  🚀 LIGHTNING-FAST ACTIONS:                                                   ║
║                                                                              ║
║  📋 jobtty show {job_data['job_id']:<10} → View full job details                   ║
║  ⚡ jobtty apply {job_data['job_id']:<10} → Apply instantly!                       ║
║  👎 jobtty dismiss {job_data['job_id']:<10} → Not interested                      ║
║                                                                              ║
║  🎯 THIS IS THE WORLD'S FIRST TERMINAL-NATIVE JOB NOTIFICATION SYSTEM!      ║
╚══════════════════════════════════════════════════════════════════════════════╝

╭────────────────────────────────────────────────────────────────────────────╮
│  🔔 Terminal notification powered by JobTTY v1.1.0                        │
│  💡 Press Enter to dismiss • Keep terminal open for more alerts           │
╰────────────────────────────────────────────────────────────────────────────╯
"""
        return notification
    
    def _broadcast_to_terminals(self, notification: str):
        """Send notification using named pipes system"""
        
        try:
            # Use named pipe system instead of direct tty writing
            self._send_via_named_pipe(notification)
                
        except Exception as e:
            self._log(f"❌ Error broadcasting notification: {e}")
    
    def _send_via_named_pipe(self, notification: str):
        """Send notification to dedicated terminal window + system notification"""
        
        try:
            import subprocess
            import platform
            
            if platform.system() == 'Darwin':  # macOS
                # Extract job info for clean display
                company = "Unknown Company"
                position = "Job Alert"
                
                if "COMPANY:" in notification:
                    try:
                        company = notification.split("COMPANY:")[1].split("POSITION:")[0].strip()
                    except:
                        pass
                
                if "POSITION:" in notification:
                    try:
                        position = notification.split("POSITION:")[1].split("LOCATION:")[0].strip()
                    except:
                        pass
                
                # Send to named pipe for daemon listen
                self._send_via_pipe_fallback(notification)
            
            # Write to notification file as backup
            notification_file = Path.home() / ".jobtty" / "notifications.txt"
            try:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                with open(notification_file, 'a', encoding='utf-8') as f:
                    f.write(f"[{timestamp}] {notification}\n")
                    f.flush()
                self._log(f"📤 Notification written to {notification_file}")
                
            except Exception as e:
                self._log(f"❌ Failed to write notification: {e}")
            
        except Exception as e:
            self._log(f"❌ Notification error: {e}")
    
    def _send_via_pipe_fallback(self, notification: str):
        """Fallback pipe method"""
        pipe_dir = Path.home() / ".jobtty" / "pipes"
        pipe_dir.mkdir(exist_ok=True)
        notification_pipe = pipe_dir / "notifications"
        
        try:
            if not notification_pipe.exists():
                os.mkfifo(str(notification_pipe))
            
            # Write notification to pipe using Python directly (safer than bash)
            try:
                # Non-blocking write to named pipe
                with open(notification_pipe, 'w', encoding='utf-8') as pipe:
                    pipe.write(notification)
                    pipe.flush()
            except OSError:
                # If pipe is full or no reader, continue silently
                pass
            
        except Exception as e:
            self._log(f"❌ Error with named pipe: {e}")
    
    def _get_active_terminals(self) -> List[str]:
        """Get list of active terminal sessions (deprecated - using pipes now)"""
        return []
    
    def _log(self, message: str):
        """Write log message with timestamp"""
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        if self.is_running:
            # Daemon mode - write to file
            try:
                with open(self.log_file, 'a') as f:
                    f.write(f"{log_entry}\n")
                    f.flush()
            except:
                pass
        else:
            # Interactive mode - print to console
            print(log_entry)

# CLI convenience functions
def start_daemon(background: bool = True):
    """Start the notification daemon"""
    daemon = JobNotificationDaemon()
    daemon.start(daemonize=background)

def stop_daemon():
    """Stop the notification daemon"""
    daemon = JobNotificationDaemon()
    daemon.stop()

def daemon_status():
    """Check daemon status"""
    daemon = JobNotificationDaemon()
    daemon.status()

def check_notifications_once():
    """Manually check for notifications (for testing)"""
    daemon = JobNotificationDaemon()
    daemon._check_for_new_jobs()