from bs4 import BeautifulSoup


class AdobeFlashHandler(object):
    """
    This class contains leverage for Adobe Flash audio content.
    Inherit all concrete question parsers from it.
    """

    def __init__(self, soup: BeautifulSoup):

        # When soup contains flash content, we must get audio file name
        # and get rid of that block:
        if self._contains_flash(soup):
            self._audio_file_name = self._get_audio_file_name(soup)
            self._soup = self._remove_flash_object(soup)

        else:
            self._audio_file_name = ""
            self._soup = soup

    @property
    def audio_file_name(self):
        return self._audio_file_name

    @staticmethod
    def _remove_flash_object(soup: BeautifulSoup) -> BeautifulSoup:
        soup.itemBody.find("object").decompose()
        return soup

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