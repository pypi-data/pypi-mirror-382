from typing import Optional

from norman_objects.shared.invocations.invocation import Invocation
from norman_objects.shared.queries.query_constraints import QueryConstraints
from norman_objects.shared.security.sensitive import Sensitive
from pydantic import TypeAdapter

from norman_core.clients.http_client import HttpClient


class Invocations:
    @staticmethod
    async def get_invocations(http_client: HttpClient, token: Sensitive[str], constraints: Optional[QueryConstraints] = None):
        json = None
        if constraints is not None:
            json = constraints.model_dump(mode="json")

        response = await http_client.post("persist/invocations/get", token, json=json)
        return TypeAdapter(dict[str, Invocation]).validate_python(response)

    @staticmethod
    async def create_invocations(http_client: HttpClient, token: Sensitive[str], invocations: list[Invocation]):
        json = TypeAdapter(list[Invocation]).dump_python(invocations, mode="json")

        response = await http_client.post("persist/invocations", token, json=json)
        return TypeAdapter(list[Invocation]).validate_python(response)

    @staticmethod
    async def create_invocations_by_model_names(http_client: HttpClient, token: Sensitive[str], model_name_counter: dict[str, int]):
        response = await http_client.post("persist/invocations/by-name", token, json=model_name_counter)
        return TypeAdapter(list[Invocation]).validate_python(response)

    @staticmethod
    async def get_invocation_history(http_client: HttpClient, token: Sensitive[str], constraints: Optional[QueryConstraints] = None):
        json = None
        if constraints is not None:
            json = constraints.model_dump(mode="json")

        response = await http_client.post("persist/invocation/history/get", token, json=json)
        return TypeAdapter(dict[str, Invocation]).validate_python(response)
