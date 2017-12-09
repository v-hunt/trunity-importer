from unittest import TestCase
import os

from trunity_3_client.builders import Answer

from trunity_importer.qti.parser import (
    QuestionnaireMetaInfoParser,
    MultipleChoiceParser,
    MultipleAnswerParser,
    EssayParser,
    QuestionType,
    Question,
)


DATA_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),  # current file dir
    'data'
)


class QuestionnaireMetaInfoParserTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        assert os.path.isdir(DATA_DIR), "Data directory isn't exist!"

        with open(
                os.path.join(DATA_DIR, 'question_pool_meta_sample.xml')) as fo:
            question_info_xml = fo.read()

        cls.parser = QuestionnaireMetaInfoParser.from_xml(question_info_xml)

    def test_get_questionnaire_title(self):

        self.assertEqual(
            self.parser.get_questionnaire_title(),
            'Questionnaire Title'
        )

    def test_get_file_names(self):

        self.assertListEqual(
            self.parser.get_file_names(),
            ["question_1.xml", "question_2.xml", "question_3.xml", "question_4.xml"]
        )

    def test_get_section_title(self):

        self.assertEqual(
            self.parser.get_section_title(),
            "Section 1"
        )


class MultipleChoiceParserTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        assert os.path.isdir(DATA_DIR), "Data directory isn't exist!"

        with open(
                os.path.join(DATA_DIR, 'multiple_choice.xml')) as fo:
            question_xml = fo.read()

        cls.parser = MultipleChoiceParser.from_xml(question_xml)

    def test_get_text(self):

        self.assertEqual(
            self.parser.get_text(),
            "Question <b>text</b>"
        )

    def test_get_answers(self):

        self.assertListEqual(
            self.parser.get_answers(),
            [
                Answer('Answer 1', False, 0),
                Answer('Answer 2', False, 0),
                Answer('Answer 3', True, 1),
                Answer('Answer 4', False, 0),
            ]
        )


class MultipleAnswerParserTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        assert os.path.isdir(DATA_DIR), "Data directory isn't exist!"

        with open(
                os.path.join(DATA_DIR, 'multiple_answer.xml')) as fo:
            question_xml = fo.read()

        cls.parser = MultipleAnswerParser.from_xml(question_xml)

    def test_get_text(self):
        self.assertEqual(
            self.parser.get_text(),
            "Question <b>text</b>"
        )

    def test_get_answers(self):
        self.assertListEqual(
            self.parser.get_answers(),
            [
                Answer('Answer 1', False, 0),
                Answer('Answer 2', True, 1),
                Answer('Answer 3', True, 1),
                Answer('Answer 4', True, 1),
            ]
        )


class EssayParserTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        assert os.path.isdir(DATA_DIR), "Data directory isn't exist!"

        with open(
                os.path.join(DATA_DIR, 'essay.xml')) as fo:
            question_xml = fo.read()

        cls.parser = EssayParser.from_xml(question_xml)

    def test_get_text(self):

        self.assertEqual(
            self.parser.get_text(),
            "Question <b>text</b>"
        )


class QuestionTestCase(TestCase):
    """
    TestCase for main parser class.
    """

    @classmethod
    def setUpClass(cls):
        assert os.path.isdir(DATA_DIR), "Data directory isn't exist!"

        with open(
                os.path.join(DATA_DIR, 'multiple_choice.xml')) as fo:
            cls.multiple_choice_xml = fo.read()

        with open(
                os.path.join(DATA_DIR, 'multiple_answer.xml')) as fo:
            cls.multiple_answer_xml = fo.read()

        with open(
                os.path.join(DATA_DIR, 'essay.xml')) as fo:
            cls.essay_xml = fo.read()

    def test_type_is_multiple_choice(self):
        question = Question.from_xml(self.multiple_choice_xml)
        print('Type: ', question.type)

        self.assertEqual(
            question.type,
            QuestionType.MULTIPLE_CHOICE,
            "Wrong question type!"
        )

    def test_type_is_multiple_answer(self):
        question = Question.from_xml(self.multiple_answer_xml)

        self.assertEqual(
            question.type,
            QuestionType.MULTIPLE_ANSWER,
            "Wrong question type!"
        )

    def test_type_is_essay(self):
        question = Question.from_xml(self.essay_xml)

        self.assertEqual(
            question.type,
            QuestionType.ESSAY,
            "Wrong question type!"
        )

    def test_parser_is_multiple_choice_parser(self):
        question = Question.from_xml(self.multiple_choice_xml)

        self.assertTrue(
            isinstance(question.parser, MultipleChoiceParser),
            "Must be MultipleChoiceParser instance!"
        )

    def test_parser_is_multiple_answer_parser(self):
        question = Question.from_xml(self.multiple_answer_xml)

        self.assertTrue(
            isinstance(question.parser, MultipleAnswerParser),
            "Must be MultipleAnswerParser instance!"
        )

    def test_parser_essay_parser(self):
        question = Question.from_xml(self.essay_xml)

        self.assertTrue(
            isinstance(question.parser, EssayParser),
            "Must be EssayParser instance!"
        )

