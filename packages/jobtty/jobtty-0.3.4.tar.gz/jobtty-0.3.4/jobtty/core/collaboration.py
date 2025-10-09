"""
Live Terminal Collaboration System
Real-time pair programming and monitoring for Jobtty challenges
"""

import asyncio
import json
import uuid
from typing import Dict, Set, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

# Optional websockets import
try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    websockets = None
    WEBSOCKETS_AVAILABLE = False

class SessionType(Enum):
    PAIR_PROGRAMMING = "pair"
    RECRUITER_MONITORING = "monitor"
    GROUP_CHALLENGE = "group"
    MENTORING = "mentor"

class UserRole(Enum):
    DRIVER = "driver"      # Active coder
    NAVIGATOR = "navigator" # Pair programming partner  
    OBSERVER = "observer"   # Recruiter/mentor watching
    MODERATOR = "moderator" # Session host

@dataclass
class CollaborationSession:
    """Live collaboration session model"""
    id: str
    challenge_id: str
    session_type: SessionType
    created_at: datetime
    expires_at: datetime
    
    # Participants
    participants: Dict[str, UserRole] = field(default_factory=dict)
    max_participants: int = 4
    
    # Session state
    active_file: Optional[str] = None
    cursor_position: tuple = (0, 0)
    shared_state: Dict[str, Any] = field(default_factory=dict)
    
    # Analytics for recruiters
    keystrokes_per_user: Dict[str, int] = field(default_factory=dict)
    command_history: list = field(default_factory=list)
    git_commits: list = field(default_factory=list)
    test_runs: list = field(default_factory=list)

