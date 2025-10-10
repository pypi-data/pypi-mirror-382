#!/usr/bin/env python3
"""Business Agent CLI Tool"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import click
from agent.tasks import TaskManager
from agent.planner import BusinessPlanner
from agent.research import ResearchAgent
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
console = Console()

@click.group()
def cli():
    """Business Agent CLI - Manage your business from the command line"""
    pass

# TASK COMMANDS
@cli.group()
def task():
    """Manage tasks"""
    pass

@task.command()
@click.argument('title')
@click.option('--description', '-d', help='Task description')
@click.option('--priority', '-p', type=int, default=3)
@click.option('--category', '-c', help='Task category')
@click.option('--hours', '-h', type=float, help='Estimated hours')
def add(title, description, priority, category, hours):
    """Add a new task"""
    task_mgr = TaskManager()
    task = task_mgr.create_task(
        title=title,
        description=description,
        priority=priority,
        category=category,
        estimated_hours=hours
    )
    console.print(f"[green]✓[/green] Task created: {task.title} (ID: {task.id})")
    task_mgr.close()

@task.command()
def list():
    """List all pending tasks"""
    task_mgr = TaskManager()
    tasks = task_mgr.get_tasks_for_today()
    
    if not tasks:
        console.print("[yellow]No pending tasks[/yellow]")
        return
    
    table = Table(title="📋 Your Tasks", show_header=True, header_style="bold cyan")
    table.add_column("ID", style="dim")
    table.add_column("Priority", justify="center")
    table.add_column("Title")
    table.add_column("Category", style="cyan")
    
    for task in tasks:
        priority_str = "🔴" if task.priority == 1 else "🟡" if task.priority == 3 else "🟢"
        table.add_row(
            str(task.id),
            priority_str,
            task.title[:50],
            task.category or "-"
        )
    
    console.print(table)
    task_mgr.close()

@task.command()
@click.argument('task_id', type=int)
def complete(task_id):
    """Mark a task as complete"""
    task_mgr = TaskManager()
    task = task_mgr.complete_task(task_id)
    if task:
        console.print(f"[green]✓[/green] Completed: {task.title}")
    else:
        console.print(f"[red]✗[/red] Task {task_id} not found")
    task_mgr.close()

# GOAL COMMANDS
@cli.group()
def goal():
    """Manage goals"""
    pass

@goal.command()
@click.argument('title')
@click.option('--description', '-d', help='Goal description')
@click.option('--horizon', '-h', type=click.Choice(['weekly', 'monthly', 'quarterly', 'yearly']), default='monthly')
@click.option('--target', '-t', help='Target date (YYYY-MM-DD)')
def add(title, description, horizon, target):
    """Add a new goal"""
    planner = BusinessPlanner()
    target_date = None
    if target:
        target_date = datetime.strptime(target, '%Y-%m-%d')
    
    goal = planner.create_goal(
        title=title,
        description=description,
        horizon=horizon,
        target_date=target_date
    )
    console.print(f"[green]✓[/green] Goal created: {goal.title} (ID: {goal.id})")
    planner.close()

@goal.command()
def list():
    """List all active goals"""
    planner = BusinessPlanner()
    goals = planner.get_active_goals()
    
    if not goals:
        console.print("[yellow]No active goals[/yellow]")
        return
    
    table = Table(title="🎯 Your Goals", show_header=True, header_style="bold cyan")
    table.add_column("ID", style="dim")
    table.add_column("Title")
    table.add_column("Horizon", style="cyan")
    table.add_column("Progress", justify="right")
    
    for goal in goals:
        progress_bar = "█" * int(goal.progress_percentage / 10) + "░" * (10 - int(goal.progress_percentage / 10))
        table.add_row(
            str(goal.id),
            goal.title[:40],
            goal.horizon,
            f"{progress_bar} {goal.progress_percentage:.0f}%"
        )
    
    console.print(table)
    planner.close()

@goal.command()
@click.argument('goal_id', type=int)
def breakdown(goal_id):
    """Break down a goal into tasks using AI"""
    planner = BusinessPlanner()
    console.print(f"[cyan]Breaking down goal {goal_id}...[/cyan]")
    tasks = planner.break_down_goal(goal_id)
    
    if tasks:
        console.print(f"[green]✓[/green] Created {len(tasks)} tasks")
        for task in tasks:
            console.print(f"  • {task.title}")
    else:
        console.print("[red]✗[/red] Failed to break down goal")
    planner.close()

# RESEARCH COMMANDS
@cli.group()
def research():
    """Conduct research"""
    pass

@research.command()
@click.argument('topic')
@click.option('--goal', '-g', help='Business goal')
def topic(topic, goal):
    """Research a topic"""
    researcher = ResearchAgent()
    console.print(f"[cyan]Researching: {topic}...[/cyan]\n")
    
    result = researcher.research_topic(
        topic=topic,
        business_goal=goal or "General research",
        depth="standard"
    )
    
    if 'error' in result:
        console.print(f"[red]✗ Error:[/red] {result['error']}")
    else:
        console.print(Panel(
            Markdown(result['findings']),
            title=f"🔍 Research: {topic}",
            border_style="blue"
        ))
        console.print(f"\n[dim]Saved as research ID: {result['research_id']}[/dim]")
    researcher.close()

@research.command()
@click.argument('domain')
@click.argument('offering')
def competitors(domain, offering):
    """Research competitors"""
    researcher = ResearchAgent()
    console.print(f"[cyan]Analyzing competitive landscape...[/cyan]\n")
    
    result = researcher.research_competitors(domain, offering)
    
    if 'error' in result:
        console.print(f"[red]✗ Error:[/red] {result['error']}")
    else:
        console.print(Panel(
            Markdown(result['findings']),
            title="🏆 Competitive Analysis",
            border_style="blue"
        ))
    researcher.close()

# STATS COMMAND
@cli.command()
def stats():
    """Show statistics"""
    task_mgr = TaskManager()
    weekly_stats = task_mgr.get_weekly_stats()
    velocity = task_mgr.get_task_velocity()
    today_tasks = task_mgr.get_tasks_for_today()
    
    console.print("\n[bold cyan]📊 Your Statistics[/bold cyan]\n")
    console.print("[bold]This Week:[/bold]")
    console.print(f"  • Tasks Completed: {weekly_stats['total_tasks_completed']}")
    console.print(f"  • Completion Rate: {weekly_stats['average_completion_rate']:.0%}")
    console.print(f"\n[bold]Velocity:[/bold] {velocity:.1f} tasks/day")
    console.print(f"\n[bold]Today:[/bold] {len(today_tasks)} tasks scheduled\n")
    task_mgr.close()

if __name__ == "__main__":
    cli()
