import sys
import json
from typing import Dict, Any, Optional
from pathlib import Path
from fastmcp.server.context import Context
import asyncio

PATH = Path(__file__).resolve().parents[1]
sys.path.append(str(PATH))

from utils.shared_mcp import mcp, Session
from features.project import Project
from dotenv import load_dotenv
from utils.helpers import is_string_json

load_dotenv()  # load environment variables from .env


@mcp.tool()
async def create_work(work_type: str, work_name: str, ctx: Context, PF_loginCert: Optional[str] = None)-> Dict[str, Any]:
    """Create a work from a project structure. This needs to be triggered if there is a work structure in the request
      Note:
        The parameter 'PF_loginCert' is not required from the user. It will be fetched internally by the system.
    """
    format_work = {
      "items": [
        {
          "id": "project-1",
          "type": "project",
          "name": work_name or work_type,
          "description": "A comprehensive system for managing and tracking car deliveries",
          "parent_id": None
        },
        {
          "id": "epic-1",
          "type": "epic",
          "name": "User Management",
          "description": "System for managing users, roles, and permissions",
          "parent_id": "project-1"
        },
        {
          "id": "story-1",
          "type": "story",
          "name": "Driver Management",
          "description": "Management of driver profiles and operations",
          "parent_id": "epic-1"
        }
      ]
    }
    Session.login_cert = PF_loginCert
    str_format_work = json.dumps(format_work)
    messages = [{"role": "user", "content": f"Create a project structure for the following work type: {work_type} and work name: {work_name}. If the name is not provided, use the work type as the name. Please return the project structure in json, in the following format \
            : {str_format_work}. I want the result to not be in nested json. I want to know the immediate parent of an item. Don't response with anything else. Only send the json response"}]
    messages = messages[0]["content"]
    try:
      ctx.fastmcp = mcp
      response = await ctx.sample(messages, model_preferences="claude-3-5-sonnet-20241022", max_tokens=4000)

      project = Project()
      first_result_content = response.text
      json_response = is_string_json(first_result_content)
      
      if json_response:
        json_result = json.loads(first_result_content)
        return await project.create_work_and_wbs_in_pf(json_result)
    except Exception as e:
      return {"type": "text", "data": f"Something Went Wrong when creating the work: {e}"}


# generated_payload = {"items": [{"id": "project-1", "type": "project", "name": "Food Delivery App", "description": "Mobile application for food ordering and delivery service", "parent_id": None}, {"id": "epic-1", "type": "epic", "name": "User App Development", "description": "Customer-facing mobile application development", "parent_id": "project-1"}, {"id": "epic-2", "type": "epic", "name": "Restaurant Portal", "description": "Web portal for restaurant partners to manage orders", "parent_id": "project-1"}, {"id": "epic-3", "type": "epic", "name": "Driver App Development", "description": "Mobile application for delivery drivers", "parent_id": "project-1"}, {"id": "epic-4", "type": "epic", "name": "Backend System", "description": "Server-side development and database management", "parent_id": "project-1"}, {"id": "story-1", "type": "story", "name": "User Registration", "description": "Implementation of user registration and authentication", "parent_id": "epic-1"}, {"id": "story-2", "type": "story", "name": "Restaurant Browse", "description": "Browse and search functionality for restaurants", "parent_id": "epic-1"}, {"id": "story-3", "type": "story", "name": "Order Management", "description": "Place, track, and manage food orders", "parent_id": "epic-1"}, {"id": "story-4", "type": "story", "name": "Restaurant Dashboard", "description": "Dashboard for restaurants to view and manage orders", "parent_id": "epic-2"}, {"id": "story-5", "type": "story", "name": "Menu Management", "description": "Tools for restaurants to manage their menu items", "parent_id": "epic-2"}, {"id": "story-6", "type": "story", "name": "Driver Registration", "description": "Driver onboarding and verification system", "parent_id": "epic-3"}, {"id": "story-7", "type": "story", "name": "Delivery Management", "description": "Accept and manage delivery assignments", "parent_id": "epic-3"}, {"id": "story-8", "type": "story", "name": "API Development", "description": "Development of REST APIs for all services", "parent_id": "epic-4"}, {"id": "story-9", "type": "story", "name": "Database Design", "description": "Design and implementation of database schema", "parent_id": "epic-4"}, {"id": "story-10", "type": "story", "name": "Payment Integration", "description": "Integration with payment gateway services", "parent_id": "epic-4"}]}
# asyncio.run(Project().create_work_and_wbs_in_pf(generated_payload))
# print("nothing")
