from typing import Optional

from norman_objects.shared.queries.query_constraints import QueryConstraints
from norman_objects.shared.security.sensitive import Sensitive
from norman_objects.shared.status_flags.status_flag import StatusFlag
from pydantic import TypeAdapter

from norman_core.clients.http_client import HttpClient


class InvocationFlags:
    @staticmethod
    async def get_invocation_status_flags(http_client: HttpClient, token: Sensitive[str], constraints: Optional[QueryConstraints] = None):
        json = None
        if constraints is not None:
            json=constraints.model_dump(mode="json")

        response = await http_client.post("/persist/invocation/flags/get", token, json=json)
        return TypeAdapter(dict[str, list[StatusFlag]]).validate_python(response)

    @staticmethod
    async def get_input_status_flags(http_client: HttpClient, token: Sensitive[str], constraints: Optional[QueryConstraints] = None):
        json = None
        if constraints is not None:
            json=constraints.model_dump(mode="json")

        response = await http_client.post("/persist/input/flags/get", token, json=json)
        return TypeAdapter(dict[str, list[StatusFlag]]).validate_python(response)

    @staticmethod
    async def get_output_status_flags(http_client: HttpClient, token: Sensitive[str], constraints: Optional[QueryConstraints] = None):
        json = None
        if constraints is not None:
            json=constraints.model_dump(mode="json")

        response = await http_client.post("/persist/output/flags/get", token, json=json)
        return TypeAdapter(dict[str, list[StatusFlag]]).validate_python(response)
