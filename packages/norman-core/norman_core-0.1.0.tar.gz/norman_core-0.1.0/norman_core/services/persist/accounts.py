from typing import Optional

from norman_objects.shared.accounts.account import Account
from norman_objects.shared.queries.query_constraints import QueryConstraints
from norman_objects.shared.security.sensitive import Sensitive
from pydantic import TypeAdapter

from norman_core.clients.http_client import HttpClient


class Accounts:
    @staticmethod
    async def get_accounts(http_client: HttpClient, token: Sensitive[str], constraints: Optional[QueryConstraints] = None):
        json = None
        if constraints is not None:
            json = constraints.model_dump(mode="json")

        response = await http_client.post("persist/accounts/get", token, json=json)
        return TypeAdapter(dict[str, Account]).validate_python(response)

    @staticmethod
    async def create_accounts(http_client: HttpClient, token: Sensitive[str], accounts: list[Account]):
        json = TypeAdapter(list[Account]).dump_python(accounts, mode="json")

        response = await http_client.post("persist/accounts", token, json=json)
        return TypeAdapter(list[Account]).validate_python(response)

    @staticmethod
    async def replace_accounts(http_client: HttpClient, token: Sensitive[str], accounts: list[Account]):
        json = None
        if accounts is not None:
            json = TypeAdapter(list[Account]).dump_python(accounts, mode="json")

        modified_entity_count: int = await http_client.put("persist/accounts", token, json=json)
        return modified_entity_count

    @staticmethod
    async def update_accounts(http_client: HttpClient, token: Sensitive[str], account: Account.UpdateSchema, constraints: Optional[QueryConstraints] = None):
        parsed_constraints = None
        if constraints is not None:
            parsed_constraints = constraints.model_dump(mode="json")

        json = {
            "account": account.model_dump(mode="json"),
            "constraints": parsed_constraints
        }

        affected_entities_count: int = await http_client.patch("persist/accounts", token, json=json)
        return affected_entities_count

    @staticmethod
    async def delete_accounts(http_client: HttpClient, token: Sensitive[str], constraints: QueryConstraints):
        json = constraints.model_dump(mode="json")

        affected_entities_count: int = await http_client.delete("persist/accounts", token, json=json)
        return affected_entities_count
