from typing import Optional

from norman_objects.shared.queries.query_constraints import QueryConstraints
from norman_objects.shared.security.sensitive import Sensitive
from norman_objects.shared.status_flags.status_flag import StatusFlag
from pydantic import TypeAdapter

from norman_core.clients.http_client import HttpClient


class ModelFlags:
    @staticmethod
    async def get_model_status_flags(http_client: HttpClient, token: Sensitive[str], constraints: Optional[QueryConstraints] = None):
        json = None
        if constraints is not None:
            json = constraints.model_dump(mode="json")

        response = await http_client.post("persist/model/flags/get", token, json=json)
        return TypeAdapter(dict[str, list[StatusFlag]]).validate_python(response)

    @staticmethod
    async def get_asset_status_flags(http_client: HttpClient, token: Sensitive[str], constraints: Optional[QueryConstraints] = None):
        json = None
        if constraints is not None:
            json = constraints.model_dump(mode="json")

        response = await http_client.post("persist/asset/flags/get", token, json=json)
        return TypeAdapter(dict[str, list[StatusFlag]]).validate_python(response)
