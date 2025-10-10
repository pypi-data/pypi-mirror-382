from datetime import datetime, timedelta
from sqlalchemy import and_
from agent.models import Goal, BusinessPlan, Task, get_session
from agent.tasks import TaskManager
import anthropic
import os
import json

class BusinessPlanner:
    def __init__(self):
        self.session = get_session()
        self.task_mgr = TaskManager()
        self.client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.model = "claude-sonnet-4-20250514"
    
    # === Business Plan Management ===
    
    def create_business_plan(self, vision, mission, value_proposition, 
                           target_market, revenue_model, key_resources=None,
                           key_activities=None, key_partnerships=None, 
                           cost_structure=None, version="1.0"):
        """Create a new business plan"""
        # Deactivate old plans
        old_plans = self.session.query(BusinessPlan).filter(
            BusinessPlan.is_active == True
        ).all()
        for plan in old_plans:
            plan.is_active = False
        
        plan = BusinessPlan(
            version=version,
            vision=vision,
            mission=mission,
            value_proposition=value_proposition,
            target_market=target_market,
            revenue_model=revenue_model,
            key_resources=key_resources or {},
            key_activities=key_activities or [],
            key_partnerships=key_partnerships or [],
            cost_structure=cost_structure or {},
            is_active=True
        )
        self.session.add(plan)
        self.session.commit()
        return plan
    
    def get_active_business_plan(self):
        """Get the current active business plan"""
        return self.session.query(BusinessPlan).filter(
            BusinessPlan.is_active == True
        ).first()
    
    # === Goal Management ===
    
    def create_goal(self, title, description, horizon, target_date=None, 
                   success_criteria=None, parent_goal_id=None, metrics=None):
        """Create a new goal"""
        goal = Goal(
            title=title,
            description=description,
            horizon=horizon,
            target_date=target_date,
            success_criteria=success_criteria,
            parent_goal_id=parent_goal_id,
            metrics=metrics or {}
        )
        self.session.add(goal)
        self.session.commit()
        return goal
    
    def get_goal(self, goal_id):
        """Get a specific goal"""
        return self.session.query(Goal).filter(Goal.id == goal_id).first()
    
    def get_active_goals(self):
        """Get all active goals"""
        return self.session.query(Goal).filter(
            Goal.status == 'active'
        ).order_by(Goal.horizon, Goal.target_date).all()
    
    def get_goals_by_horizon(self, horizon):
        """Get goals for a specific time horizon"""
        return self.session.query(Goal).filter(
            and_(
                Goal.horizon == horizon,
                Goal.status == 'active'
            )
        ).order_by(Goal.target_date).all()
    
    def update_goal_progress(self, goal_id, progress_percentage):
        """Update goal progress"""
        goal = self.get_goal(goal_id)
        if goal:
            goal.progress_percentage = progress_percentage
            goal.updated_at = datetime.now()
            
            # Auto-complete if 100%
            if progress_percentage >= 100:
                goal.status = 'completed'
            
            self.session.commit()
        return goal
    
    def calculate_goal_progress(self, goal_id):
        """Calculate goal progress based on completed tasks"""
        tasks = self.task_mgr.get_tasks_by_goal(goal_id)
        if not tasks:
            return 0
        
        completed = len([t for t in tasks if t.status == 'completed'])
        progress = (completed / len(tasks)) * 100
        
        # Update the goal
        self.update_goal_progress(goal_id, progress)
        return progress
    
    # === Goal Breakdown (AI-Powered) ===
    
    def break_down_goal(self, goal_id):
        """Use AI to break down a goal into actionable tasks"""
        goal = self.get_goal(goal_id)
        if not goal:
            return None
        
        business_plan = self.get_active_business_plan()
        context = ""
        if business_plan:
            context = f"""
Business Context:
- Vision: {business_plan.vision}
- Mission: {business_plan.mission}
- Value Proposition: {business_plan.value_proposition}
"""
        
        prompt = f"""{context}

I need help breaking down this business goal into actionable tasks:

GOAL: {goal.title}
DESCRIPTION: {goal.description}
TIME HORIZON: {goal.horizon}
TARGET DATE: {goal.target_date.strftime('%Y-%m-%d') if goal.target_date else 'Not set'}
SUCCESS CRITERIA: {goal.success_criteria or 'Not defined'}

Please break this goal down into 5-10 specific, actionable tasks that would help achieve this goal. For each task, provide:

1. Title (clear, action-oriented)
2. Description (what needs to be done)
3. Estimated hours
4. Priority (1-5, where 1 is highest)
5. Category (development, marketing, operations, finance, etc.)
6. Dependencies (if any, reference other task numbers)

Format your response as a JSON array of tasks:
[
  {{
    "title": "Task title",
    "description": "Detailed description",
    "estimated_hours": 2.5,
    "priority": 1,
    "category": "development",
    "dependencies": []
  }},
  ...
]

Only return the JSON array, no additional text."""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=3000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
                response_text = response_text.strip()
            
            tasks_data = json.loads(response_text)
            
            # Create tasks in database
            created_tasks = []
            task_id_mapping = {}  # Map array index to actual task ID
            
            for i, task_data in enumerate(tasks_data):
                # Calculate due date based on goal target date
                due_date = None
                if goal.target_date:
                    # Distribute tasks evenly before target date
                    days_until_target = (goal.target_date - datetime.now()).days
                    task_offset = (days_until_target / len(tasks_data)) * (i + 1)
                    due_date = datetime.now() + timedelta(days=task_offset)
                
                task = self.task_mgr.create_task(
                    title=task_data['title'],
                    description=task_data['description'],
                    estimated_hours=task_data.get('estimated_hours'),
                    priority=task_data.get('priority', 3),
                    category=task_data.get('category'),
                    due_date=due_date,
                    parent_goal_id=goal_id,
                    dependencies=[]  # Will update after all tasks created
                )
                created_tasks.append(task)
                task_id_mapping[i] = task.id
            
            # Update dependencies
            for i, task_data in enumerate(tasks_data):
                if task_data.get('dependencies'):
                    dep_ids = [task_id_mapping[dep_idx] for dep_idx in task_data['dependencies'] 
                              if dep_idx in task_id_mapping]
                    created_tasks[i].dependencies = dep_ids
            
            self.session.commit()
            return created_tasks
            
        except Exception as e:
            print(f"Error breaking down goal: {e}")
            return None
    
    def suggest_next_tasks(self, goal_id, num_tasks=3):
        """Use AI to suggest next tasks based on current progress"""
        goal = self.get_goal(goal_id)
        if not goal:
            return None
        
        existing_tasks = self.task_mgr.get_tasks_by_goal(goal_id)
        completed_tasks = [t for t in existing_tasks if t.status == 'completed']
        pending_tasks = [t for t in existing_tasks if t.status in ['pending', 'in_progress']]
        
        completed_str = "\n".join([f"- {t.title}" for t in completed_tasks[:10]])
        pending_str = "\n".join([f"- {t.title} ({t.status})" for t in pending_tasks[:10]])
        
        prompt = f"""Given this goal and current progress, suggest {num_tasks} next actionable tasks:

GOAL: {goal.title}
DESCRIPTION: {goal.description}
PROGRESS: {goal.progress_percentage}%

COMPLETED TASKS:
{completed_str or 'None yet'}

PENDING/IN-PROGRESS TASKS:
{pending_str or 'None'}

Suggest {num_tasks} new tasks that would best advance this goal right now. Consider:
- What's already been accomplished
- What's currently in progress
- Natural next steps
- Quick wins vs. strategic moves

Return as JSON array with same format as before."""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text.strip()
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
                response_text = response_text.strip()
            
            tasks_data = json.loads(response_text)
            
            created_tasks = []
            for task_data in tasks_data:
                task = self.task_mgr.create_task(
                    title=task_data['title'],
                    description=task_data['description'],
                    estimated_hours=task_data.get('estimated_hours'),
                    priority=task_data.get('priority', 3),
                    category=task_data.get('category'),
                    parent_goal_id=goal_id
                )
                created_tasks.append(task)
            
            return created_tasks
            
        except Exception as e:
            print(f"Error suggesting tasks: {e}")
            return None
    
    def create_goal_hierarchy(self, yearly_goal_title, yearly_goal_description):
        """Create a full goal hierarchy: yearly -> quarterly -> monthly"""
        # Create yearly goal
        yearly_goal = self.create_goal(
            title=yearly_goal_title,
            description=yearly_goal_description,
            horizon='yearly',
            target_date=datetime.now() + timedelta(days=365)
        )
        
        # Use AI to break into quarterly goals
        prompt = f"""Break down this yearly goal into 4 quarterly goals:

YEARLY GOAL: {yearly_goal_title}
DESCRIPTION: {yearly_goal_description}

Create 4 quarterly milestones (Q1, Q2, Q3, Q4) that would logically lead to achieving this yearly goal.

Return as JSON:
[
  {{
    "title": "Q1 goal title",
    "description": "What to achieve in Q1",
    "success_criteria": "How to measure success"
  }},
  ...
]"""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text.strip()
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
                response_text = response_text.strip()
            
            quarterly_goals_data = json.loads(response_text)
            
            quarterly_goals = []
            for i, qgoal_data in enumerate(quarterly_goals_data):
                target = datetime.now() + timedelta(days=90 * (i + 1))
                qgoal = self.create_goal(
                    title=qgoal_data['title'],
                    description=qgoal_data['description'],
                    horizon='quarterly',
                    target_date=target,
                    success_criteria=qgoal_data.get('success_criteria'),
                    parent_goal_id=yearly_goal.id
                )
                quarterly_goals.append(qgoal)
            
            return {
                'yearly': yearly_goal,
                'quarterly': quarterly_goals
            }
            
        except Exception as e:
            print(f"Error creating goal hierarchy: {e}")
            return {'yearly': yearly_goal, 'quarterly': []}
    
    def close(self):
        """Close database session"""
        self.session.close()
        self.task_mgr.close()
