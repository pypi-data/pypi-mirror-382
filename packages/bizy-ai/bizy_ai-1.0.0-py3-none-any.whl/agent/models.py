from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class Task(Base):
    __tablename__ = 'tasks'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    priority = Column(Integer, default=3)  # 1=highest, 5=lowest
    status = Column(String(50), default='pending')  # pending, in_progress, completed, blocked
    category = Column(String(100))  # development, marketing, operations, finance, etc.
    estimated_hours = Column(Float)
    actual_hours = Column(Float)
    due_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    parent_goal_id = Column(Integer)  # Links to goals
    dependencies = Column(JSON)  # List of task IDs this depends on
    notes = Column(Text)
    tags = Column(JSON)  # List of tags for filtering
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'status': self.status,
            'category': self.category,
            'estimated_hours': self.estimated_hours,
            'actual_hours': self.actual_hours,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'parent_goal_id': self.parent_goal_id,
            'dependencies': self.dependencies or [],
            'notes': self.notes,
            'tags': self.tags or []
        }

class Goal(Base):
    __tablename__ = 'goals'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    horizon = Column(String(50))  # yearly, quarterly, monthly, weekly
    target_date = Column(DateTime)
    status = Column(String(50), default='active')  # active, completed, on_hold, cancelled
    progress_percentage = Column(Float, default=0.0)
    success_criteria = Column(Text)
    parent_goal_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metrics = Column(JSON)  # Key metrics to track
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'horizon': self.horizon,
            'target_date': self.target_date.isoformat() if self.target_date else None,
            'status': self.status,
            'progress_percentage': self.progress_percentage,
            'success_criteria': self.success_criteria,
            'parent_goal_id': self.parent_goal_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'metrics': self.metrics or {}
        }

class DailyLog(Base):
    __tablename__ = 'daily_logs'
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False, unique=True)
    tasks_completed = Column(Integer, default=0)
    tasks_planned = Column(Integer, default=0)
    completion_rate = Column(Float)
    energy_level = Column(String(20))  # high, medium, low
    blockers = Column(Text)
    wins = Column(Text)
    learnings = Column(Text)
    tomorrow_focus = Column(Text)
    mood = Column(String(50))
    notes = Column(Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'tasks_completed': self.tasks_completed,
            'tasks_planned': self.tasks_planned,
            'completion_rate': self.completion_rate,
            'energy_level': self.energy_level,
            'blockers': self.blockers,
            'wins': self.wins,
            'learnings': self.learnings,
            'tomorrow_focus': self.tomorrow_focus,
            'mood': self.mood,
            'notes': self.notes
        }

class ResearchItem(Base):
    __tablename__ = 'research'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(500))
    summary = Column(Text)
    source_url = Column(String(1000))
    category = Column(String(100))  # competitor, trend, opportunity, threat, technology
    relevance_score = Column(Float)
    date_found = Column(DateTime, default=datetime.utcnow)
    action_items = Column(Text)
    tags = Column(JSON)
    raw_data = Column(JSON)  # Store full research data
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'summary': self.summary,
            'source_url': self.source_url,
            'category': self.category,
            'relevance_score': self.relevance_score,
            'date_found': self.date_found.isoformat() if self.date_found else None,
            'action_items': self.action_items,
            'tags': self.tags or []
        }

class BusinessMetric(Base):
    __tablename__ = 'metrics'
    
    id = Column(Integer, primary_key=True)
    metric_name = Column(String(200))
    value = Column(Float)
    date = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)
    target_value = Column(Float)
    category = Column(String(100))  # revenue, growth, customer, product, etc.
    
    def to_dict(self):
        return {
            'id': self.id,
            'metric_name': self.metric_name,
            'value': self.value,
            'date': self.date.isoformat() if self.date else None,
            'notes': self.notes,
            'target_value': self.target_value,
            'category': self.category
        }

class BusinessPlan(Base):
    __tablename__ = 'business_plans'
    
    id = Column(Integer, primary_key=True)
    version = Column(String(50))
    vision = Column(Text)
    mission = Column(Text)
    value_proposition = Column(Text)
    target_market = Column(Text)
    revenue_model = Column(Text)
    key_resources = Column(JSON)
    key_activities = Column(JSON)
    key_partnerships = Column(JSON)
    cost_structure = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'version': self.version,
            'vision': self.vision,
            'mission': self.mission,
            'value_proposition': self.value_proposition,
            'target_market': self.target_market,
            'revenue_model': self.revenue_model,
            'key_resources': self.key_resources or {},
            'key_activities': self.key_activities or [],
            'key_partnerships': self.key_partnerships or [],
            'cost_structure': self.cost_structure or {},
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active
        }

# Database setup
def get_engine(db_path=None):
    if db_path is None:
        # Use environment variable or default to home directory
        db_path = os.getenv('BUSINESS_AGENT_DB', os.path.expanduser('~/.business-agent/tasks.db'))

    # Create directory if it doesn't exist
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    return create_engine(f'sqlite:///{db_path}', echo=False)

def get_session(engine=None):
    if engine is None:
        engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()

def init_database(db_path=None):
    """Initialize the database with all tables"""
    engine = get_engine(db_path)
    Base.metadata.create_all(engine)
    return engine
