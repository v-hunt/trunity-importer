from unittest import TestCase
import os

from trunity_3_client.builders import Answer

from trunity_importer.qti.parsers import (
    ManifestParser,
    QuestionnaireMetaInfoParser,
    MultipleChoiceParser,
    MultipleAnswerParser,
    ShortAnswerParser,
    EssayParser,
    QuestionType,
    Question,
)


DATA_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),  # current file dir
    'data'
)


class ImsmanifestParserTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        assert os.path.isdir(DATA_DIR), "Data directory isn't exist!"

        with open(
            os.path.join(DATA_DIR, 'insmanifest.xml')
        ) as fo:
            insmanifest_xml = fo.read()

        cls.parser = ManifestParser.from_xml(insmanifest_xml)

    def test_get_questionnaire_files(self):
        self.assertListEqual(
            self.parser.get_questionnaire_files(),
            ['testitems/-CGM_CA15E_CAR_G04BYT.xml',
             'testitems/-CGM_CA15E_CAR_G04CH1.xml',
             'testitems/-CGM_CA15E_CAR_G04CH10.xml',
             'testitems/-CGM_CA15E_CAR_G04CH10PT.xml',
             'testitems/-CGM_CA15E_CAR_G04CH11.xml',
             'testitems/-CGM_CA15E_CAR_G04CH11PT.xml',
             'testitems/-CGM_CA15E_CAR_G04CH12.xml',
             'testitems/-CGM_CA15E_CAR_G04CH12PT.xml',
             'testitems/-CGM_CA15E_CAR_G04CH13.xml',
             'testitems/-CGM_CA15E_CAR_G04CH13PT.xml',
             'testitems/-CGM_CA15E_CAR_G04CH1PT.xml',
             'testitems/-CGM_CA15E_CAR_G04CH2.xml',
             'testitems/-CGM_CA15E_CAR_G04CH2PT.xml',
             'testitems/-CGM_CA15E_CAR_G04CH3.xml',
             'testitems/-CGM_CA15E_CAR_G04CH3PT.xml',
             'testitems/-CGM_CA15E_CAR_G04CH4.xml',
             'testitems/-CGM_CA15E_CAR_G04CH4PT.xml',
             'testitems/-CGM_CA15E_CAR_G04CH5.xml',
             'testitems/-CGM_CA15E_CAR_G04CH5PT.xml',
             'testitems/-CGM_CA15E_CAR_G04CH6.xml',
             'testitems/-CGM_CA15E_CAR_G04CH6PT.xml',
             'testitems/-CGM_CA15E_CAR_G04CH7.xml',
             'testitems/-CGM_CA15E_CAR_G04CH7PT.xml',
             'testitems/-CGM_CA15E_CAR_G04CH8.xml',
             'testitems/-CGM_CA15E_CAR_G04CH8PT.xml',
             'testitems/-CGM_CA15E_CAR_G04CH9.xml',
             'testitems/-CGM_CA15E_CAR_G04CH9PT.xml',
             'testitems/-CGM_CA15E_CAR_G04EYT.xml',
             'testitems/-CGM_CA15E_CAR_G04GRTL_1_11.xml',
             'testitems/-CGM_CA15E_CAR_G04GRTL_12_20.xml',
             'testitems/-CGM_CA15E_CAR_G04MYT.xml',
             'testitems/-CGM_CA15E_CAR_G04PSY.xml',
             'testitems/-CGM_CA15E_CAR_G04U1PT.xml',
             'testitems/-CGM_CA15E_CAR_G04U2PT.xml',
             'testitems/-CGM_CA15E_CAR_G04U3PT.xml']

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
                Answer('<b>Answer 2</b>', True, 1),
                Answer('<b>Answer 2</b>', True, 1),
            ]
        )


class ShortAnswerParserTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        assert os.path.isdir(DATA_DIR), "Data directory isn't exist!"

        with open(
                os.path.join(DATA_DIR, 'short_answer.xml')) as fo:
            question_xml = fo.read()

        cls.parser = ShortAnswerParser.from_xml(question_xml)

    def test_get_text(self):
        self.assertEqual(
            self.parser.get_text(),
            "Question <b>text</b>"
        )

    def test_get_answer(self):

        self.assertEqual(
            self.parser.get_answer(),
            Answer('10', True, 1),
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

    def test_get_correct_answer(self):

        self.assertEqual(
            self.parser.get_correct_answer(),
            "<p>Feedback (correct answer)</p>"
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

        with open(
                os.path.join(DATA_DIR, 'short_answer.xml')) as fo:
            cls.short_answer_xml = fo.read()

    def test_type_is_multiple_choice(self):
        question = Question.from_xml(self.multiple_choice_xml)

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

    def test_type_is_short_answer(self):
        question = Question.from_xml(self.short_answer_xml)

        self.assertEqual(
            question.type,
            QuestionType.SHORT_ANSWER,
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

    def test_parser_is_essay_parser(self):
        question = Question.from_xml(self.essay_xml)

        self.assertTrue(
            isinstance(question.parser, EssayParser),
            "Must be EssayParser instance!"
        )

    def test_parser_is_short_answer_parser(self):
        question = Question.from_xml(self.short_answer_xml)

        self.assertTrue(
            isinstance(question.parser, ShortAnswerParser),
            "Must be ShortAnswerParser instance!"
        )
