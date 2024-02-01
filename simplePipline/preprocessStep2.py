from pydantic import BaseModel, Field

from typing import List, Optional
from bs4 import BeautifulSoup, NavigableString


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


def clean_data(paragraphs, images, image_captions, tables):
    paragraphs = list(filter(None, paragraphs))
    images = list(filter(None, images))
    image_captions = list(filter(lambda x: x is not None and "$$$" not in x, image_captions))
    tables = list(filter(None, tables))
    return paragraphs, images, image_captions, tables


def process_table(table, image_index):
    headers = None
    row_span_buffer = [None] * 100  # Adjust the size if needed
    tables = []
    images = []
    image_captions = []
    all_text = ""

    for row in table.find_all('tr'):
        imgs = row.find_all('img')
        if imgs:
            ps = row.find_all('p')
            for img in imgs:
                images.append(img['src'])
                img.replace_with("$image_" + str(image_index) + "$")
                image_index += 1

            for p in ps:
                if p.text is not None:
                    image_captions.append(p.get_text().strip())
            for cell in row.find_all(['td', 'th']):
                all_text += cell.text.strip()
            continue

        if headers is None:
            headers = [' '.join(cell.stripped_strings) for cell in row.find_all('td')]
            continue

        row_data = []
        col_idx = 0
        for cell in row.find_all(['td', 'th']):
            row_span = cell.get('rowspan')
            if row_span:
                row_span_buffer[col_idx] = (cell.get_text().strip(), int(row_span) - 1)

            if row_span_buffer[col_idx]:
                row_data.append(row_span_buffer[col_idx][0])
                row_span_buffer[col_idx] = (row_span_buffer[col_idx][0], row_span_buffer[col_idx][1] - 1) if \
                    row_span_buffer[col_idx][1] > 0 else None
            else:
                row_data.append(cell.get_text().strip())

            col_idx += 1

        while len(row_data) < len(headers):
            row_data.insert(0, "")

        combined_rows = [f"{header}: {data}" for header, data in zip(headers, row_data)]
        table_text = ' | '.join(combined_rows)

        tables.append(table_text.strip())
        all_text += all_text

    return tables, images, image_captions, all_text, image_index


def table_text_return(table):
    table_text = ""
    headers = None
    row_span_buffer = [None] * 100  # Adjust the size if needed
    for row in table.find_all('tr'):
        if headers is None:
            headers = [' '.join(cell.stripped_strings) for cell in row.find_all('td')]
            continue

        row_data = []
        col_idx = 0
        for cell in row.find_all(['td', 'th']):
            row_span = cell.get('rowspan')
            if row_span:
                row_span_buffer[col_idx] = (cell.get_text().strip(), int(row_span) - 1)

            if row_span_buffer[col_idx]:
                row_data.append(row_span_buffer[col_idx][0])
                row_span_buffer[col_idx] = (row_span_buffer[col_idx][0], row_span_buffer[col_idx][1] - 1) if \
                    row_span_buffer[col_idx][1] > 0 else None
            else:
                row_data.append(cell.get_text().strip())

            col_idx += 1

        while len(row_data) < len(headers):
            row_data.insert(0, "")

        combined_rows = [f"{header}: {data}" for header, data in zip(headers, row_data)]
        table_text += ' | '.join(combined_rows)
    return table_text


def create_node_metadata_instances_associated(soup):
    instances = []
    title_text = ""
    all_text = ""
    image_index = 1
    paragraphs, images, image_captions, tables = [], [], [], []

    for title in soup.find_all('h2'):
        if title_text and (paragraphs or images or image_captions or tables):
            paragraphs, images, image_captions, tables = clean_data(paragraphs, images, image_captions, tables)
            instance = NodeMetadata(
                title=title_text,
                Paragraph=paragraphs,
                image=images,
                image_caption=image_captions,
                table=tables,
                all_text=title_text + " " + all_text
            )
            instances.append(instance)
            # Reset content for the next title
            paragraphs, images, image_captions, tables = [], [], [], []
            all_text = ""
            title_text = title.get_text().strip()
        else:
            # Merge titles if no content has been found yet
            if title_text:
                title_text += " | " + title.get_text().strip()
            else:
                title_text = title.get_text().strip()

        for sibling in title.find_next_siblings():
            if sibling.name == 'h2':
                if not (paragraphs or images or image_captions or tables):
                    title_text += " | " + sibling.get_text().strip()
                break
            elif sibling.name == 'p':
                text = sibling.get_text().strip()
                all_text += text
                if text.startswith(('Figura', 'figura')):
                    image_captions.append(text)
                else:
                    paragraphs.append(text)
                if sibling.find('img'):
                    images.append(sibling.find('img')['src'])
                    all_text += "$image_" + str(image_index) + "$"
                    image_index += 1
            elif sibling.name == 'table':
                table_data, table_images, table_image_captions, all_text_table, image_index = process_table(sibling,
                                                                                                            image_index)
                all_text += all_text_table
                tables.extend(table_data)
                images.extend(table_images)
                image_captions.extend(table_image_captions)

    if title_text and (paragraphs or images or image_captions or tables):
        paragraphs, images, image_captions, tables = clean_data(paragraphs, images, image_captions, tables)
        instance = NodeMetadata(
            title=title_text,
            Paragraph=paragraphs,
            image=images,
            image_caption=image_captions,
            table=tables,
            all_text=title_text + " " + all_text
        )
        instances.append(instance)

    return instances


if __name__ == '__main__':
    with open('./output.html', 'rb') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    preNodes = create_node_metadata_instances_associated(soup)
