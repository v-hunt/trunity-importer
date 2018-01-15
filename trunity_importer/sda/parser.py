import re
import json
from typing import Union, List

from bs4 import BeautifulSoup, Tag

from trunity_3_client.builders import Answer

from trunity_importer.sda.question_containers import (
    MultipleChoice,
    MultipleAnswer,
    Essay,
)
from trunity_importer.sda.validators.pre_validators import validate
from trunity_importer.sda.warnings import warnings


class GradeError(ValueError):
    """
    Raise when there is no such grade exist or with other grade issues.
    """
    pass


class _GradeParser(object):
    """
    Parse XML export file for Grades.
    """

    def __init__(self, soup: BeautifulSoup):
        self._soup = soup

        self._test_ids = self._get_test_ids()
        self._grades_available = list(self.test_ids.values())

    @property
    def grades_available(self) -> List[str]:
        """
        List of all available grades.

        Example:
            ["1", "K", "21"]
        """
        unique_grades = set(self._grades_available)
        return list(unique_grades)

    @property
    def test_ids(self) -> dict:
        """
        Dict with test_id as keys, grades as values.

        Example:
            {
                "111": "1",
                "222": "K",
            },
        """
        return self._test_ids

    @staticmethod
    def _extract_grade_from_activity_reference(activity_reference: str) -> str:
        """
        Examples:
        SCIDIM_NA18E_OLA_G0KU04L00_0019 -> K
        SCIDIM_NA18E_OLA_G01U00L00_0033 -> 1
        (should be the character between "SCIDIM_NA18E_OLA_G0" and "U")

        :param activity_reference: activity_reference attribute value
        :return: grade, for example, '1', '22', 'K' etc
        """
        pattern = re.compile(
            r"^SCIDIM_NA18E_OLA_G0([A-Z,0-9]+)U.+"
        )
        match = re.match(pattern, activity_reference)

        if match:
            return match.groups()[0]

    def _get_all_activity_references(self) -> dict:
        """
        Return dict with test_id's as keys
        and activity_reference attributes as values.
        """
        return {
            tag['test_id']: tag['activity_reference'].strip()
            for tag in self._soup.find_all("test")
        }

    def _get_test_ids(self) -> dict:
        """
        Dict with test_id as keys, grades as values.
        """
        activity_references = self._get_all_activity_references()
        test_ids = {}

        for test_id, activity_reference in activity_references.items():
            grade = self._extract_grade_from_activity_reference(
                activity_reference
            )
            if grade is not None:
                test_ids[test_id] = grade

        return test_ids

    def grade_is_valid(self, grade: str) -> bool:
        """
        Return True if grade in available grades in XML. False otherwise.
        """
        if grade in self.grades_available:
            return True
        return False

    def validate_grade(self, grade: str):
        """
        Raise GradeError when `grade` not in available grades list.
        """
        if not self.grade_is_valid(grade):
            raise GradeError(
                "There is no grade {grade}. " +
                "Grades available: {grades_available}".format(
                    grade=grade,
                    grades_available=self.grades_available,
                )
            )


class Parser(object):
    """
    Parser for "XML export file".
    (File with name in format XML_Export_DDDDD.xml)
    """

    def __init__(self, xml: str):
        self._soup = BeautifulSoup(xml, "xml")

        self._questionnaire_titles = self._get_questionnaire_titles()
        self.grades = _GradeParser(self._soup)

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
    def _is_multiple_answer(item_tag: Tag):
        """
        Check if item tag can be treated as MultipleAnswer.

        Some of TechnologyEnhanced can be treated as MultipleAnswer.
        """
        json_str = item_tag.display_text.string.strip()
        data = json.loads(json_str)
        if "multiple_responses" in data and data["multiple_responses"] is True \
                and "type" in data and data["type"] == "mcq":
            return True
        return False

    @staticmethod
    def _get_multiple_answers_data(json_str: str):
        data = json.loads(json_str)

        text = data["stimulus"]

        def get_answers():
            answers = []
            for num, option in enumerate(data["options"]):
                text = option["label"]
                correct = True if option["value"] in data["validation"]["valid_response"]["value"] else False
                score = 1 if correct else 0
                feedback = data["metadata"]["distractor_rationale_response_level"][num] \
                    if "metadata" in data and "distractor_rationale_response_level" in data["metadata"] else ""

                answers.append(Answer(
                    text, correct, score, feedback,
                ))
            return answers

        return text, get_answers()

    @staticmethod
    def _get_multiple_answer(item_tag: Tag) -> MultipleAnswer:
        meta_info = Parser._get_gen_meta_info(item_tag)

        text, answers = Parser._get_multiple_answers_data(meta_info['text'])

        return MultipleAnswer(
            text=text,
            answers=answers,
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
            is_valid = validate(item)

            if is_valid:
                if item['type'] == 'MultipleChoice':
                    question = self._get_multiple_choice(item)

                elif item['type'] == 'ConstructedResponse':
                    # we treat ConstructedResponse as Trunity Essay:
                    question = self._get_essay(item)

                elif item['type'] == 'TechnologyEnhanced':
                    # we only can support MultipleAnswer for this type:
                    if self._is_multiple_answer(item):
                        question = self._get_multiple_answer(item)

                else:
                    warnings.add(
                        item_id=item['id'],
                        message="Question type is unknown - {}".format(item['type'])
                    )

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
