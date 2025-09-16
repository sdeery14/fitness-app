"""
User session management for fitness planning.
"""
from typing import Optional, Dict, Any, List, TYPE_CHECKING
from datetime import datetime, date, timedelta
from dataclasses import dataclass, field
import uuid

from .fitness_plan_models import FitnessPlan

if TYPE_CHECKING:
    from .tools import ScheduledTrainingDay


@dataclass
class UserProfile:
    """User profile information."""
    name: Optional[str] = None
    age: Optional[int] = None
    height: Optional[float] = None  # in cm or inches
    weight: Optional[float] = None  # in kg or lbs
    fitness_level: Optional[str] = None  # beginner, intermediate, advanced
    goals: List[str] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)
    medical_conditions: List[str] = field(default_factory=list)
    equipment_available: List[str] = field(default_factory=list)


@dataclass
class WorkoutLog:
    """Log entry for a completed workout."""
    date: date
    workout_name: str
    exercises_completed: List[str]
    duration_minutes: Optional[int] = None
    notes: Optional[str] = None
    rating: Optional[int] = None  # 1-10 scale


@dataclass
class UserSession:
    """Manages user data and session state for fitness planning."""
    
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    
    # User data
    profile: UserProfile = field(default_factory=UserProfile)
    
    # Fitness plan data
    current_fitness_plan: Optional[FitnessPlan] = None
    fitness_plan_history: List[FitnessPlan] = field(default_factory=list)
    
    # Training schedule data
    current_schedule: List['ScheduledTrainingDay'] = field(default_factory=list)
    
    # Progress tracking
    workout_logs: List[WorkoutLog] = field(default_factory=list)
    measurements: Dict[str, Any] = field(default_factory=dict)
    
    def set_fitness_plan(self, fitness_plan: FitnessPlan) -> None:
        """Set the current fitness plan and update history."""
        if self.current_fitness_plan:
            self.fitness_plan_history.append(self.current_fitness_plan)
        
        self.current_fitness_plan = fitness_plan
        self.last_updated = datetime.now()
    
    def get_fitness_plan(self) -> Optional[FitnessPlan]:
        """Get the current fitness plan."""
        return self.current_fitness_plan
    
    def clear_fitness_plan(self) -> None:
        """Clear the current fitness plan."""
        if self.current_fitness_plan:
            self.fitness_plan_history.append(self.current_fitness_plan)
        self.current_fitness_plan = None
        self.current_schedule = []  # Clear schedule when plan is cleared
        self.last_updated = datetime.now()
    
    def has_fitness_plan(self) -> bool:
        """Check if a fitness plan is currently set."""
        return self.current_fitness_plan is not None
    
    def set_schedule(self, schedule: List['ScheduledTrainingDay']) -> None:
        """Set the current training schedule."""
        self.current_schedule = schedule
        self.last_updated = datetime.now()
    
    def get_schedule(self) -> List['ScheduledTrainingDay']:
        """Get the current training schedule."""
        return self.current_schedule
    
    def clear_schedule(self) -> None:
        """Clear the current training schedule."""
        self.current_schedule = []
        self.last_updated = datetime.now()
    
    def has_schedule(self) -> bool:
        """Check if a training schedule is currently set."""
        return len(self.current_schedule) > 0
    
    def update_profile(self, **kwargs) -> None:
        """Update user profile information."""
        for key, value in kwargs.items():
            if hasattr(self.profile, key):
                setattr(self.profile, key, value)
        self.last_updated = datetime.now()
    
    def log_workout(self, workout_log: WorkoutLog) -> None:
        """Add a workout log entry."""
        self.workout_logs.append(workout_log)
        self.last_updated = datetime.now()
    
    def get_recent_workouts(self, days: int = 30) -> List[WorkoutLog]:
        """Get workout logs from the last N days."""
        cutoff_date = date.today() - timedelta(days=days)
        return [log for log in self.workout_logs if log.date >= cutoff_date]
    
    def update_measurements(self, measurements: Dict[str, Any]) -> None:
        """Update user measurements (weight, body fat, etc.)."""
        self.measurements.update(measurements)
        self.last_updated = datetime.now()
    
    def clear_all_data(self) -> None:
        """Clear all user data including profile, fitness plan, and schedule."""
        self.profile = UserProfile()
        self.current_fitness_plan = None
        self.current_schedule = []
        self.workout_logs.clear()
        self.measurements.clear()
        self.last_updated = datetime.now()


class SessionManager:
    """Manages user sessions."""
    
    _sessions: Dict[str, UserSession] = {}
    _current_session_id: Optional[str] = None
    
    @classmethod
    def create_session(cls) -> UserSession:
        """Create a new user session."""
        session = UserSession()
        cls._sessions[session.session_id] = session
        cls._current_session_id = session.session_id
        return session
    
    @classmethod
    def get_session(cls, session_id: Optional[str] = None) -> Optional[UserSession]:
        """Get a session by ID, or the current session if no ID provided."""
        if session_id is None:
            session_id = cls._current_session_id
        
        if session_id is None:
            return None
            
        return cls._sessions.get(session_id)
    
    @classmethod
    def get_current_session(cls) -> Optional[UserSession]:
        """Get the current active session."""
        return cls.get_session()
    
    @classmethod
    def set_current_session(cls, session_id: str) -> bool:
        """Set the current active session."""
        if session_id in cls._sessions:
            cls._current_session_id = session_id
            return True
        return False
    
    @classmethod
    def get_or_create_session(cls, session_id: Optional[str] = None) -> UserSession:
        """Get an existing session or create a new one."""
        if session_id and session_id in cls._sessions:
            cls._current_session_id = session_id
            return cls._sessions[session_id]
        
        # If no current session exists, create one
        if cls._current_session_id is None or cls._current_session_id not in cls._sessions:
            return cls.create_session()
        
        return cls._sessions[cls._current_session_id]
    
    @classmethod
    def delete_session(cls, session_id: str) -> bool:
        """Delete a session."""
        if session_id in cls._sessions:
            del cls._sessions[session_id]
            if cls._current_session_id == session_id:
                cls._current_session_id = None
            return True
        return False
    
    @classmethod
    def list_sessions(cls) -> List[UserSession]:
        """Get all sessions."""
        return list(cls._sessions.values())
    
    @classmethod
    def clear_all_sessions(cls) -> None:
        """Clear all sessions."""
        cls._sessions.clear()
        cls._current_session_id = None