class TerminalCollaborationServer:
    """WebSocket server for real-time terminal collaboration"""
    
    def __init__(self):
        self.sessions: Dict[str, CollaborationSession] = {}
        self.connections: Dict[str, Any] = {}  # WebSocket connections when available
        self.user_sessions: Dict[str, str] = {}  # user_id -> session_id
        
    async def start_server(self, host="localhost", port=8765):
        """Start the collaboration WebSocket server"""
        if not WEBSOCKETS_AVAILABLE:
            print("❌ WebSocket collaboration requires 'websockets' package")
            print("💡 Install with: pip3 install websockets")
            return False
            
        print(f"🚀 Starting Jobtty Collaboration Server on {host}:{port}")
        
        async with websockets.serve(self.handle_connection, host, port):
            await asyncio.Future()  # Run forever
    
    async def handle_connection(self, websocket, path):
        """Handle new WebSocket connections"""
        user_id = str(uuid.uuid4())
        self.connections[user_id] = websocket
        
        try:
            await self.send_welcome(user_id)
            
            async for message in websocket:
                await self.process_message(user_id, message)
                
        except Exception as e:  # Handle ConnectionClosed and other websocket errors
            if 'ConnectionClosed' in str(type(e)):
                await self.handle_disconnect(user_id)
            else:
                print(f"WebSocket error: {e}")
        finally:
            if user_id in self.connections:
                del self.connections[user_id]
    
    async def send_welcome(self, user_id: str):
        """Send welcome message to new connection"""
        welcome = {
            "type": "welcome",
            "user_id": user_id,
            "server_info": {
                "name": "Jobtty Collaboration Server",
                "version": "1.0.0",
                "features": ["pair_programming", "live_monitoring", "git_integration"]
            }
        }
        await self.send_to_user(user_id, welcome)
    
    async def process_message(self, user_id: str, message: str):
        """Process incoming messages from clients"""
        try:
            data = json.loads(message)
            msg_type = data.get("type")
            
            if msg_type == "join_session":
                await self.handle_join_session(user_id, data)
            elif msg_type == "create_session":
                await self.handle_create_session(user_id, data)
            elif msg_type == "terminal_input":
                await self.handle_terminal_input(user_id, data)
            elif msg_type == "cursor_move":
                await self.handle_cursor_move(user_id, data)
            elif msg_type == "file_change":
                await self.handle_file_change(user_id, data)
            elif msg_type == "git_action":
                await self.handle_git_action(user_id, data)
            elif msg_type == "chat_message":
                await self.handle_chat_message(user_id, data)
                
        except json.JSONDecodeError:
            await self.send_error(user_id, "Invalid JSON message")
    
    async def handle_create_session(self, user_id: str, data: dict):
        """Create a new collaboration session"""
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        challenge_id = data.get("challenge_id")
        session_type = SessionType(data.get("session_type", "pair"))
        
        session = CollaborationSession(
            id=session_id,
            challenge_id=challenge_id,
            session_type=session_type,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=4),
            participants={user_id: UserRole.DRIVER}
        )
        
        self.sessions[session_id] = session
        self.user_sessions[user_id] = session_id
        
        response = {
            "type": "session_created",
            "session_id": session_id,
            "join_command": f"jobtty pair join {session_id}",
            "monitor_command": f"jobtty recruit monitor {session_id}"
        }
        
        await self.send_to_user(user_id, response)
        print(f"📡 Session {session_id} created for challenge {challenge_id}")
    
    async def handle_join_session(self, user_id: str, data: dict):
        """Join an existing collaboration session"""
        session_id = data.get("session_id")
        role = UserRole(data.get("role", "navigator"))
        
        if session_id not in self.sessions:
            await self.send_error(user_id, f"Session {session_id} not found")
            return
            
        session = self.sessions[session_id]
        
        if len(session.participants) >= session.max_participants:
            await self.send_error(user_id, "Session full")
            return
        
        session.participants[user_id] = role
        self.user_sessions[user_id] = session_id
        
        # Notify all participants
        join_notification = {
            "type": "user_joined",
            "user_id": user_id,
            "role": role.value,
            "participants_count": len(session.participants)
        }
        
        await self.broadcast_to_session(session_id, join_notification)
        
        # Send session state to new user
        session_state = {
            "type": "session_state",
            "session": {
                "id": session.id,
                "challenge_id": session.challenge_id,
                "participants": {uid: role.value for uid, role in session.participants.items()},
                "active_file": session.active_file,
                "cursor_position": session.cursor_position
            }
        }
        await self.send_to_user(user_id, session_state)
    
    async def handle_terminal_input(self, user_id: str, data: dict):
        """Handle terminal input from participants"""
        session_id = self.user_sessions.get(user_id)
        if not session_id:
            return
            
        session = self.sessions[session_id]
        user_role = session.participants.get(user_id)
        
        # Only driver can type by default
        if user_role != UserRole.DRIVER and data.get("force") != True:
            await self.send_error(user_id, "Only driver can type. Use 'jobtty pair request-control' to take over")
            return
        
        # Track keystroke analytics
        session.keystrokes_per_user[user_id] = session.keystrokes_per_user.get(user_id, 0) + 1
        
        # Track commands for skill analysis
        if data.get("command"):
            session.command_history.append({
                "user_id": user_id,
                "command": data["command"],
                "timestamp": datetime.now().isoformat()
            })
        
        # Broadcast terminal input to all participants
        terminal_update = {
            "type": "terminal_update",
            "user_id": user_id,
            "input": data.get("input", ""),
            "command": data.get("command"),
            "output": data.get("output"),
            "timestamp": datetime.now().isoformat()
        }
        
        await self.broadcast_to_session(session_id, terminal_update)
    
    async def handle_git_action(self, user_id: str, data: dict):
        """Track git actions for progress scoring"""
        session_id = self.user_sessions.get(user_id)
        if not session_id:
            return
            
        session = self.sessions[session_id]
        
        git_event = {
            "user_id": user_id,
            "action": data.get("action"),  # commit, push, branch, etc
            "message": data.get("message"),
            "files_changed": data.get("files_changed", []),
            "timestamp": datetime.now().isoformat()
        }
        
        session.git_commits.append(git_event)
        
        # Calculate progress score based on git activity
        progress_score = self.calculate_progress_score(session)
        
        git_update = {
            "type": "git_update",
            "user_id": user_id,
            "git_event": git_event,
            "progress_score": progress_score,
            "leaderboard_position": self.get_leaderboard_position(session_id, user_id)
        }
        
        await self.broadcast_to_session(session_id, git_update)
    
    def calculate_progress_score(self, session: CollaborationSession) -> int:
        """Calculate progress score based on git activity and commands"""
        score = 0
        
        # Git commit scoring
        for commit in session.git_commits:
            score += 10  # Base points per commit
            if commit.get("files_changed"):
                score += len(commit["files_changed"]) * 2
        
        # Command variety bonus
        unique_commands = set(cmd["command"] for cmd in session.command_history if cmd.get("command"))
        score += len(unique_commands) * 5
        
        # Test run bonus
        test_commands = [cmd for cmd in session.command_history if "test" in cmd.get("command", "")]
        score += len(test_commands) * 15
        
        return score
    
    def get_leaderboard_position(self, session_id: str, user_id: str) -> int:
        """Get user's position in session leaderboard"""
        session = self.sessions[session_id]
        scores = []
        
        for uid in session.participants:
            user_score = session.keystrokes_per_user.get(uid, 0)
            scores.append((uid, user_score))
        
        scores.sort(key=lambda x: x[1], reverse=True)
        
        for i, (uid, score) in enumerate(scores):
            if uid == user_id:
                return i + 1
        return len(scores)
    
    async def send_to_user(self, user_id: str, message: dict):
        """Send message to specific user"""
        if user_id in self.connections:
            await self.connections[user_id].send(json.dumps(message))
    
    async def broadcast_to_session(self, session_id: str, message: dict):
        """Broadcast message to all session participants"""
        if session_id not in self.sessions:
            return
            
        session = self.sessions[session_id]
        for user_id in session.participants:
            await self.send_to_user(user_id, message)
    
    async def send_error(self, user_id: str, error: str):
        """Send error message to user"""
        error_msg = {
            "type": "error",
            "message": error,
            "timestamp": datetime.now().isoformat()
        }
        await self.send_to_user(user_id, error_msg)
    
    async def handle_disconnect(self, user_id: str):
        """Handle user disconnection"""
        session_id = self.user_sessions.get(user_id)
        if session_id and session_id in self.sessions:
            session = self.sessions[session_id]
            
            if user_id in session.participants:
                del session.participants[user_id]
                
                # Notify remaining participants
                disconnect_msg = {
                    "type": "user_left",
                    "user_id": user_id,
                    "participants_count": len(session.participants)
                }
                await self.broadcast_to_session(session_id, disconnect_msg)
                
                # Clean up empty sessions
                if not session.participants:
                    del self.sessions[session_id]
                    print(f"🗑️ Cleaned up empty session {session_id}")
        
        if user_id in self.user_sessions:
            del self.user_sessions[user_id]

