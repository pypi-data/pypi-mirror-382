from typing import Any

from pydantic import BaseModel
from pydantic import ConfigDict

ExtractorResult = dict[str, Any] | list[Any]


class ExtractDataOutput(BaseModel):
    """
    Output data from the extract data component.

    Attributes:
        extracted_data: The extracted data
    """

    extracted_data: ExtractorResult | None
    model_config = ConfigDict(extra="allow")
