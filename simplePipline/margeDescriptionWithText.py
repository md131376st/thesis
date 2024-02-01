import re
from simplePipline.preprocessStep2 import table_text_return


def margeDescriptionWithText(soup, soup1):
    images = soup.find_all("img")
    images1 = soup1.find_all("img")
    for image in images:
        img = next((img for img in images1 if img['src'] == image['src']), None)
        if img is not None:
            pattern = r"'description'\s*:\s*'((?:[^'\\]|\\.|'(?!'\n\}))+)'"
            text = img.next_sibling.next_sibling.text
            match = re.search(pattern, text, re.DOTALL)
            if match:
                description = match.group(1)
                image.replace_with(description)
            else:
                continue
    tlbs = soup.find_all("table")
    for tlb in tlbs:
        text = table_text_return(tlb)
        tlb.replace_with(text)
    return soup.text, str(soup), soup


if __name__ == '__main__':
    pass
