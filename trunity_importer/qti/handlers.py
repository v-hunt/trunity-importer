from bs4 import BeautifulSoup


class AdobeFlashHandler(object):
    """
    This class contains leverage for Adobe Flash audio content.
    Inherit all concrete question parsers from it.
    """

    def __init__(self, soup: BeautifulSoup):

        self._soup = soup

        # When soup contains flash content, we should get audio file name
        if self._contains_flash(soup):
            self._audio_file_name = self._get_audio_file_name(soup)

        else:
            self._audio_file_name = ""

    @property
    def audio_file_name(self):
        return self._audio_file_name

    @property
    def soup(self):
        return self._soup

    def replace_flash_tag(self, markup: str):
        object_tag = self._soup.itemBody.find("object")
        markup_soup = BeautifulSoup(markup, 'lxml')

        # 'lxml' adds redundant <body> and <html> tags. We remove them:
        markup_soup.html.unwrap()
        markup_soup.body.unwrap()

        object_tag.replace_with(markup_soup)

    @staticmethod
    def _contains_flash(soup: BeautifulSoup) -> bool:
        """
        Check if soup has flash content inside.
        """
        return bool(soup.itemBody.find("object"))

    @staticmethod
    def _get_audio_file_name(soup: BeautifulSoup) -> str:
        src_string = soup.itemBody.find("object").find("embed")['src']
        return src_string.split('=/')[-1]