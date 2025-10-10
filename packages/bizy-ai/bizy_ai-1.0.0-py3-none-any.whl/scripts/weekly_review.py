#!/usr/bin/env python3
"""Weekly Review Script"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.core import BusinessAgent
from agent.tasks import TaskManager
from agent.planner import BusinessPlanner
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
console = Console()

def run_weekly_review():
    try:
        console.print(f"\n[bold blue]📊 WEEKLY REVIEW - {datetime.now().strftime('%B %d, %Y')}[/bold blue]\n")
        
        agent = BusinessAgent()
        task_mgr = TaskManager()
        planner = BusinessPlanner()
        
        # Get weekly statistics
        weekly_stats = task_mgr.get_weekly_stats()
        
        # Get goal progress
        active_goals = planner.get_active_goals()
        goals_progress = "\n".join([
            f"- {g.title}: {g.progress_percentage:.0f}% complete"
            for g in active_goals[:5]
        ]) if active_goals else "No active goals"
        
        # Get key events
        key_events = []
        for log in weekly_stats.get('logs', []):
            if log.get('wins'):
                key_events.append(f"Win: {log['wins']}")
        key_events_str = "\n".join(key_events[-10:]) if key_events else "No events logged"
        
        # Generate review
        console.print("[dim]Generating comprehensive analysis...[/dim]\n")
        review = agent.weekly_review(
            weekly_stats=weekly_stats,
            goals_progress=goals_progress,
            key_events=key_events_str
        )
        
        console.print(Panel(
            Markdown(review),
            title="🤖 Weekly Analysis",
            border_style="blue",
            padding=(1, 2)
        ))
        
        console.print(f"\n[bold]⚡ Velocity:[/bold] {task_mgr.get_task_velocity(days=7):.1f} tasks/day\n")
        
        task_mgr.close()
        planner.close()
        
        console.print("[bold green]✨ Week reviewed! Ready for the next one.[/bold green]\n")
        
    except Exception as e:
        console.print(f"[bold red]❌ Error:[/bold red] {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_weekly_review()
