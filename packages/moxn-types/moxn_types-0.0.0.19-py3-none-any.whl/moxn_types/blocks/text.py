from typing import Literal

from pydantic import ConfigDict, Field, field_validator

from moxn_types.blocks.base import BaseContent, BlockType


class TextContentModel(BaseContent):
    block_type: Literal[BlockType.TEXT] = Field(
        default=BlockType.TEXT, alias="blockType"
    )
    text: str

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("block_type", mode="before")
    @classmethod
    def coerce_block_type(cls, v):
        """Coerce string values from API to BlockType enum."""
        if isinstance(v, str):
            return BlockType(v)
        return v
