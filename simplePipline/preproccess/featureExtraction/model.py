from typing import Optional, List

from pydantic import BaseModel, Field

from simplePipline.utils.logger import Logger


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

    def img_placeholder_to_description(self, img_descriptor):
        for descriptor in img_descriptor:

            if descriptor["index"].startswith('$image_'):
                self.all_text = self.all_text.replace(descriptor["index"], descriptor["description"])
            elif descriptor["index"][0].isdigit():
                self.all_text = self.alltext.replace(f"$image_{descriptor["index"]}$", descriptor["description"])
            else:
                Logger("invalid index format for image placeholder").get_logger().warning(descriptor)
                self.all_text += descriptor["description"]

    def img_info_to_html(self, img_descriptor):
        html_content = ""
        for index, img in enumerate(self.image):
            try:
                html_content += f'''
                                    <div class="image-container">
                                        <img src="{img}" alt="Image {index}">
                                            <div class="description">
                                                <pre>{{
                                                    'index': '{img_descriptor[index]["index"]}',
                                                    'description': '{img_descriptor[index]["description"]}'
                                                     }}</pre>
                                                 </div>
                                             </div>
                                    '''
            except:
                Logger("invalid index html").get_logger().warning("invalid index missed image")
                html_content += f'''
                                    <div class="image-container">
                                        <img src="{img}" alt="Image {index}">
                                        <div class="description">
                                            <pre>{{'index': 'N/A', 'description': 'No description available'}}</pre>
                                        </div>
                                    </div>
                                '''

            return html_content
