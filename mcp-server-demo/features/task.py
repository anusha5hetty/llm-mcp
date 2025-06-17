import json
from utils.http_client import make_api_request, HTTPMethod
from utils.constants import GET_STRUCTURE_URL, CREATE_URL


class Task:
    async def get_structure_code(self, father_code: str):
        return await make_api_request(GET_STRUCTURE_URL.format(father_code=father_code), HTTPMethod.GET)
        
    async def create(self, task_name: str, task_description: str, father_code: str):
        json_response = await self.get_structure_code(father_code)
        structure_code = json_response.get("StructureCode")
        
        payload = json_response
        payload["Description"] = task_name

        payload["Attributes"] = {
            "PE01": task_description
        }

        response = await make_api_request(CREATE_URL, HTTPMethod.POST, body=payload)
        return structure_code