# Terminal sharing client integration
class TerminalShareClient:
    """Client for sharing terminal sessions"""
    
    def __init__(self, server_url="ws://localhost:8765"):
        self.server_url = server_url
        self.websocket = None
        self.session_id = None
        self.user_id = None
        
    async def connect(self):
        """Connect to collaboration server"""
        if not WEBSOCKETS_AVAILABLE:
            print("❌ WebSocket collaboration requires 'websockets' package")
            print("💡 Install with: pip3 install websockets")
            return False
            
        try:
            self.websocket = await websockets.connect(self.server_url)
            print("🔗 Connected to Jobtty Collaboration Server")
            return True
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            return False
    
    async def create_session(self, challenge_id: str, session_type: str = "pair"):
        """Create a new collaboration session"""
        if not self.websocket:
            return None
            
        message = {
            "type": "create_session",
            "challenge_id": challenge_id,
            "session_type": session_type
        }
        
        await self.websocket.send(json.dumps(message))
        response = await self.websocket.recv()
        return json.loads(response)
    
    async def join_session(self, session_id: str, role: str = "navigator"):
        """Join an existing session"""
        if not self.websocket:
            return False
            
        message = {
            "type": "join_session", 
            "session_id": session_id,
            "role": role
        }
        
        await self.websocket.send(json.dumps(message))
        self.session_id = session_id
        return True
    
    async def share_terminal_input(self, input_text: str, command: str = None):
        """Share terminal input with session participants"""
        if not self.websocket or not self.session_id:
            return
            
        message = {
            "type": "terminal_input",
            "input": input_text,
            "command": command,
            "timestamp": datetime.now().isoformat()
        }
        
        await self.websocket.send(json.dumps(message))
    
    async def share_git_action(self, action: str, commit_message: str = None, files: list = None):
        """Share git actions with session"""
        if not self.websocket or not self.session_id:
            return
            
        message = {
            "type": "git_action",
            "action": action,
            "message": commit_message,
            "files_changed": files or [],
            "timestamp": datetime.now().isoformat()
        }
        
        await self.websocket.send(json.dumps(message))
    
    async def listen_for_updates(self, callback):
        """Listen for real-time updates from other participants"""
        if not self.websocket:
            return
            
        try:
            async for message in self.websocket:
                data = json.loads(message)
                await callback(data)
        except Exception as e:  # Handle ConnectionClosed and other websocket errors
            if 'ConnectionClosed' in str(type(e)):
                print("🔌 Connection to collaboration server lost")
            else:
                print(f"WebSocket error: {e}")

