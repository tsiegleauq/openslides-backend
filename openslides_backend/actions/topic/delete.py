import fastjsonschema  # type: ignore

from ...models.topic import Topic
from ...shared.schema import schema_version
from ..actions import register_action
from ..generics import DeleteAction

delete_topic_schema = fastjsonschema.compile(
    {
        "$schema": schema_version,
        "title": "Delete topics schema",
        "description": "An array of topics to be deleted.",
        "type": "array",
        "items": {
            "type": "object",
            "properties": Topic().get_properties("id"),
            "required": ["id"],
            "additionalProperties": False,
        },
        "minItems": 1,
        "uniqueItems": True,
    }
)


@register_action("topic.delete")
class TopicDelete(DeleteAction):
    """
    Action to delete simple topics that can be shown in the agenda.
    """

    # TODO: Add protection against deletion without deleting agenda item.

    model = Topic()
    schema = delete_topic_schema
