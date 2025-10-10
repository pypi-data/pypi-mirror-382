import anthropic
import os
from datetime import datetime
from agent.models import ResearchItem, get_session

class ResearchAgent:
    def __init__(self):
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"
        self.session = get_session()
    
    def research_topic(self, topic, business_goal, depth="standard"):
        """Research a topic using Claude's web search capability"""
        
        depth_guidance = {
            "quick": "Use 1-2 web searches to get a quick overview",
            "standard": "Use 3-5 web searches to get comprehensive information",
            "deep": "Use 5-10 web searches for thorough, multi-angle research"
        }
        
        prompt = f"""Research this topic for my business:

TOPIC: {topic}

BUSINESS GOAL: {business_goal}

RESEARCH DEPTH: {depth_guidance.get(depth, depth_guidance['standard'])}

Please research this topic and provide:

1. **Key Findings** - Most important insights (3-5 bullet points)
2. **Trends** - Current trends or patterns
3. **Opportunities** - How this could benefit my business
4. **Risks/Challenges** - What to watch out for
5. **Action Items** - 2-3 specific next steps I should take
6. **Sources** - List the key sources you used

Use web search to gather current information. Be thorough and practical."""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            research_text = message.content[0].text
            
            # Save to database
            research_item = ResearchItem(
                title=topic,
                summary=research_text,
                category="general",
                date_found=datetime.now(),
                raw_data={"prompt": prompt, "depth": depth}
            )
            self.session.add(research_item)
            self.session.commit()
            
            return {
                'research_id': research_item.id,
                'topic': topic,
                'findings': research_text,
                'date': datetime.now()
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'topic': topic
            }
    
    def research_competitors(self, business_domain, your_offering):
        """Research competitive landscape"""
        
        prompt = f"""Research the competitive landscape for my business:

MY BUSINESS DOMAIN: {business_domain}
MY OFFERING: {your_offering}

Use web search to find and analyze:

1. **Top 5-7 Competitors**
   - Company name
   - What they offer
   - Their key strengths
   - Pricing approach (if public)
   - Market position

2. **Competitive Gaps**
   - What are competitors NOT doing well?
   - Underserved customer needs
   - Opportunities for differentiation

3. **Market Trends**
   - Where is this market heading?
   - Emerging technologies or approaches
   - Changing customer expectations

4. **Strategic Recommendations**
   - How should we position ourselves?
   - What should we focus on?
   - What should we avoid?

Be specific and cite sources where possible."""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=5000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            research_text = message.content[0].text
            
            # Save to database
            research_item = ResearchItem(
                title=f"Competitive Analysis: {business_domain}",
                summary=research_text,
                category="competitor",
                date_found=datetime.now(),
                raw_data={
                    "domain": business_domain,
                    "offering": your_offering
                }
            )
            self.session.add(research_item)
            self.session.commit()
            
            return {
                'research_id': research_item.id,
                'findings': research_text,
                'date': datetime.now()
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_research_history(self, category=None, limit=10):
        """Retrieve past research"""
        query = self.session.query(ResearchItem)
        
        if category:
            query = query.filter(ResearchItem.category == category)
        
        items = query.order_by(ResearchItem.date_found.desc()).limit(limit).all()
        return [item.to_dict() for item in items]
    
    def weekly_intelligence_report(self, business_focus_areas):
        """Generate a weekly intelligence digest"""
        from datetime import timedelta
        week_ago = datetime.now() - timedelta(days=7)
        
        recent_research = self.session.query(ResearchItem).filter(
            ResearchItem.date_found >= week_ago
        ).all()
        
        research_summary = "\n".join([
            f"- {r.title} ({r.category})"
            for r in recent_research[:10]
        ])
        
        prompt = f"""Create a weekly intelligence report for my business:

FOCUS AREAS: {', '.join(business_focus_areas)}

RECENT RESEARCH CONDUCTED:
{research_summary or 'No research this week'}

Generate a concise intelligence brief covering:

1. **Key Insights** - Top 3 takeaways from this week
2. **Trending Topics** - What's gaining attention in our space
3. **Competitive Intelligence** - Notable competitor moves
4. **Opportunities** - What we should act on
5. **Threats** - What we should watch
6. **Next Week's Research Priorities** - What to investigate next

Keep it scannable and actionable."""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=3000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return message.content[0].text
            
        except Exception as e:
            return f"Error generating intelligence report: {e}"
    
    def close(self):
        """Close database session"""
        self.session.close()
