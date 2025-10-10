#!/usr/bin/env python3
"""
Evening Review Script
Interactive end-of-day review and reflection
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.core import BusinessAgent
from agent.tasks import TaskManager
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

console = Console()

def display_banner():
    """Display evening banner"""
    now = datetime.now()
    console.print()
    console.print(f"[bold magenta]{'='*70}[/bold magenta]")
    console.print(f"[bold magenta]  🌙 EVENING REVIEW - {now.strftime('%A, %B %d, %Y')}[/bold magenta]")
    console.print(f"[bold magenta]{'='*70}[/bold magenta]")
    console.print()

def run_evening_review():
    """Main function for evening review"""
    try:
        display_banner()
        
        # Initialize
        agent = BusinessAgent()
        task_mgr = TaskManager()
        
        # Get today's tasks
        today_tasks = task_mgr.get_tasks_for_today()
        completed_tasks = [t for t in today_tasks if t.status == 'completed']
        pending_tasks = [t for t in today_tasks if t.status in ['pending', 'in_progress', 'blocked']]
        
        # Display today's stats
        completion_rate = len(completed_tasks) / len(today_tasks) if today_tasks else 0
        
        console.print("[bold]📊 Today's Summary:[/bold]")
        console.print(f"  • Tasks completed: {len(completed_tasks)}/{len(today_tasks)} ({completion_rate:.0%})")
        console.print()
        
        if completed_tasks:
            console.print("[bold green]✅ Completed:[/bold green]")
            for task in completed_tasks:
                console.print(f"  • {task.title}")
            console.print()
        
        if pending_tasks:
            console.print("[bold yellow]⏳ Not Completed:[/bold yellow]")
            for task in pending_tasks[:5]:
                status_emoji = {"pending": "⏳", "in_progress": "🔄", "blocked": "🚧"}.get(task.status, "")
                console.print(f"  • {status_emoji} {task.title}")
            console.print()
        
        # Interactive reflection
        console.print("[bold cyan]📝 Daily Reflection[/bold cyan]")
        console.print("[dim]Take a moment to reflect on your day...[/dim]")
        console.print()
        
        wins = Prompt.ask("💪 [bold]What were your wins today?[/bold] (biggest accomplishments)")
        console.print()
        
        blockers = Prompt.ask("🚧 [bold]Any blockers or challenges?[/bold] (what slowed you down)")
        console.print()
        
        learnings = Prompt.ask("💡 [bold]What did you learn?[/bold] (insights or discoveries)")
        console.print()
        
        energy_choices = ["high", "medium", "low"]
        energy = Prompt.ask(
            "⚡ [bold]Energy level[/bold]",
            choices=energy_choices,
            default="medium"
        )
        console.print()
        
        mood_choices = ["great", "good", "okay", "tough"]
        mood = Prompt.ask(
            "😊 [bold]Overall mood[/bold]",
            choices=mood_choices,
            default="good"
        )
        console.print()
        
        # Log the day
        console.print("[dim]Saving your reflections...[/dim]")
        task_mgr.create_daily_log(
            date=datetime.now(),
            tasks_completed=len(completed_tasks),
            tasks_planned=len(today_tasks),
            wins=wins,
            blockers=blockers,
            learnings=learnings,
            energy_level=energy,
            mood=mood
        )
        
        # Get AI insights
        console.print("[dim]Analyzing your day...[/dim]")
        console.print()
        
        insights = agent.evening_review_analysis(
            completed_tasks=completed_tasks,
            planned_tasks=today_tasks,
            wins=wins,
            blockers=blockers,
            learnings=learnings,
            energy_level=energy
        )
        
        # Display insights
        console.print(Panel(
            Markdown(insights),
            title="🤖 AI Insights",
            border_style="green",
            padding=(1, 2)
        ))
        
        console.print()
        console.print("[bold cyan]💤 Great work today! Rest well and see you tomorrow morning.[/bold cyan]")
        console.print()
        
        # Cleanup
        task_mgr.close()
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Review cancelled. Your data has been saved.[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[bold red]❌ Error:[/bold red] {e}")
        import traceback
        console.print(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    run_evening_review()
