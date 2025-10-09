from typing import Optional

from norman_objects.shared.notifications.notification import Notification
from norman_objects.shared.queries.query_constraints import QueryConstraints
from norman_objects.shared.security.sensitive import Sensitive
from pydantic import TypeAdapter

from norman_core.clients.http_client import HttpClient


class Notifications:
    @staticmethod
    async def get_notifications(http_client: HttpClient, token: Sensitive[str], constraints: Optional[QueryConstraints] = None):
        json = None
        if constraints is not None:
            json = constraints.model_dump(mode="json")

        response = await http_client.post("persist/notifications/get", token, json=json)
        return TypeAdapter(list[Notification]).validate_python(response)
