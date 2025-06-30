import os
from typing import Dict, Any
from dotenv import load_dotenv

from features.task import Task
from utils.shared_mcp import Session
from utils.http_client import make_api_request, HTTPMethod
from utils.helpers import find_details_in_dct
from utils.constants import PLAN_PAGE_URL, GET_STRUCTURE_PARTIAL_URL, CREATE_PARTIAL_URL

load_dotenv() 
BASE_API_URL = os.getenv("BASE_API_URL")

class Project:
    def __init__(self):
        self.task = Task()

    async def get_structure_code(self):
        return await make_api_request(GET_STRUCTURE_PARTIAL_URL, method=HTTPMethod.GET)        
        
    async def create(self, work_name: str, work_description: str, father_code: str = "9"):
        json_response = await self.get_structure_code()
        structure_code = json_response.get("StructureCode")
        
        payload = json_response
        payload["Description"] = work_name
        payload["Parent"] = {
            "StructureCode": father_code
        }
        payload["Attributes"] = {
            "PE01": work_description
        }

        response = await make_api_request(CREATE_PARTIAL_URL, HTTPMethod.POST, body=payload)

        return structure_code
    
    async def create_work_and_wbs_in_pf(self, dct_work_structure: Dict[str, Any], work_name: str) -> Dict[str, str]:
        """Create a work from a project structure. This needs to be triggered if there is a work structure in the request"""
        processed_work = {}
        work_structure = dct_work_structure.get("items")
        Session.work_cache[work_name] = {}
        
        project_id = None
        for item in work_structure:
            name = item.get("name")
            description = item.get("description")
            parent_id = item.get("parent_id")
            work_id = item.get("id")
            if parent_id:
                parent_structure_code = await self.get_pf_parent_details(work_structure, processed_work, parent_id)
                structure_code = await self.task.create(name, description, parent_structure_code)
                processed_work[work_id] = (structure_code, name)
                Session.work_cache[work_name][name] = structure_code
            else:
                structure_code = await self.create(name, description)
                project_id = structure_code
                processed_work[work_id] = (structure_code, name)
                Session.work_cache[work_name]["self"] = structure_code            

        plan_page_url = PLAN_PAGE_URL.format(BASE_API_URL=BASE_API_URL, project_id=project_id)
        return {"type": "text", "data": f"Work created: {plan_page_url}"}

    @staticmethod
    async def get_pf_parent_details(work_structure, processed_work, parent_id):
        task = Task()
        processed_parent = processed_work.get(parent_id)
        if processed_work:
            parent_structure_code = processed_parent[0]
        else:
            parent_details_in_request = find_details_in_dct(work_structure, "id", parent_id)
            grand_parent_structure_code = Project.get_pf_parent_details(work_structure, processed_work, parent_details_in_request.get("id"))
            
            parent_structure_code = await task.create(parent_details_in_request.get("name"), parent_details_in_request.get("description"), grand_parent_structure_code)
            processed_work[parent_id] = (parent_structure_code, parent_details_in_request.get("name"))
        return parent_structure_code
        
