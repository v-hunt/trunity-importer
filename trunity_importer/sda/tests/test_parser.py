import os
from unittest import TestCase

from bs4 import BeautifulSoup
from trunity_3_client.builders import Answer

from trunity_importer.sda.parser import Parser
from trunity_importer.sda.question_containers import MultipleChoice
from trunity_importer.sda import QuestionType

DATA_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),  # current file dir
    'data'
)


class ParserTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        assert os.path.isdir(DATA_DIR), "Data directory isn't exist!"

        with open(
                os.path.join(DATA_DIR, 'multiple_choice.xml')
        ) as fo:
            cls.multiple_choice_xml = fo.read()

        with open(
                os.path.join(DATA_DIR, 'XML_Export_sample.xml')
        ) as fo:
            cls.xml_export_sample = fo.read()

        with open(
                os.path.join(DATA_DIR, 'essay.xml')
        ) as fo:
            cls.essay_xml = fo.read()

    def test__get_multiple_choice(self):
        tag = BeautifulSoup(self.multiple_choice_xml, "xml").find('item')
        question = Parser._get_multiple_choice(tag)

        self.assertEqual(
            question.text,
            "<p>Text</p>",
            "Wrong text for MultipleChoice question!"
        )

        self.assertListEqual(
            question.answers,
            [
                Answer("<p>Answer 1</p>", False, 0, "<p>Feedback 1</p>"),
                Answer("<p>Answer 2</p>", True, 1, "<p>Feedback 2</p>"),
                Answer("<p>Answer 3</p>", False, 0, "<p>Feedback 3</p>"),
            ],
            "Wrong answer for MultipleChoice question!"
        )

        self.assertEqual(
            question.audio_file,
            "12345.mp3",
            "Wrong audio file for MultipleChoice question!"
        )

        self.assertEqual(
            question.test_id,
            '12345',
            "Wrong test_id for MultipleChoice question!"
        )

        self.assertEqual(
            question.item_position,
            1,
            "Wrong item_position for MultipleChoice question!"
        )

        self.assertEqual(
            question.item_id,
            831087,
            "Wrong item_id for MultipleChoice question!"
        )

    def test__get_essay(self):
        item_tag = BeautifulSoup(self.essay_xml, "xml").find('item')
        question = Parser._get_essay(item_tag)

        self.assertEqual(
            question.text,
            "<p>Text</p>",
            "Wrong text for Essay question!"
        )

        self.assertEqual(
            question.correct_answer,
            "<p>Answer</p>",
            "Wrong answer for Essay question!"
        )

        self.assertEqual(
            question.audio_file,
            "12345.mp3",
            "Wrong audio file for Essay question!"
        )

        self.assertEqual(
            question.test_id,
            '12345',
            "Wrong test_id for Essay question!"
        )

        self.assertEqual(
            question.item_position,
            1,
            "Wrong item_position for Essay question!"
        )

        self.assertEqual(
            question.item_id,
            831087,
            "Wrong item_id for Essay question!"
        )

    def test_get_questions(self):
        parser = Parser(self.multiple_choice_xml)

        for question in parser.get_questions():
            self.assertEqual(
                question.type,
                QuestionType.MULTIPLE_CHOICE,
            )
            self.assertTrue(
                isinstance(question, MultipleChoice),
            )

    def test_questionnaire_titles(self):
        parser = Parser(self.xml_export_sample)

        self.assertDictEqual(
            parser.questionnaire_titles,
            {
                '111': 'Questionnaire 1',
                '222': 'Questionnaire 2',
                '333': 'Questionnaire 3',
                '444': 'Questionnaire 4',
            },
            "Wrong questionnaire titles!"
        )

    def test_get_questionnaire_title(self):
        parser = Parser(self.xml_export_sample)

        self.assertEqual(
            parser.get_questionnaire_title('444'),
            "Questionnaire 4" + " - Question Pool"
        )
