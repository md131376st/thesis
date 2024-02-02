from typing import Optional, List

from pydantic import BaseModel, Field


class NodeMetadata(BaseModel):
    """Node metadata."""

    title: str = Field(..., description="title of the text.")
    Paragraph: Optional[List[str]] = Field(None, description="Paragraph entities of the text.")
    image: Optional[List[str]] = Field(None, description="The Image about this text chunk.")
    image_caption: Optional[List[str]] = Field(None, description="Image description about this text chunk.")
    table: Optional[List[str]] = Field(None, description="Table related to the text chunk.")
    all_text: str = Optional[Field(..., description="Concatinated text with image placeHolder")]

    def __str__(self):
        Paragraph = ' '.join(self.Paragraph[:2])
        table = ' '.join(self.table)
        images = self.image if self.image else []
        captions = self.image_caption if self.image_caption else []


        return (self.title + '\n' + Paragraph +
                '\n' + "| table content: " + table)
