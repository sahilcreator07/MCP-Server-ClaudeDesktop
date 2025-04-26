from mcp.server.fastmcp import FastMCP
import json
import os

# Initialize MCP Server
mcp = FastMCP("Lead Scoring Assistant")

LEADS_FILE = os.path.join(os.path.dirname(__file__), "leads.json")

def ensure_file():
    if not os.path.exists(LEADS_FILE):
        with open(LEADS_FILE, "w") as f:
            json.dump([], f)

def load_leads():
    ensure_file()
    with open(LEADS_FILE, "r") as f:
        return json.load(f)

def save_leads(leads):
    with open(LEADS_FILE, "w") as f:
        json.dump(leads, f, indent=2)

@mcp.tool()
def add_lead(name: str, industry: str, company_size: int, budget: float, intent_score: int) -> str:
    """
    Add a new incoming lead to the system.

    Args:
        name (str): Company name
        industry (str): Industry category
        company_size (int): Number of employees
        budget (float): Available marketing/sales budget
        intent_score (int): Buyer intent score (0-100)

    Returns:
        str: Confirmation message
    """
    leads = load_leads()
    new_lead = {
        "id": f"lead_{len(leads)+1:03}",
        "name": name,
        "industry": industry,
        "company_size": company_size,
        "budget": budget,
        "intent_score": intent_score
    }
    leads.append(new_lead)
    save_leads(leads)
    return f"Lead {new_lead['id']} added successfully!"

@mcp.tool()
def score_lead(lead_id: str) -> str:
    """
    Score a lead based on company size, budget, and intent.

    Args:
        lead_id (str): Lead identifier

    Returns:
        str: Lead score and qualification result
    """
    leads = load_leads()
    lead = next((l for l in leads if l["id"] == lead_id), None)
    
    if not lead:
        return "Lead not found."

    # Simple scoring logic
    score = 0
    if lead["company_size"] > 100:
        score += 30
    if lead["budget"] > 50000:
        score += 40
    if lead["intent_score"] > 70:
        score += 30

    if score >= 80:
        qualification = "Hot Lead 🔥"
    elif score >= 50:
        qualification = "Warm Lead 🔥"
    else:
        qualification = "Cold Lead ❄️"

    return f"Lead {lead['name']} scored {score}/100 → {qualification}"

@mcp.resource("leads://recent")
def get_recent_leads() -> str:
    """
    Fetch a list of recent leads.

    Returns:
        str: Names of recent leads
    """
    leads = load_leads()
    if not leads:
        return "No leads available."
    
    return "\n".join(f"{lead['id']} - {lead['name']}" for lead in leads[-5:])

@mcp.prompt()
def lead_summary_prompt() -> str:
    """
    Create a prompt for summarizing all current leads and trends.

    Returns:
        str: A prompt for the AI to analyze lead trends
    """
    leads = load_leads()
    if not leads:
        return "There are no leads yet."

    return f"Here are the latest leads: {json.dumps(leads)}. Summarize trends and suggest next steps."
