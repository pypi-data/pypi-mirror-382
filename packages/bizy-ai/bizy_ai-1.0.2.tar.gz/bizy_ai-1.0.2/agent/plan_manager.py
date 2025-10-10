#!/usr/bin/env python3
"""
Business Plan Management Script
Review and update business plans, goals, and tasks
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.core import BusinessAgent
from agent.planner import BusinessPlanner
from agent.tasks import TaskManager
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
console = Console()

def review_business_plan():
    """Display comprehensive business plan review"""
    try:
        console.print()
        console.print(f"[bold blue]{'='*70}[/bold blue]")
        console.print(f"[bold blue]  📋 BUSINESS PLAN REVIEW - {datetime.now().strftime('%B %d, %Y')}[/bold blue]")
        console.print(f"[bold blue]{'='*70}[/bold blue]")
        console.print()

        planner = BusinessPlanner()
        task_mgr = TaskManager()
        agent = BusinessAgent()

        # Get active business plan
        plan = planner.get_active_business_plan()

        if not plan:
            console.print("[yellow]⚠️  No active business plan found.[/yellow]")
            console.print("\nWould you like to create one? Use: [cyan]bizy plan create[/cyan]")
            return

        # Display business plan
        console.print("[bold]📊 Current Business Plan[/bold]")
        console.print(f"[dim]Version: {plan.version} | Created: {plan.created_at.strftime('%Y-%m-%d')}[/dim]\n")

        plan_info = f"""
**Vision:** {plan.vision}

**Mission:** {plan.mission}

**Value Proposition:** {plan.value_proposition}

**Target Market:** {plan.target_market}

**Revenue Model:** {plan.revenue_model}
"""
        console.print(Panel(Markdown(plan_info), title="Business Plan", border_style="blue"))

        # Get goals
        console.print("\n[bold]🎯 Goals Overview[/bold]\n")
        all_goals = planner.get_active_goals()

        if all_goals:
            goals_table = Table(show_header=True, header_style="bold cyan")
            goals_table.add_column("Horizon")
            goals_table.add_column("Goal")
            goals_table.add_column("Progress", justify="right")
            goals_table.add_column("Target Date")

            for goal in all_goals[:10]:
                progress_bar = "█" * int(goal.progress_percentage / 10) + "░" * (10 - int(goal.progress_percentage / 10))
                target = goal.target_date.strftime('%Y-%m-%d') if goal.target_date else "Not set"
                goals_table.add_row(
                    goal.horizon.upper(),
                    goal.title[:40],
                    f"{progress_bar} {goal.progress_percentage:.0f}%",
                    target
                )

            console.print(goals_table)
        else:
            console.print("[yellow]No active goals found.[/yellow]")

        # Get task summary
        console.print("\n[bold]📋 Task Summary[/bold]\n")
        weekly_stats = task_mgr.get_weekly_stats()
        today_tasks = task_mgr.get_tasks_for_today()
        overdue = task_mgr.get_overdue_tasks()

        console.print(f"  • This Week: {weekly_stats['total_tasks_completed']}/{weekly_stats['total_tasks_planned']} completed ({weekly_stats['average_completion_rate']:.0%})")
        console.print(f"  • Today: {len(today_tasks)} tasks scheduled")
        console.print(f"  • Overdue: {len(overdue)} tasks")

        # AI Analysis
        console.print("\n[dim]Generating AI analysis...[/dim]")

        goals_summary = "\n".join([
            f"- [{g.horizon.upper()}] {g.title}: {g.progress_percentage:.0f}% complete"
            for g in all_goals[:5]
        ]) if all_goals else "No active goals"

        analysis_prompt = f"""Analyze this business plan and provide strategic insights:

BUSINESS PLAN:
- Vision: {plan.vision}
- Mission: {plan.mission}
- Value Proposition: {plan.value_proposition}

GOALS PROGRESS:
{goals_summary}

EXECUTION METRICS:
- Weekly Completion Rate: {weekly_stats['average_completion_rate']:.0%}
- Tasks Overdue: {len(overdue)}

Provide:
1. **Plan-Goal Alignment** - Are the goals aligned with the business plan?
2. **Execution Health** - Is the execution on track?
3. **Recommended Adjustments** - What should be updated or changed?
4. **Next Strategic Moves** - What are the top 3 priorities?

