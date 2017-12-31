import os
from zipfile import ZipFile

from bs4 import BeautifulSoup
from trunity_3_client import FilesClient

from trunity_importer.sda.parser import MultipleChoice

QUESTION_TEXT_TEMPLATE = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),  # current file dir
    'templates/question.html'
)


class QuestionHandler:

    def __init__(self, files_client: FilesClient,
                 zip_file: ZipFile):
        self._files_client = files_client
        self._zip_file = zip_file

        with open(QUESTION_TEXT_TEMPLATE) as fo:
            self._question_text_templ = fo.read()

    def _upload_images(self, html: str):
        """
        Upload all images to Trunity and replace src attributes with new urls.
        """
        def fix_image_src(image_path: str) -> str:
            return image_path.replace("\\", "/") + ".gif"

        soup = BeautifulSoup(html, "lxml")
        for img in soup.find_all("img"):
            image_src = fix_image_src(img['src'])
            file_obj = self._zip_file.open(image_src)
            cdn_file_url = self._files_client.list.post(file_obj=file_obj)
            img['src'] = cdn_file_url

            # add some padding for nicer look:
            img["style"] = "padding: 5px;"

        return soup.decode()

    def _upload_mp3_file(self, name: str) -> str:
        src = 'media/' + name
        file_obj = self._zip_file.open(src)
        return self._files_client.list.post(file_obj=file_obj)

    def _upload_images_in_question(self, question: MultipleChoice):
        question.text = self._upload_images(question.text)

        for answer in question.answers:
            answer.text = self._upload_images(answer.text)

        return question

    def _add_audio_file_to_question(self, question: MultipleChoice):
        mp3_source = self._upload_mp3_file(question.audio_file)

        question.text = self._question_text_templ.format(
            mp3_source=mp3_source,
            question_text=question.text
        )
        return question

    def handle(self, question: MultipleChoice):
        handlers = [
            self._upload_images_in_question,
            self._add_audio_file_to_question,
        ]

        for handler in handlers:
            question = handler(question)

        return question