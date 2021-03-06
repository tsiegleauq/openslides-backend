from ..shared.patterns import Collection
from . import fields
from .base import Model


class OrganisationField(fields.RequiredForeignKeyField):
    """
    Special field for foreign key to organisation model. We support only one
    organisation (with id 1) at the moment.
    """

    def get_schema(self) -> fields.Schema:
        schema = super().get_schema()
        schema["maximun"] = 1
        return schema


class Committee(Model):
    """
    Model for committees.

    There are the following reverse relation fields:
        TODO
    """

    # TODO: Add reverse relation fields to docstring.

    collection = Collection("committee")
    verbose_name = "committee"

    id = fields.IdField(description="The id of this committee.")
    organisation_id = OrganisationField(
        description="The id of the organisation of this committee.",
        to=Collection("organisation"),
        related_name="committee_ids",
    )
    name = fields.RequiredCharField(description="The name of this committee.")
