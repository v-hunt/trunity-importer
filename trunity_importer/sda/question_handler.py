import os
import re
from zipfile import ZipFile
from typing import Callable

from bs4 import BeautifulSoup
from trunity_3_client import FilesClient

from trunity_importer.sda.question_containers import (
    MultipleChoice,
    MultipleAnswer,
    Essay,
    Question,
    QuestionType,
)

QUESTION_TEXT_TEMPLATE = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),  # current file dir
    'templates/question.html'
)


class ImageSrcFixer:

    @staticmethod
    def general_fixer(image_path: str) -> str:
        return image_path.replace("\\", "/") + ".gif"

    @staticmethod
    def mult_answer_fixer(image_path: str) -> str:
        """
        Takes https://webcms.rpclearning.com/GetImagePreview.aspx?ImageID=580404
        and return "images/580404.gif"
        """
        pattern = re.compile(r"ImageID=(\d+)")
        find = re.findall(pattern, image_path)
        return 'images/' + find[0] + '.gif'


class QuestionHandler:

    def __init__(self, files_client: FilesClient,
                 zip_file: ZipFile):
        self._files_client = files_client
        self._zip_file = zip_file

        with open(QUESTION_TEXT_TEMPLATE) as fo:
            self._question_text_templ = fo.read()

    def _upload_images(self, html: str, img_src_fixer: Callable[[str], str]):
        """
        Upload all images to Trunity and replace src attributes with new urls.
        """
        soup = BeautifulSoup(html, "lxml")
        for img in soup.find_all("img"):
            image_src = img_src_fixer(img['src'])
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

    def _upload_images_in_multiple_answer(self, question: MultipleAnswer):
        img_src_fixer = ImageSrcFixer.mult_answer_fixer
        print("Uploading images for MultipleAnswer "
              "(TechnologyEnhanced) question...", end='')
        question.text = self._upload_images(question.text, img_src_fixer)

        for answer in question.answers:
            answer.text = self._upload_images(answer.text, img_src_fixer)

        print("\t\t Success!")
        return question

    def _upload_images_in_multiple_choice(self, question: MultipleChoice):
        img_src_fixer = ImageSrcFixer.general_fixer

        print("Uploading images for MultipleChoice question...", end='')
        question.text = self._upload_images(question.text, img_src_fixer)

        for answer in question.answers:
            answer.text = self._upload_images(answer.text, img_src_fixer)

        print("\t\t Success!")
        return question

    def _upload_images_in_essay(self, question: Essay):
        img_src_fixer = ImageSrcFixer.general_fixer

        print("Uploading images for Essay question...", end='')

        question.text = self._upload_images(question.text, img_src_fixer)
        question.correct_answer = self._upload_images(
            question.correct_answer,
            img_src_fixer,
        )

        print("\t\t Success!")
        return question

    def _add_audio_file_to_question(self, question: Question):
        if question.audio_file:
            print("Uploading mp3 for question...", end='')
            mp3_source = self._upload_mp3_file(question.audio_file)

            question.text = self._question_text_templ.format(
                mp3_source=mp3_source,
                question_text=question.text
            )
            print("\t\t Success!")
        return question

    def handle(self, question: Question):
        # for other types of questions that are not listed below:
        handlers = []

        if question.type == QuestionType.MULTIPLE_CHOICE:
            handlers = [
                self._upload_images_in_multiple_choice,
                self._add_audio_file_to_question,
            ]

        elif question.type == QuestionType.ESSAY:
            handlers = [
                self._upload_images_in_essay,
                self._add_audio_file_to_question,
            ]

        elif question.type == QuestionType.MULTIPLE_ANSWER:
            handlers = [
                self._upload_images_in_multiple_answer,
                self._add_audio_file_to_question,
            ]

        for handler in handlers:
            question = handler(question)

        return question
