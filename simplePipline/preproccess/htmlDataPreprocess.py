import base64
from io import BytesIO

from PIL import Image
from bs4 import BeautifulSoup, NavigableString

from simplePipline.preproccess.dataProccess import DataPreprocess


class HTMLDataPreprocess(DataPreprocess):
    def __init__(self, loglevel, html_content, max_image_width=150):
        DataPreprocess.__init__(self, loglevel, html_content)
        self.logger.debug("par processing html content")
        self.soup = BeautifulSoup(html_content, "html.parser")
        self.max_image_width = max_image_width

    def correct_error(self):
        self.remove_quotation_marks()
        self.set_html_encoding_to_utf8()
        self.content = str(self.soup)

    def extra_steps(self):

        self.remove_content_before_next_header(
            [
                'Indice Generale',
                'INDICE DELLE FIGURE',
                'Indice figure',
                'Indice delle tabelle'])
        self.remove_html_after_phrase("Allegati")
        self.content = str(self.soup)

    def remove_unwanted_data(self):
        self.remove_empty_elements()
        self.remove_empty_table_rows()
        self.process_html_images()
        self.remove_empty_tables()
        unwanted_tags = ['em', 'a', 'u', 'br']
        for tag in unwanted_tags:
            self.remove_useless_tags(tag)
        self.content = str(self.soup)

    def structure_data(self):
        self.convert_p_strong_to_h2()
        self.replace_headers_with_h2()
        self.content = str(self.soup)
        pass

    def replace_headers_with_h2(self):
        # Iterate through all header tags and replace them with h2
        for header_tag in ['h1', 'h3', 'h4', 'h5', 'h6']:
            for tag in self.soup.find_all(header_tag):
                new_tag = self.soup.new_tag('h2')
                new_tag.string = tag.text if tag.text is not None else ''
                tag.replace_with(new_tag)

    def remove_quotation_marks(self):
        self.content = self.content.replace('“', '').replace('”', '').replace('’', "'")

    def set_html_encoding_to_utf8(self):
        self.soup = BeautifulSoup(self.content, 'html.parser')

        meta_charset = self.soup.find('meta', {'charset': True})
        if meta_charset:
            meta_charset['charset'] = 'utf-8'
        else:
            new_meta_charset = self.soup.new_tag('meta', charset='utf-8')
            head = self.soup.head or self.soup.new_tag('head')
            self.soup.insert(0, head)
            head.insert(0, new_meta_charset)

    def remove_html_after_phrase(self, phrase):
        remove_tag = self.soup.find(string=phrase)
        if remove_tag:
            for sibling in remove_tag.find_all_next():
                sibling.decompose()
            remove_tag_parent = remove_tag.parent
            remove_tag_parent.decompose()

    def remove_empty_elements(self):
        self.soup = BeautifulSoup(self.content, 'lxml')
        self_closing_tags = ['br', 'hr', 'img', 'input', 'link', 'meta', 'area', 'base', 'col', 'command', 'embed',
                             'keygen', 'param', 'source', 'track', 'wbr']
        for tag in list(self.soup.find_all()):
            if tag.name not in self_closing_tags and self.is_empty_element(tag, self_closing_tags):
                tag.decompose()

    def is_empty_element(self, element, self_closing_tags):
        if isinstance(element, NavigableString):
            return not element.strip()
        if any(child.name in self_closing_tags for child in element.children):
            return False
        return all(self.is_empty_element(child, self_closing_tags) for child in element.children)

    def remove_empty_table_rows(self):
        self.soup = BeautifulSoup(self.content, 'html.parser')
        for td in self.soup.find_all('td'):
            if not td.get_text(strip=True) and not td.find():
                td.decompose()
        for tr in self.soup.find_all('tr'):
            if not tr.find('td'):
                tr.decompose()

    def process_html_images(self):
        for img_tag in self.soup.find_all("img"):
            if img_tag["src"].startswith("data:image"):
                header, encoded = img_tag["src"].split(",", 1)
                if header == "data:image/x-emf;base64":
                    img_tag.decompose()
                    continue
                img_data = base64.b64decode(encoded)
                resized_encoded = self.resize_image(img_data, self.max_image_width)
                img_tag["src"] = header + "," + resized_encoded

    def resize_image(self, image_data, max_width):
        with Image.open(BytesIO(image_data)) as img:
            ratio = max_width / img.width
            new_size = (max_width, int(img.height * ratio))
            resized_img = img.resize(new_size, Image.Resampling.LANCZOS)
            output_buffer = BytesIO()
            resized_img.save(output_buffer, format=img.format)
            return base64.b64encode(output_buffer.getvalue()).decode()

    def remove_useless_tags(self, tag_to_remove):
        for tag in self.soup.find_all(tag_to_remove):
            tag.unwrap()

    def remove_empty_tables(self):
        for table in self.soup.find_all('table'):
            if not table.find(['td', 'th']):
                table.decompose()

    def convert_p_strong_to_h2(self):
        for p in self.soup.find_all('p'):
            if p.strong and len(p.contents) == 1:
                new_tag = self.soup.new_tag('h2')
                for content in p.strong.contents:
                    if isinstance(content, NavigableString):
                        new_tag.append(content)
                    else:
                        new_tag.append(content.extract())
                p.replace_with(new_tag)

    def remove_content_before_next_header(self, phrases):

        for phrase in phrases:
            lower_phrase = phrase.lower()
            phrase_tag = self.soup.find(string=lambda text: lower_phrase in text.lower() if text else False)
            if phrase_tag:
                # Find the next header tag after the phrase tag
                next_header = phrase_tag.find_next(['h2'])
                while next_header.text.lower().find(phrase.lower()) != -1:
                    next_header = next_header.find_next(['h2'])

                # self.write_html_to_file(next_header)
                if next_header:
                    # Remove all content before the next header
                    current_element = next_header.find_previous_sibling()
                    while current_element:
                        current_element.decompose()
                        current_element = next_header.find_previous_sibling()
