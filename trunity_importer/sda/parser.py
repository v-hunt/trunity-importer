import warnings
from typing import Union

from bs4 import BeautifulSoup, Tag

from trunity_3_client.builders import Answer

from trunity_importer.sda.question_containers import (
    MultipleChoice,
    Essay,
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
    def _get_gen_meta_info(item_tag: Tag) -> dict:
        """
        Parse common information for all types of questions.
        """
        text = item_tag.display_text.string.strip()
        item_id = int(item_tag['id'])

        def get_audio_file() -> Union[str, None]:
            if item_tag.media_file:
                return item_tag.media_file['id']
            else:
                warnings.warn(
                    "Audio file wasn't found for item with id {}".format(
                        item_id
                    )
                )

        test_id = item_tag.test_usage.test_info['test_id']
        item_position = item_tag.test_usage.test_info['item_position']
        # TODO: it possible that some of questions are in wrong order. Use `item_position` for sorting them.

        return dict(
            text=text,
            item_id=item_id,
            audio_file=get_audio_file(),
            test_id=test_id,
            item_position=int(item_position),
        )

    @staticmethod
    def _get_multiple_choice(item_tag: Tag) -> MultipleChoice:

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

        meta_info = Parser._get_gen_meta_info(item_tag)

        return MultipleChoice(
            text=meta_info['text'],
            answers=get_answers(),
            audio_file=meta_info['audio_file'],
            test_id=meta_info['test_id'],
            item_position=meta_info['item_position'],
            item_id=meta_info['item_id'],
        )

    @staticmethod
    def _get_essay(item_tag: Tag) -> Essay:
        correct_answer = item_tag.rubric_text.string.strip()
        meta_info = Parser._get_gen_meta_info(item_tag)

        return Essay(
            text=meta_info['text'],
            correct_answer=correct_answer,
            audio_file=meta_info['audio_file'],
            test_id=meta_info['test_id'],
            item_position=meta_info['item_position'],
            item_id=meta_info['item_id'],
        )

    def get_questions(self):
        for item in self._soup.find_all("item"):
            question = None
            if item['type'] == 'MultipleChoice':
                question = self._get_multiple_choice(item)

            elif item['type'] == 'ConstructedResponse':
                # we treat ConstructedResponse as Trunity Essay:
                question = self._get_essay(item)

            elif item['type'] == 'TechnologyEnhanced':
                # we ignore this type of questions as Trunity doesn't
                # have the functionality at the moment.
                pass

            else:
                warnings.warn(
                    "Question type is unknown!"
                )
                print('\tUnknown question type: ', item['type'])

            if question is not None:
                yield question

    def _get_questionnaire_titles(self) -> dict:
        """
        Return dict with test_id's as keys
        and questionnaire titles as values.
        """
        return {
            tag['test_id']: tag['test_name'].strip()
            for tag in self._soup.find_all("test")
        }

    def get_questionnaire_title(self, test_id: str) -> str:
        """
        Get questionnaire title by test_id.

        You can treat test_id as questionnaire id in the xml.
        """
        title = self._questionnaire_titles[test_id]
        return title + " - Question Pool"
