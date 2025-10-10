from typing import Literal
from typing import Union

from pydantic import BaseModel
from pydantic import Field

# class BasicSchemaDict(TypedDict):
#     type: Literal["number", "boolean", "array", "object", "string"]
#     description: NotRequired[str | None]


# class StringSchemaDict(BasicSchemaDict):
#     type: Literal["string"]
#     enum: NotRequired[list[str] | None]
#     maxLength: NotRequired[int | None]
#     minLength: NotRequired[int | None]
#     pattern: NotRequired[str | None]


# class NumberSchemaDict(BasicSchemaDict):
#     type: Literal["number", "integer"]
#     multipleOf: NotRequired[float | None]
#     maximum: NotRequired[float | None]
#     exclusiveMaximum: NotRequired[float | None]
#     minimum: NotRequired[float | None]
#     exclusiveMinimum: NotRequired[float | None]


# class BooleanSchemaDict(BasicSchemaDict):
#     type: Literal["boolean"]
#     description: NotRequired[str]


# class ArraySchemaDict(BasicSchemaDict):
#     type: Literal["array"]
#     items: Union["JsonSchema_Dict", list["JsonSchema_Dict"]]
#     maxItems: NotRequired[int | None]
#     minItems: NotRequired[int | None]
#     uniqueItems: NotRequired[bool | None]


# class ObjectSchemaDict(BasicSchemaDict):
#     type: Literal["object"]
#     properties: dict[str, "JsonSchema_Dict"]
#     required: NotRequired[list[str] | None]
#     maxProperties: NotRequired[int | None]
#     minProperties: NotRequired[int | None]


# JsonSchema_Dict = (
#     NumberSchemaDict | StringSchemaDict | BooleanSchemaDict | ArraySchemaDict | ObjectSchemaDict | BasicSchemaDict
# )


class BasicSchema(BaseModel):
    type: Literal["number", "boolean", "array", "object", "string"]
    description: str | None = None


class StringSchema(BasicSchema):
    """Schema for string values - internal validation model"""

    type: Literal["string"] = "string"
    enum: list[str] | None = None
    maxLength: int | None = Field(None, description="Maximum length of the string")
    minLength: int | None = Field(None, description="Minimum length of the string")
    pattern: str | None = None


class NumberSchema(BasicSchema):
    """Schema for numeric values - internal validation model"""

    type: Literal["number", "integer"]
    multipleOf: float | None = Field(None, description="Value must be a multiple of this number")
    maximum: float | None = Field(None, description="Maximum value")
    exclusiveMaximum: float | None = Field(None, description="Exclusive maximum value")
    minimum: float | None = Field(None, description="Minimum value")
    exclusiveMinimum: float | None = Field(None, description="Exclusive minimum value")


class BooleanSchema(BasicSchema):
    """Schema for boolean values - internal validation model"""

    type: Literal["boolean"] = "boolean"


class ArraySchema(BasicSchema):
    """Schema for array values - internal validation model"""

    type: Literal["array"] = "array"
    items: Union["JsonSchema", list["JsonSchema"]] | None = None
    maxItems: int | None = Field(None, description="Maximum number of items in the array")
    minItems: int | None = Field(None, description="Minimum number of items in the array")
    uniqueItems: bool | None = Field(None, description="Whether all items in the array must be unique")


class ObjectSchema(BasicSchema):
    """Schema for object values - internal validation model"""

    type: Literal["object"] = "object"
    properties: dict[str, "JsonSchema"] | None = None
    required: list[str] | None = None
    maxProperties: int | None = Field(None, description="Maximum number of properties in the object")
    minProperties: int | None = Field(None, description="Minimum number of properties in the object")


JsonSchema = StringSchema | NumberSchema | BooleanSchema | ArraySchema | ObjectSchema | BasicSchema


ArraySchema.model_rebuild()
ObjectSchema.model_rebuild()
