import warnings
from typing import List

from bs4 import BeautifulSoup, Tag

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
                feedback = distractor_tag.rationale.string.strip() \
                    if distractor_tag.rationale.string else ""

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
        for item in self._soup.find_all("item"):
            type_, question = None, None
            if item['type'] == 'MultipleChoice':
                type_ = QuestionType.MULTIPLE_CHOICE
                question = self._get_multiple_choice(item)

            elif item['type'] == 'TechnologyEnhanced':
                # we ignore this type of questions as Trunity doesn't
                # have the functionality at the moment.
                pass

            else:
                warnings.warn(
                    "Question type is unknown!"
                )
                print('\tUnknown question type: ', item['type'])

            if type_ is not None and question is not None:
                yield {'type': type_, 'question': question}