# CLI Integration helpers
def create_collaboration_session(challenge_id: str, session_type: str = "pair"):
    """Create a new collaboration session from CLI"""
    if not WEBSOCKETS_AVAILABLE:
        print("❌ WebSocket collaboration requires 'websockets' package")
        print("💡 Install with: pip3 install websockets")
        print("🔧 Or use local challenges: jobtty challenges --list")
        return False
        
    asyncio.run(_create_session_async(challenge_id, session_type))

async def _create_session_async(challenge_id: str, session_type: str):
    """Async helper for session creation"""
    client = TerminalShareClient()
    
    if await client.connect():
        result = await client.create_session(challenge_id, session_type)
        
        if result and result.get("type") == "session_created":
            session_id = result["session_id"]
            print(f"""
🎉 Collaboration session created!

Session ID: {session_id}
Challenge: {challenge_id}

🤝 Invite others:
   jobtty pair join {session_id}

👀 Recruiter monitoring: 
   jobtty recruit monitor {session_id}

🔗 Web dashboard:
   https://jobtty.io/sessions/{session_id}
""")
        else:
            print("❌ Failed to create session")

def join_collaboration_session(session_id: str, role: str = "navigator"):
    """Join an existing collaboration session"""
    if not WEBSOCKETS_AVAILABLE:
        print("❌ WebSocket collaboration requires 'websockets' package")
        print("💡 Install with: pip3 install websockets")
        print("🔧 Or use local challenges: jobtty challenges --list")
        return False
        
    asyncio.run(_join_session_async(session_id, role))

async def _join_session_async(session_id: str, role: str):
    """Async helper for joining sessions"""
    client = TerminalShareClient()
    
    if await client.connect():
        success = await client.join_session(session_id, role)
        
        if success:
            print(f"🚀 Joined session {session_id} as {role}")
            
            # Start real-time terminal sharing
            async def handle_updates(data):
                msg_type = data.get("type")
                
                if msg_type == "terminal_update":
                    user_id = data.get("user_id")
                    command = data.get("command")
                    output = data.get("output")
                    
                    if command:
                        print(f"💻 [{user_id[:8]}] $ {command}")
                    if output:
                        print(f"📤 {output}")
                
                elif msg_type == "git_update":
                    git_event = data.get("git_event", {})
                    action = git_event.get("action")
                    message = git_event.get("message")
                    score = data.get("progress_score")
                    
                    print(f"🔗 Git {action}: {message} (Score: {score})")
                
                elif msg_type == "user_joined":
                    role_joined = data.get("role")
                    print(f"👋 New {role_joined} joined the session")
            
            await client.listen_for_updates(handle_updates)
        else:
            print(f"❌ Failed to join session {session_id}")