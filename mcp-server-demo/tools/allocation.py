import sys
from typing import Optional

from pathlib import Path
PATH = Path(__file__).resolve().parents[1]
sys.path.append(str(PATH))

from utils.shared_mcp import mcp, Session, work_cache
from features.allocation import Allocation

@mcp.tool()
async def create_team_allocation(team_name: str, start_date: str, end_date: str) -> str:
    pass

@mcp.tool()
async def create_resource_allocation(resource_name: str, work_name:str, task_name:str, PF_loginCert: Optional[str] = None) -> str:
    """
    Create an Allocation under a task for a resource or assign a task to a resource
    """
    work_details = work_cache.get(work_name, {})
    # if not work_details:
    #     return {"type": "text", "data": "The Work details is not found. Are you sure you have created the work in the current session?"}
    task_id = work_details.get(task_name) or "20276"
    project_id = work_details.get('self') or "20276"

    # task_id = "20276"
    # project_id = "20276"
    resource_code = "20556"
    allocation = Allocation()
    Session.login_cert = PF_loginCert
    response = await allocation.create(project_id, task_id, resource_code)
    print(f"Allocation for resource {resource_name} created uner the work: {project_id}")
    return {"type": "reload", "data": response}


# if __name__ == '__main__':
#     import asyncio
    
#     asyncio.run(create_resource_allocation("dummy", "S8Tu9NsLXKvp043hJagwNv1vlhE_iB_qIRpUXghRA"))
