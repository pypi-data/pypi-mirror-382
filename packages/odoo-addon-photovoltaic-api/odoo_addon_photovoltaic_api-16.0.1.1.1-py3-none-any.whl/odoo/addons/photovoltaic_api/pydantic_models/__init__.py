from typing import Any
from odoo import fields, models
from pydantic import ConfigDict, BaseModel, model_validator


def false_to_none(obj, key, default=None):
    # from https://github.com/OCA/rest-framework/blob/15.0/pydantic/utils.py#L53
    res = getattr(obj, key)
    if isinstance(obj, models.BaseModel) and key in obj._fields:
        field = obj._fields[key]
        if res is False and field.type != "boolean":
            return None
        if field.type == "date" and not res:
            return None
        if field.type == "datetime":
            if not res:
                return None
            # Get the timestamp converted to the client's timezone.
            # This call also add the tzinfo into the datetime object
            return fields.Datetime.context_timestamp(obj, res)
        if field.type == "many2one" and not res:
            return None
        if field.type in ["one2many", "many2many"]:
            return list(res)
    return res


class OrmModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='before')
    @classmethod
    def false_to_none(cls, obj: Any) -> Any:
        if isinstance(obj, models.BaseModel):
            return {key: false_to_none(obj, key) for key in obj._fields}
        return obj
