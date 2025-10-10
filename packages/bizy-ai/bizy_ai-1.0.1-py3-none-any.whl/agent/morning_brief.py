#!/usr/bin/env python3
"""
Morning Briefing Script
Generates and displays the daily morning briefing
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.core import BusinessAgent
from agent.tasks import TaskManager
from agent.planner import BusinessPlanner
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

console = Console()

def display_banner():
    """Display welcome banner"""
    now = datetime.now()
    console.print()
    console.print(f"[bold cyan]{'='*70}[/bold cyan]")
    console.print(f"[bold cyan]  ☀️  MORNING BRIEFING - {now.strftime('%A, %B %d, %Y')}[/bold cyan]")
    console.print(f"[bold cyan]{'='*70}[/bold cyan]")
    console.print()

def run_morning_briefing():
    """Main function to run morning briefing"""
    try:
        display_banner()
        
        # Initialize components
        console.print("[dim]Initializing business agent...[/dim]")
        agent = BusinessAgent()
        task_mgr = TaskManager()
        planner = BusinessPlanner()
        
        # Get yesterday's summary
        console.print("[dim]Analyzing yesterday's performance...[/dim]")
        yesterday_summary = task_mgr.get_yesterday_summary()
        
        # Get today's tasks
        console.print("[dim]Loading today's tasks...[/dim]")
        today_tasks = task_mgr.get_tasks_for_today()
        
        # Get active goals
        console.print("[dim]Checking goal progress...[/dim]")
        active_goals = planner.get_active_goals()
        
        # Get overdue tasks
        overdue_tasks = task_mgr.get_overdue_tasks()
        
        console.print()
        
        # Display quick stats
        console.print("[bold]📊 Quick Stats:[/bold]")
        console.print(f"  • Yesterday: {yesterday_summary['tasks_completed']}/{yesterday_summary['tasks_due']} tasks completed ({yesterday_summary['completion_rate']:.0%})")
        console.print(f"  • Today: {len(today_tasks)} tasks scheduled")
        console.print(f"  • Active goals: {len(active_goals)}")
        if overdue_tasks:
            console.print(f"  • [yellow]⚠️  {len(overdue_tasks)} overdue tasks[/yellow]")
        console.print()
        
        # Generate AI briefing
        console.print("[dim]Generating personalized briefing...[/dim]")
        briefing = agent.morning_briefing(
            tasks_today=today_tasks,
            yesterday_summary=yesterday_summary,
            business_context="See active goals below",
            goals=active_goals
        )
        
        # Display the briefing
        console.print(Panel(
            Markdown(briefing),
            title="🤖 Your Daily Briefing",
            border_style="blue",
            padding=(1, 2)
        ))
        
        # Display today's task list
        if today_tasks:
            console.print()
            console.print("[bold]📋 Today's Task List:[/bold]")
            console.print()
            
            # Sort by priority
            sorted_tasks = sorted(today_tasks, key=lambda t: t.priority)
            
            for i, task in enumerate(sorted_tasks[:10], 1):
                priority_emoji = {1: "🔴", 2: "🟠", 3: "🟡", 4: "🟢", 5: "🔵"}.get(task.priority, "⚪")
                status_emoji = {"pending": "⏳", "in_progress": "🔄", "blocked": "🚧"}.get(task.status, "❓")
                
                task_line = f"{i}. {priority_emoji} {status_emoji} {task.title}"
                
                if task.estimated_hours:
                    task_line += f" [dim]({task.estimated_hours}h)[/dim]"
                
                if task.category:
                    task_line += f" [dim italic]#{task.category}[/dim italic]"
                
                console.print(f"   {task_line}")
        
        # Display overdue tasks if any
        if overdue_tasks:
            console.print()
            console.print("[bold yellow]⚠️  Overdue Tasks:[/bold yellow]")
            for task in overdue_tasks[:5]:
                console.print(f"   • {task.title} [dim](Due: {task.due_date.strftime('%m/%d')})[/dim]")
        
        console.print()
        console.print("[bold green]✨ Have a productive day! ✨[/bold green]")
        console.print()
        
        # Cleanup
        task_mgr.close()
        planner.close()
        
    except Exception as e:
        console.print(f"[bold red]❌ Error generating briefing:[/bold red] {e}")
        import traceback
        console.print(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    run_morning_briefing()
