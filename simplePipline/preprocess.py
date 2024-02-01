import os

from bs4 import BeautifulSoup, NavigableString
import mammoth
from PIL import Image
from io import BytesIO
import base64


class HTMLPreprocessor:
    def __init__(self, docx_file_path, html_file_path, max_image_width=150) -> object:
        self.docx_file_path = docx_file_path
        self.html_file_path = html_file_path
        self.max_image_width = max_image_width

    def conver_docx_bytes_io_to_html(self, fd):
        result = mammoth.convert_to_html(fd)
        pass
    def convert_docx_to_html(self):
        with open(self.docx_file_path, "rb") as docx_file:
            result = mammoth.convert_to_html(docx_file)
            html = result.value
            messages = result.messages
            print(messages)
        return html

    def write_html_to_file(self, html_content):
        with open(self.html_file_path, "w", encoding="utf-8") as html_file:
            html_file.write(html_content)

    def replace_headers_with_h2(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')

        # Iterate through all header tags and replace them with h2
        for header_tag in ['h1', 'h3', 'h4', 'h5', 'h6']:
            for tag in soup.find_all(header_tag):
                new_tag = soup.new_tag('h2')
                new_tag.string = tag.string
                tag.replace_with(new_tag)

        return str(soup)

    def remove_quotation_marks(self, html_content):
        return html_content.replace('“', '').replace('”', '').replace('’', "'")

    def set_html_encoding_to_utf8(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')

        meta_charset = soup.find('meta', {'charset': True})
        if meta_charset:
            meta_charset['charset'] = 'utf-8'
        else:
            new_meta_charset = soup.new_tag('meta', charset='utf-8')
            head = soup.head or soup.new_tag('head')
            soup.insert(0, head)
            head.insert(0, new_meta_charset)

        return str(soup)

    def remove_html_after_phrase(self, html_content, phrase):
        soup = BeautifulSoup(html_content, 'html.parser')
        remove_tag = soup.find(string=phrase)
        if remove_tag:
            for sibling in remove_tag.find_all_next():
                sibling.decompose()
            remove_tag_parent = remove_tag.parent
            remove_tag_parent.decompose()

        return str(soup)

    def preprocess_html(self, html_content):
        html_content = self.remove_quotation_marks(html_content)
        html_content = self.set_html_encoding_to_utf8(html_content)
        html_content = self.remove_empty_elements(html_content)
        html_content = self.remove_empty_table_rows(html_content)
        html_content = self.process_html_images(html_content)
        html_content = self.remove_empty_tables(html_content)
        html_content = self.remove_useless_tags(html_content, 'em')
        html_content = self.remove_useless_tags(html_content, 'a')
        html_content = self.remove_useless_tags(html_content, 'u')
        html_content = self.remove_useless_tags(html_content, 'br')
        html_content = self.convert_p_strong_to_h2(html_content)
        html_content = self.replace_headers_with_h2(html_content)
        html_content = self.remove_content_before_next_header(html_content,
                                                              [
                                                                  'Indice Generale',
                                                                  'INDICE DELLE FIGURE',
                                                                  'Indice figure',
                                                                  'Indice delle tabelle'])
        html_content = self.remove_html_after_phrase(html_content, "Allegati")
        return html_content

    def remove_empty_elements(self, html_content):
        soup = BeautifulSoup(html_content, 'lxml')
        self_closing_tags = ['br', 'hr', 'img', 'input', 'link', 'meta', 'area', 'base', 'col', 'command', 'embed',
                             'keygen', 'param', 'source', 'track', 'wbr']
        for tag in list(soup.find_all()):
            if tag.name not in self_closing_tags and self.is_empty_element(tag, self_closing_tags):
                tag.decompose()
        return str(soup)

    def is_empty_element(self, element, self_closing_tags):
        if isinstance(element, NavigableString):
            return not element.strip()
        if any(child.name in self_closing_tags for child in element.children):
            return False
        return all(self.is_empty_element(child, self_closing_tags) for child in element.children)

    def remove_empty_table_rows(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        for td in soup.find_all('td'):
            if not td.get_text(strip=True) and not td.find():
                td.decompose()
        for tr in soup.find_all('tr'):
            if not tr.find('td'):
                tr.decompose()
        return str(soup)

    def process_html_images(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        for img_tag in soup.find_all("img"):
            if img_tag["src"].startswith("data:image"):
                header, encoded = img_tag["src"].split(",", 1)
                if header == "data:image/x-emf;base64":
                    img_tag.decompose()
                    continue
                img_data = base64.b64decode(encoded)
                resized_encoded = self.resize_image(img_data, self.max_image_width)
                img_tag["src"] = header + "," + resized_encoded
        return str(soup)

    def resize_image(self, image_data, max_width):
        with Image.open(BytesIO(image_data)) as img:
            ratio = max_width / img.width
            new_size = (max_width, int(img.height * ratio))
            resized_img = img.resize(new_size, Image.Resampling.LANCZOS)
            output_buffer = BytesIO()
            resized_img.save(output_buffer, format=img.format)
            return base64.b64encode(output_buffer.getvalue()).decode()

    def remove_useless_tags(self, html_content, tag_to_remove):
        soup = BeautifulSoup(html_content, 'html.parser')
        for tag in soup.find_all(tag_to_remove):
            tag.unwrap()
        return str(soup)

    def remove_empty_tables(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        for table in soup.find_all('table'):
            if not table.find(['td', 'th']):
                table.decompose()
        return str(soup)

    def convert_p_strong_to_h2(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        for p in soup.find_all('p'):
            if p.strong and len(p.contents) == 1:
                new_tag = soup.new_tag('h2')
                for content in p.strong.contents:
                    if isinstance(content, NavigableString):
                        new_tag.append(content)
                    else:
                        new_tag.append(content.extract())
                p.replace_with(new_tag)
        return str(soup)

    def unwrap_p_in_td(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')

        for td in soup.find_all('td'):
            p_tag = td.find('p')
            if p_tag:
                p_tag.unwrap()

        return str(soup)

    def remove_content_before_next_header(self, html_content, phrases):
        soup = BeautifulSoup(html_content, 'html.parser')
        for phrase in phrases:
            lower_phrase = phrase.lower()
            phrase_tag = soup.find(string=lambda text: lower_phrase in text.lower() if text else False)
            if phrase_tag:
                # Find the next header tag after the phrase tag
                next_header = phrase_tag.find_next(['h2'])
                hi = next_header.text.lower().find(phrase.lower())
                while next_header.text.lower().find(phrase.lower()) != -1:
                    next_header = next_header.find_next(['h2'])

                # self.write_html_to_file(next_header)
                if next_header:
                    # Remove all content before the next header
                    current_element = next_header.find_previous_sibling()
                    while current_element:
                        current_element.decompose()
                        current_element = next_header.find_previous_sibling()

        return str(soup)

    def process_docx_to_html(self):
        html_content = self.convert_docx_to_html()
        processed_html = self.preprocess_html(html_content)
        self.write_html_to_file(processed_html)
        return processed_html


def list_docx_files(directory):
    return [file for file in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, file)) and file.endswith('.docx')]


# files = list_docx_files('./src/problemFiles/convertionProblem/')
# for index, file in enumerate(files):
#     print(file)
#     preprocessor = HTMLPreprocessor("./src/problemFiles/convertionProblem/"+file, str(index)+".html" )
#     html_content = preprocessor.process_docx_to_html()
# preprocessor = HTMLPreprocessor(
#     "./data/AFU - ISY_Motore di ricerca - v1.0.1.docx",
#     "out.html")
# html_content = preprocessor.process_docx_to_html()
