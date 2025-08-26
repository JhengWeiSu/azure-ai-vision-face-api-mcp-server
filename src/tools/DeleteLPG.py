import os
from typing import Annotated

from azure.ai.vision.face import FaceAdministrationClient
from azure.core.credentials import AzureKeyCredential
from pydantic import Field

from .utils._enums import DeleteLPGConfig


def delete_large_person_group(
    group_uuid: Annotated[str, Field(description=DeleteLPGConfig.ARGS_GROUP_UUID)],
):
    ENDPOINT = os.getenv("AZURE_FACE_ENDPOINT")
    KEY = os.getenv("AZURE_FACE_API_KEY")

    with FaceAdministrationClient(
        endpoint=ENDPOINT,
        credential=AzureKeyCredential(KEY),
        headers={"X-MS-AZSDK-Telemetry": "sample=mcp-face-reco-delete-lpg"},
    ) as face_admin_client:
        try:
            face_admin_client.large_person_group.delete(
                large_person_group_id=group_uuid
            )
            return f"Deleted large person group with UUID: {group_uuid} successfully."
        except Exception as e:
            if "ResourceNotFound" in str(e) or "not found" in str(e).lower():
                return f"Large person group with UUID: {group_uuid} does not exist."
            else:
                raise
