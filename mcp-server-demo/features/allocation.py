import os
import json
from dotenv import load_dotenv

from utils.http_client import make_api_request, HTTPMethod

load_dotenv()
BASE_API_URL = os.getenv("BASE_API_URL")

def make_allocation_paylod(project_code, task_code, resource_code):

    return {
            "pplCode": project_code,
            "rowDto": {
                "Cells": [{
                        "ColumnId": "ALLO_PLANNING_CODE",
                        "CurrentValue": task_code,
                        "OriginalValue": task_code,
                        "Type": 8,
                        "DisplayText": "",
                        "IsReadOnly": False,
                        "LinkPath": ""
                    }, {
                        "ColumnId": "ALLO_RESOURCE_CODE",
                        "CurrentValue": resource_code,
                        "OriginalValue": resource_code,
                        "Type": 8,
                        "DisplayText": "",
                        "IsReadOnly": False,
                        "LinkPath": ""
                    }, {
                        "ColumnId": "ALLO_TEAM",
                        "CurrentValue": None,
                        "OriginalValue": None,
                        "Type": 7,
                        "DisplayText": None,
                        "IsReadOnly": False,
                        "LinkPath": ""
                    }, {
                        "ColumnId": "ALLO_RESERVE_CODE",
                        "CurrentValue": None,
                        "OriginalValue": None,
                        "Type": 8,
                        "DisplayText": "",
                        "IsReadOnly": False,
                        "LinkPath": ""
                    }, {
                        "ColumnId": "ALLO_PPL_CODE",
                        "CurrentValue": project_code,
                        "OriginalValue": project_code,
                        "Type": 8,
                        "DisplayText": "",
                        "IsReadOnly": False,
                        "LinkPath": ""
                    }, {
                        "ColumnId": "ALLO_CALENDAR_CODE",
                        "CurrentValue": "STANDARD",
                        "OriginalValue": "STANDARD",
                        "Type": 8,
                        "DisplayText": "",
                        "IsReadOnly": False,
                        "LinkPath": ""
                    }, {
                        "ColumnId": "ALLO_RESOURCE_DESCRIPTION",
                        "CurrentValue": "389|M Davis",
                        "OriginalValue": "389|M Davis",
                        "Type": 7,
                        "DisplayText": None,
                        "IsReadOnly": False,
                        "LinkPath": ""
                    }, {
                        "ColumnId": "ALLO_REQUIREMENT_DESCRIPTION",
                        "CurrentValue": None,
                        "OriginalValue": None,
                        "Type": 7,
                        "DisplayText": None,
                        "IsReadOnly": False,
                        "LinkPath": ""
                    }, {
                        "ColumnId": "ALLO_STATE",
                        "CurrentValue": "APR",
                        "OriginalValue": "APR",
                        "Type": 8,
                        "DisplayText": "",
                        "IsReadOnly": False,
                        "LinkPath": ""
                    },{
                        "ColumnId": "ALLO_START_DATE",
                        "CurrentValue": "2025-04-12T08:00:00",
                        "OriginalValue": "2025-04-12T08:00:00",
                        "Type": 10,
                        "DisplayText": None,
                        "IsReadOnly": False,
                        "LinkPath": ""
                    }, {
                        "ColumnId": "ALLO_FINISH_DATE",
                        "CurrentValue": "2025-09-19T17:00:00",
                        "OriginalValue": "2025-09-19T17:00:00",
                        "Type": 10,
                        "DisplayText": None,
                        "IsReadOnly": False,
                        "LinkPath": ""
                    }, {
                        "ColumnId": "ALLO_DURATION",
                        "CurrentValue": "8.00:00:00",
                        "OriginalValue": "2.00:00:00",
                        "Type": 1,
                        "DisplayText": "",
                        "IsReadOnly": False,
                        "LinkPath": ""
                    }, {
                        "ColumnId": "ALLO_REMAIN",
                        "CurrentValue": "8.00:00:00",
                        "OriginalValue": "2.00:00:00",
                        "Type": 2,
                        "DisplayText": "",
                        "IsReadOnly": False,
                        "LinkPath": ""
                    }, {
                        "ColumnId": "ALLO_PCT_UTILIZATION",
                        "CurrentValue": 1,
                        "OriginalValue": 1,
                        "Type": 6,
                        "DisplayText": None,
                        "IsReadOnly": False,
                        "LinkPath": ""
                    },  {
                        "ColumnId": "ALLO_LID",
                        "CurrentValue": None,
                        "OriginalValue": None,
                        "Type": 10,
                        "DisplayText": None,
                        "IsReadOnly": False,
                        "LinkPath": ""
                    }, {
                        "ColumnId": "ALLO_RESOURCE_NB",
                        "CurrentValue": 1,
                        "OriginalValue": 1,
                        "Type": 4,
                        "DisplayText": "0",
                        "IsReadOnly": False,
                        "LinkPath": ""
                    },  {
                        "ColumnId": "ALLO_WORKSET_CODE",
                        "CurrentValue": None,
                        "OriginalValue": None,
                        "Type": 4,
                        "DisplayText": "0",
                        "IsReadOnly": False,
                        "LinkPath": ""
                    }
                ]
            },
            "fatherRowDto": {
                "Cells": [{
                        "ColumnId": "PE_PLANNING_CODE",
                        "CurrentValue": task_code,
                        "OriginalValue": task_code,
                        "Type": 8,
                        "DisplayText": task_code,
                        "IsReadOnly": False,
                        "LinkPath": ""
                    }
                ]
            },
            "profileDto": {
                "ProfileId": f"ALO:{task_code}:{resource_code}:0",
                "CalendarId": "STANDARD",
                "StartTimes": ["2021-09-12T08:00:00", "2025-09-19T17:00:00"],
                "Heights": [1, 0]
            }
        }

class Allocation:
    async def create(self, project_code, task_code, resource_code):
        URL = f"/services/AllocateListAttributeServiceJson.svc/InsertRow?pt=PROJECT"
        payload = make_allocation_paylod(project_code, task_code, resource_code)

        json_resp = await make_api_request(URL, HTTPMethod.POST, body=payload)
        errors = json_resp.get('d', {}).get('Errors', [])
        if len(errors)!=0:
            return f"Something went wrong when creating the allocation - {errors}"
        return "Allocation created"