import os
from typing import Annotated

from azure.ai.vision.face import FaceAdministrationClient
from azure.core.credentials import AzureKeyCredential
from pydantic import Field

from .utils._enums import DeletePersonFromLPGConfig, DeleteFaceFromLPGConfig

_LAST_WARNING: dict[str, bool] = {}


def delete_person_from_group(
    person_id: Annotated[str, Field(DeletePersonFromLPGConfig.ARGS_PERSON_ID)],
    group_uuid: Annotated[
        str, Field(description=DeletePersonFromLPGConfig.ARGS_GROUP_UUID)
    ],
    confirm: Annotated[
        bool, Field(description=DeletePersonFromLPGConfig.ARGS_CONFIRM)
    ] = False,
):
    if not _LAST_WARNING.get(f"{group_uuid}:{person_id}"):
        _LAST_WARNING[f"{group_uuid}:{person_id}"] = True
        return {
            "status": "needs_confirmation",
            "message": DeletePersonFromLPGConfig.DOUBLE_CONFIRM_WARNING.format(
                person_id=person_id, group_uuid=group_uuid
            )
            + " Call again with user confirmation.",
        }

    if not confirm:
        return {
            "message": DeletePersonFromLPGConfig.DOUBLE_CONFIRM_WARNING.format(
                person_id=person_id, group_uuid=group_uuid
            )
        }
    ENDPOINT = os.getenv("AZURE_FACE_ENDPOINT")
    KEY = os.getenv("AZURE_FACE_API_KEY")
    output_list = []
    with FaceAdministrationClient(
        endpoint=ENDPOINT,
        credential=AzureKeyCredential(KEY),
        headers={"X-MS-AZSDK-Telemetry": "sample=mcp-face-reco-delete"},
    ) as face_admin_client:
        try:
            face_admin_client.large_person_group.delete_person(
                large_person_group_id=group_uuid, person_id=person_id
            )
            output_list.append(
                f"Deleted person with ID: {person_id} from group: {group_uuid}"
            )
        except Exception as e:
            output_list.append(
                f"Failed to delete person with ID: {person_id} from group: {group_uuid}. Error: {str(e)}"
            )
    return "\n".join(output_list)


def delete_face_from_group(
    face_id: Annotated[str, Field(DeleteFaceFromLPGConfig.ARGS_FACE_ID)],
    person_id: Annotated[str, Field(DeleteFaceFromLPGConfig.ARGS_PERSON_ID)],
    group_uuid: Annotated[
        str, Field(description=DeleteFaceFromLPGConfig.ARGS_GROUP_UUID)
    ],
    confirm: Annotated[
        bool, Field(description=DeleteFaceFromLPGConfig.ARGS_CONFIRM)
    ] = False,
):
    if not _LAST_WARNING.get(f"{group_uuid}:{person_id}:{face_id}"):
        _LAST_WARNING[f"{group_uuid}:{person_id}:{face_id}"] = True
        return {
            "status": "needs_confirmation",
            "message": DeleteFaceFromLPGConfig.DOUBLE_CONFIRM_WARNING.format(
                face_id=face_id, person_id=person_id, group_uuid=group_uuid
            )
            + " Call again with user confirmation.",
        }

    if not confirm:
        return {
            "message": DeleteFaceFromLPGConfig.DOUBLE_CONFIRM_WARNING.format(
                face_id=face_id, person_id=person_id, group_uuid=group_uuid
            )
        }
    ENDPOINT = os.getenv("AZURE_FACE_ENDPOINT")
    KEY = os.getenv("AZURE_FACE_API_KEY")
    output_list = []
    with FaceAdministrationClient(
        endpoint=ENDPOINT,
        credential=AzureKeyCredential(KEY),
        headers={"X-MS-AZSDK-Telemetry": "sample=mcp-face-reco-delete"},
    ) as face_admin_client:
        try:
            face_admin_client.large_person_group.delete_face(
                large_person_group_id=group_uuid,
                person_id=person_id,
                persisted_face_id=face_id,
            )
            output_list.append(
                f"Deleted face with ID: {face_id} from person ID: {person_id} in group: {group_uuid}"
            )
        except Exception as e:
            output_list.append(
                f"Failed to delete face with ID: {face_id} from person ID: {person_id} in group: {group_uuid}. Error: {str(e)}"
            )
    return "\n".join(output_list)
