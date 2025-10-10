#!/usr/bin/env python3
"""Database Initialization Script"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.models import init_database
from rich.console import Console
from rich.prompt import Confirm

console = Console()

def main():
    console.print("[bold cyan]Business Agent Database Setup[/bold cyan]")
    console.print()
    
    console.print("Initializing database...")
    try:
        engine = init_database()
        console.print("[green]✓[/green] Database initialized successfully!")
        console.print(f"[dim]Location: data/tasks.db[/dim]")
        console.print()
        
        if Confirm.ask("Would you like to create sample tasks and goals?"):
            from agent.tasks import TaskManager
            from agent.planner import BusinessPlanner
            from datetime import datetime, timedelta
            
            task_mgr = TaskManager()
            planner = BusinessPlanner()
            
            console.print()
            console.print("Creating sample data...")
            
            # Create a sample yearly goal
            yearly_goal = planner.create_goal(
                title="Launch MVP Product",
                description="Build and launch the minimum viable product for our business agent",
                horizon="yearly",
                target_date=datetime.now() + timedelta(days=365),
                success_criteria="10 paying customers using the product daily"
            )
            console.print("[green]✓[/green] Created yearly goal")
            
            # Create sample tasks
            sample_tasks = [
                {
                    "title": "Set up development environment",
                    "description": "Install dependencies and configure the project",
                    "priority": 1,
                    "category": "development",
                    "estimated_hours": 2.0,
                    "due_date": datetime.now() + timedelta(days=1)
                },
                {
                    "title": "Define business plan",
                    "description": "Fill out the business plan template",
                    "priority": 1,
                    "category": "planning",
                    "estimated_hours": 3.0,
                    "due_date": datetime.now() + timedelta(days=2)
                }
            ]
            
            for task_data in sample_tasks:
                task_mgr.create_task(parent_goal_id=yearly_goal.id, **task_data)
            
            console.print(f"[green]✓[/green] Created {len(sample_tasks)} sample tasks")
            console.print()
            
            task_mgr.close()
            planner.close()
        
        console.print()
        console.print("[bold green]Setup complete![/bold green]")
        console.print()
        console.print("Next steps:")
        console.print("1. Copy .env.example to .env and add your ANTHROPIC_API_KEY")
        console.print("2. Fill out templates/business_plan_template.yaml")
        console.print("3. Run: python scripts/morning_brief.py")
        console.print()
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        import traceback
        console.print(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