Be concise and actionable."""

        analysis = agent.client.messages.create(
            model=agent.model,
            max_tokens=2000,
            messages=[{"role": "user", "content": analysis_prompt}]
        ).content[0].text

        console.print(Panel(
            Markdown(analysis),
            title="🤖 AI Strategic Analysis",
            border_style="blue",
            padding=(1, 2)
        ))

        console.print()
        planner.close()
        task_mgr.close()

    except Exception as e:
        console.print(f"[bold red]❌ Error reviewing plan:[/bold red] {e}")
        import traceback
        console.print(traceback.format_exc())

def create_business_plan():
    """Interactive business plan creation"""
    try:
        console.print()
        console.print(f"[bold green]{'='*70}[/bold green]")
        console.print(f"[bold green]  📝 CREATE BUSINESS PLAN[/bold green]")
        console.print(f"[bold green]{'='*70}[/bold green]")
        console.print()

        console.print("[cyan]Let's create your business plan. This will guide all your goals and tasks.[/cyan]\n")

        vision = Prompt.ask("🔭 [bold]What is your vision?[/bold] (Where are you going?)")
        mission = Prompt.ask("🎯 [bold]What is your mission?[/bold] (How will you get there?)")
        value_prop = Prompt.ask("💎 [bold]What is your value proposition?[/bold] (Why you over competitors?)")
        target_market = Prompt.ask("👥 [bold]Who is your target market?[/bold]")
        revenue_model = Prompt.ask("💰 [bold]What is your revenue model?[/bold] (How will you make money?)")

        version = Prompt.ask("📌 [bold]Version number?[/bold]", default="1.0")

        console.print("\n[dim]Creating business plan...[/dim]")

        planner = BusinessPlanner()
        plan = planner.create_business_plan(
            vision=vision,
            mission=mission,
            value_proposition=value_prop,
            target_market=target_market,
            revenue_model=revenue_model,
            version=version
        )

        console.print(Panel(
            f"[green]✅ Business Plan v{plan.version} Created Successfully![/green]\n\n"
            f"This plan will now guide your goal setting and task management.",
            title="Success",
            border_style="green"
        ))

        # Ask if they want to create goals
        if Confirm.ask("\n💡 Would you like to create your first goal now?"):
            console.print("\n[cyan]Tip: Start with a yearly goal, then break it down into smaller goals.[/cyan]\n")

            goal_title = Prompt.ask("🎯 [bold]Goal title[/bold]")
            goal_desc = Prompt.ask("📝 [bold]Goal description[/bold]")
            horizon = Prompt.ask(
                "⏰ [bold]Time horizon[/bold]",
                choices=["weekly", "monthly", "quarterly", "yearly"],
                default="yearly"
            )

            # Calculate target date
            days_map = {"weekly": 7, "monthly": 30, "quarterly": 90, "yearly": 365}
            target_date = datetime.now() + timedelta(days=days_map[horizon])

            goal = planner.create_goal(
                title=goal_title,
                description=goal_desc,
                horizon=horizon,
                target_date=target_date
            )

            console.print(f"\n[green]✅ Goal created (ID: {goal.id})[/green]")

            if Confirm.ask("\n🤖 Would you like AI to break this goal into tasks?"):
                console.print("\n[dim]AI is breaking down your goal into actionable tasks...[/dim]")
                tasks = planner.break_down_goal(goal.id)

                if tasks:
                    console.print(f"\n[green]✅ Created {len(tasks)} tasks:[/green]")
                    for i, task in enumerate(tasks[:5], 1):
                        console.print(f"  {i}. {task.title}")
                    if len(tasks) > 5:
                        console.print(f"  ... and {len(tasks) - 5} more")

        planner.close()
        console.print()

    except Exception as e:
        console.print(f"[bold red]❌ Error creating plan:[/bold red] {e}")
        import traceback
        console.print(traceback.format_exc())

def update_business_plan():
    """Update existing business plan"""
    try:
        console.print()
        console.print(f"[bold yellow]{'='*70}[/bold yellow]")
        console.print(f"[bold yellow]  ✏️  UPDATE BUSINESS PLAN[/bold yellow]")
        console.print(f"[bold yellow]{'='*70}[/bold yellow]")
        console.print()

        planner = BusinessPlanner()
        plan = planner.get_active_business_plan()

        if not plan:
            console.print("[yellow]⚠️  No active business plan found.[/yellow]")
            console.print("\nCreate one with: [cyan]bizy plan create[/cyan]")
            return

        console.print(f"[bold]Current Plan (v{plan.version})[/bold]\n")
        console.print(f"Vision: {plan.vision}")
        console.print(f"Mission: {plan.mission}")
        console.print(f"Value Proposition: {plan.value_proposition}")
        console.print(f"Target Market: {plan.target_market}")
        console.print(f"Revenue Model: {plan.revenue_model}")
        console.print()

        console.print("[cyan]What would you like to update? (Press Enter to skip)[/cyan]\n")

        vision = Prompt.ask("🔭 [bold]Vision[/bold]", default=plan.vision)
        mission = Prompt.ask("🎯 [bold]Mission[/bold]", default=plan.mission)
        value_prop = Prompt.ask("💎 [bold]Value Proposition[/bold]", default=plan.value_proposition)
        target_market = Prompt.ask("👥 [bold]Target Market[/bold]", default=plan.target_market)
        revenue_model = Prompt.ask("💰 [bold]Revenue Model[/bold]", default=plan.revenue_model)

        # Create new version
        version_parts = plan.version.split('.')
        new_minor = int(version_parts[1]) + 1 if len(version_parts) > 1 else 1
        new_version = f"{version_parts[0]}.{new_minor}"

        new_version = Prompt.ask("📌 [bold]New version number[/bold]", default=new_version)

        if Confirm.ask("\n💾 Save this as a new version of your business plan?"):
            new_plan = planner.create_business_plan(
                vision=vision,
                mission=mission,
                value_proposition=value_prop,
                target_market=target_market,
                revenue_model=revenue_model,
                version=new_version
            )

            console.print(Panel(
                f"[green]✅ Business Plan Updated to v{new_plan.version}[/green]\n\n"
                f"The previous version (v{plan.version}) has been archived.",
                title="Success",
                border_style="green"
            ))

        planner.close()
        console.print()

    except Exception as e:
        console.print(f"[bold red]❌ Error updating plan:[/bold red] {e}")
        import traceback
        console.print(traceback.format_exc())

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "review":
            review_business_plan()
        elif command == "create":
            create_business_plan()
        elif command == "update":
            update_business_plan()
        else:
            console.print(f"[red]Unknown command: {command}[/red]")
    else:
        review_business_plan()
