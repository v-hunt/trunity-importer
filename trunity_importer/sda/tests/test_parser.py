import os
from unittest import TestCase

from bs4 import BeautifulSoup
from trunity_3_client.builders import Answer

from trunity_importer.sda.parser import Parser, _GradeParser, GradeError
from trunity_importer.sda.question_containers import MultipleChoice
from trunity_importer.sda import QuestionType

DATA_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),  # current file dir
    'data'
)


class GradeParserTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        assert os.path.isdir(DATA_DIR), "Data directory isn't exist!"

        with open(
                os.path.join(DATA_DIR, 'XML_Export_sample.xml')
        ) as fo:
            cls.xml_export_soup = BeautifulSoup(fo.read(), 'xml')

        cls.parser = _GradeParser(cls.xml_export_soup)

    def test__extract_grade_from_activity_reference(self):
        test_data = {
            'SCIDIM_NA18E_OLA_G01U00L00_0033': '1',
            'SCIDIM_NA18E_OLA_G0KU04L00_0019': 'K',
            'SCIDIM_NA18E_OLA_G05U00L00_0039': '5',
            'SCIDIM_NA18E_OLA_G077U00L00_0039': '77',
            'Wrong data..': None,
            '': None,
        }

        result = [self.parser._extract_grade_from_activity_reference(activity_reference)
                  for activity_reference in test_data.keys()]
        correct_answers = list(test_data.values())

        self.assertListEqual(
            result,
            correct_answers,
            "Wrong grade extraction!"
        )

    def test__get_all_activity_references(self):
        self.assertDictEqual(
            self.parser._get_all_activity_references(),
            {
                '222': 'SCIDIM_NA18E_OLA_G0KU04L00_0019',
                '111': 'SCIDIM_NA18E_OLA_G01U00L00_0033',
                '333': '',
                '444': 'Wrong data..',
            },
            "Wrong activity_references!"
        )

    def test_test_ids(self):
        self.assertDictEqual(
            self.parser.test_ids,
            {
                "111": "1",
                "222": "K",
            },
            "Wrong test_ids!"
        )

    def test_grades_available(self):
        # we don't care about order, so we use sorted here:
        self.assertListEqual(
            sorted(self.parser.grades_available),
            sorted([
                "1",
                "K",
            ])
        )

    def test_grade_is_valid(self):
        self.assertListEqual(
            [self.parser.grade_is_valid(grade) for grade in ("1", "K", "KK")],
            [True, True, False],
            "grade_is_valid not working!"
        )

    def test_validate_grade(self):
        with self.assertRaises(GradeError):
            self.parser.validate_grade("KK")


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

        with open(
                os.path.join(DATA_DIR, 'TechnologyEnhancedMultipleAnswer.json')
        ) as fo:
            cls.tech_enhance_mult_answer_json = fo.read()

        with open(
                os.path.join(DATA_DIR, 'TechnologyEnhancedMultipleAnswer.xml')
        ) as fo:
            cls.tech_enhance_mult_answer_xml = fo.read().format(
                technology_enhanced_json=cls.tech_enhance_mult_answer_json,
            )

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

    def test__is_multiple_answer(self):
        item_tag = BeautifulSoup(
            self.tech_enhance_mult_answer_xml, "xml").find('item')

        self.assertTrue(
            Parser._is_multiple_answer(item_tag),
            "Wrong question type!"
        )

    def test__get_multiple_answers_data(self):

        def test_text():
            self.assertEqual(
                Parser._get_multiple_answers_data(
                    self.tech_enhance_mult_answer_json)[0],
                "<p>Question text</p>",
                "Wrong text for MultipleAnswer!"
            )

        def test_answers():
            self.assertListEqual(
                Parser._get_multiple_answers_data(
                    self.tech_enhance_mult_answer_json)[1],
                [
                    Answer("<p>Answer 1</p>", True, 1, "<p>Feedback 1</p>"),
                    Answer("<p>Answer 2</p>", False, 0, "<p>Feedback 2</p>"),
                    Answer("<p>Answer 3</p>", True, 1, "<p>Feedback 3</p>"),
                ],
                "Wrong answers for MultipleAnswer!"
            )

        test_text()
        test_answers()

    def test__get_multiple_answer(self):
        tag = BeautifulSoup(self.tech_enhance_mult_answer_xml, "xml").find('item')
        question = Parser._get_multiple_answer(tag)

        self.assertEqual(
            question.text,
            "<p>Question text</p>",
            "Wrong text for MultipleAnswer question!"
        )

        self.assertListEqual(
            question.answers,
            [
                Answer("<p>Answer 1</p>", True, 1, "<p>Feedback 1</p>"),
                Answer("<p>Answer 2</p>", False, 0, "<p>Feedback 2</p>"),
                Answer("<p>Answer 3</p>", True, 1, "<p>Feedback 3</p>"),
            ],
            "Wrong answer for MultipleAnswer question!"
        )

        self.assertEqual(
            question.audio_file,
            "12345.mp3",
            "Wrong audio file for MultipleAnswer question!"
        )

        self.assertEqual(
            question.test_id,
            '12345',
            "Wrong test_id for MultipleAnswer question!"
        )

        self.assertEqual(
            question.item_position,
            1,
            "Wrong item_position for MultipleAnswer question!"
        )

        self.assertEqual(
            question.item_id,
            831087,
            "Wrong item_id for MultipleAnswer question!"
        )