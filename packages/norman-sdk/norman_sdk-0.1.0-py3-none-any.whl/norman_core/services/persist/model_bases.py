from typing import Optional

from norman_objects.shared.models.model_base import ModelBase
from norman_objects.shared.requests.get_models_request import GetModelsRequest
from norman_objects.shared.security.sensitive import Sensitive
from pydantic import TypeAdapter

from norman_core.clients.http_client import HttpClient


class ModelBases:
    @staticmethod
    async def get_model_bases(http_client: HttpClient, token: Sensitive[str], request: Optional[GetModelsRequest] = None):
        if request is None:
            request = GetModelsRequest(constraints=None, finished_models=True)
        json = request.model_dump(mode="json")

        response = await http_client.post("persist/models/bases/get", token, json=json)
        return TypeAdapter(dict[str, ModelBase]).validate_python(response)
