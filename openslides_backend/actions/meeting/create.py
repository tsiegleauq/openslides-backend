import fastjsonschema  # type: ignore

from ...models.meeting import Meeting
from ...shared.schema import schema_version
from ..actions import register_action
from ..generics import CreateAction

create_meeting_schema = fastjsonschema.compile(
    {
        "$schema": schema_version,
        "title": "New meetings schema",
        "description": "An array of new meetings.",
        "type": "array",
        "items": {
            "type": "object",
            "properties": Meeting().get_properties("committee_id", "name"),
            "required": ["committee_id", "name"],
            "additionalProperties": False,
        },
        "minItems": 1,
        "uniqueItems": True,
    }
)


@register_action("meeting.create")
class MeetingCreate(CreateAction):
    """
    Action to create meetings.
    """

    model = Meeting()
    schema = create_meeting_schema
