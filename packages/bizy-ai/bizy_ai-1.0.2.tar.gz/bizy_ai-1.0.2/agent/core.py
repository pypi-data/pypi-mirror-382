import anthropic
import os
from datetime import datetime, timedelta
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
import json

console = Console()

class BusinessAgent:
    def __init__(self):
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"
    
    def morning_briefing(self, tasks_today, yesterday_summary, business_context, goals=None):
        """Generate morning briefing with AI"""
        
        tasks_str = self._format_tasks_for_prompt(tasks_today)
        goals_str = self._format_goals_for_prompt(goals) if goals else "No active goals set"
        
        prompt = f"""You are my business execution assistant. Generate an energizing and focused morning briefing for today.

TODAY'S DATE: {datetime.now().strftime('%A, %B %d, %Y')}

YESTERDAY'S SUMMARY:
Tasks Completed: {yesterday_summary.get('tasks_completed', 0)} of {yesterday_summary.get('tasks_due', 0)}
Completion Rate: {yesterday_summary.get('completion_rate', 0):.0%}

ACTIVE GOALS:
{goals_str}

TODAY'S SCHEDULED TASKS:
{tasks_str}

Create a morning briefing with these sections:

## 🌅 Good Morning!
Brief motivational opener (1-2 sentences)

## 📊 Yesterday's Recap
Quick summary of what was accomplished and what it means

## 🎯 Today's Mission
Top 3 priorities for today with estimated time for each
Explain why each matters for the bigger picture

## ⚠️ Watch Out For
Any potential blockers, risks, or important deadlines

## 💡 Pro Tip
One specific, actionable suggestion to move the business forward today

Keep it concise, energizing, and actionable. Use markdown formatting."""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            return f"Error generating briefing: {e}"
    
    def evening_review_analysis(self, completed_tasks, planned_tasks, wins, blockers, learnings, energy_level):
        """Analyze the day's work and provide insights"""
        
        completed_str = "\n".join([f"- {t.title} ({t.category or 'uncategorized'})" for t in completed_tasks])
        planned_str = "\n".join([f"- {t.title} ({t.status})" for t in planned_tasks])
        
        completion_rate = len(completed_tasks) / len(planned_tasks) if planned_tasks else 0
        
        prompt = f"""Analyze today's business execution and provide insights:

DATE: {datetime.now().strftime('%A, %B %d, %Y')}

COMPLETION RATE: {completion_rate:.0%} ({len(completed_tasks)}/{len(planned_tasks)} tasks)

COMPLETED TASKS:
{completed_str or 'None'}

PLANNED BUT NOT COMPLETED:
{planned_str or 'All completed!'}

USER'S REFLECTION:
- Wins: {wins or 'Not specified'}
- Blockers: {blockers or 'None mentioned'}
- Learnings: {learnings or 'Not specified'}
- Energy Level: {energy_level or 'Not specified'}

Provide:

## 📈 Day Analysis
Honest assessment of today's productivity (2-3 sentences)

## 🎯 What Worked
Highlight positive patterns or wins

## 🔄 What to Adjust
Constructive suggestions for improvement

## 🌟 Momentum Builder
One specific thing to carry into tomorrow

Be supportive but honest. Keep it concise."""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            return f"Error generating analysis: {e}"
    
    def weekly_review(self, weekly_stats, goals_progress, key_events):
        """Generate comprehensive weekly review"""
        
        prompt = f"""Generate a comprehensive weekly review for my business:

WEEK ENDING: {datetime.now().strftime('%B %d, %Y')}

STATS:
- Total Tasks Completed: {weekly_stats.get('total_tasks_completed', 0)}
- Total Tasks Planned: {weekly_stats.get('total_tasks_planned', 0)}
- Average Completion Rate: {weekly_stats.get('average_completion_rate', 0):.0%}
- Days Logged: {weekly_stats.get('days_logged', 0)}

GOAL PROGRESS:
{goals_progress}

KEY EVENTS/NOTES:
{key_events or 'None logged'}

Create a weekly review with:

## 📊 Week in Review
High-level summary of the week's productivity

## 🎯 Goal Progress
Assessment of progress toward key goals

## 📈 Trends & Patterns
What patterns do you notice? (velocity, energy, blockers)

## 🏆 Wins & Achievements
Celebrate what went well

## 🔧 Areas for Improvement
What could be better next week?

## 📋 Next Week's Focus
Top 3 priorities for the coming week

## 💡 Strategic Insight
One key insight or recommendation for the business

Be thorough but scannable. Use bullet points where appropriate."""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=3000,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            return f"Error generating weekly review: {e}"
    
    # Helper methods
    
    def _format_tasks_for_prompt(self, tasks):
        """Format tasks for inclusion in prompts"""
        if not tasks:
            return "No tasks scheduled"
        
        formatted = []
        for task in tasks[:10]:  # Limit to top 10
            due_str = task.due_date.strftime('%m/%d') if task.due_date else 'No due date'
            est_str = f"{task.estimated_hours}h" if task.estimated_hours else "?"
            formatted.append(
                f"- [{task.priority}] {task.title} (Est: {est_str}, Due: {due_str})"
            )
        
        return "\n".join(formatted)
    
    def _format_goals_for_prompt(self, goals):
        """Format goals for inclusion in prompts"""
        if not goals:
            return "No active goals"
        
        formatted = []
        for goal in goals[:5]:  # Top 5 goals
            target_str = goal.target_date.strftime('%m/%d/%Y') if goal.target_date else 'No target'
            formatted.append(
                f"- [{goal.horizon.upper()}] {goal.title} - {goal.progress_percentage:.0f}% (Target: {target_str})"
            )
        
        return "\n".join(formatted)
