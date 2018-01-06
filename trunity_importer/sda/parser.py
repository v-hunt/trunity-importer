import warnings
from typing import Union

from bs4 import BeautifulSoup, Tag

from trunity_3_client.builders import Answer

from trunity_importer.sda.question_containers import (
    MultipleChoice,
    QuestionType,
)


class Parser(object):

    def __init__(self, xml: str):
        self._soup = BeautifulSoup(xml, "xml")

        self._questionnaire_titles = self._get_questionnaire_titles()

    @property
    def questionnaire_titles(self):
        return self._questionnaire_titles

    @staticmethod
    def _get_multiple_choice(item_tag: Tag) -> MultipleChoice:
        text = item_tag.display_text.string.strip()

        def get_answers():
            answers = []
            for distractor_tag in item_tag.distractors.find_all("distractor"):
                text = distractor_tag.display_text.string.strip()
                correct = True if distractor_tag['is_correct'] == "True" else False
                score = 1 if correct else 0
                feedback = distractor_tag.rationale.string.strip() \
                    if distractor_tag.rationale.string else ""

                answers.append(
                    Answer(text, correct, score, feedback)
                )
            return answers

        def get_audio_file() -> Union[str, None]:
            if item_tag.media_file:
                return item_tag.media_file['id']
            else:
                warnings.warn(
                    "Audio file wasn't found for item with id {}".format(
                        item_tag['id']
                    )
                )

        test_id = item_tag.test_usage.test_info['test_id']
        item_position = item_tag.test_usage.test_info['item_position']
        # TODO: it possible that some of questions are in wrong order. Use `item_position` for sorting them.

        return MultipleChoice(
            text=text,
            answers=get_answers(),
            audio_file=get_audio_file(),
            test_id=test_id,
            item_position=int(item_position),
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

    def _get_questionnaire_titles(self) -> dict:
        """
        Return dict with test_id's as keys
        and questionnaire titles as values.
        """
        return {
            tag['test_id']: tag['student_facing_title'].strip()
            for tag in self._soup.find_all("test")
        }

    def get_questionnaire_title(self, test_id: str) -> str:
        """
        Get questionnaire title by test_id.

        You can treat test_id as questionnaire id in the xml.
        """
        title = self._questionnaire_titles[test_id]
        if not title:
            test_name = self._soup.find("test", test_id=test_id)['test_name']
            title = "test_name: " + test_name

        return title + " - Question Pool"
