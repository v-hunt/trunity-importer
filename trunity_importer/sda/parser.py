import warnings
from zipfile import ZipFile
from typing import List
from abc import ABC

from bs4 import BeautifulSoup, CData, Tag

from trunity_3_client.builders import Answer


class QuestionType:
    MULTIPLE_CHOICE = 'multiple_choice'


class MultipleChoice:
    """
    Container for parsed MultipleChoice question.
    """

    def __init__(self, text: str, answers: List[Answer], audio_file: str):
        self.text = text
        self.answers = answers
        self.audio_file = audio_file


class Parser(object):

    def __init__(self, xml: str):
        self._soup = BeautifulSoup(xml, "xml")

    @staticmethod
    def _get_multiple_choice(tag: Tag) -> MultipleChoice:
        text = tag.display_text.string.strip()

        def get_answers():
            answers = []
            for distractor_tag in tag.distractors.find_all("distractor"):
                text = distractor_tag.display_text.string.strip()
                correct = True if distractor_tag['is_correct'] == "True" else False
                score = 1 if correct else 0
                feedback = distractor_tag.rationale.string.strip()

                answers.append(
                    Answer(text, correct, score, feedback)
                )
            return answers

        audio_file = tag.media_file['id']

        return MultipleChoice(
            text=text,
            answers=get_answers(),
            audio_file=audio_file,
        )

    def get_questions(self):
        pass