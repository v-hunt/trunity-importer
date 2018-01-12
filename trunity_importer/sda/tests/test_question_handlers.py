from unittest import TestCase

from trunity_importer.sda.question_handler import ImageSrcFixer


class ImageSrcFixerTestCase(TestCase):

    def test_mult_answer_fixer(self):
        image_path = 'https://webcms.rpclearning.com/GetImagePreview.aspx?ImageID=580404'
        self.assertEqual(
            ImageSrcFixer.mult_answer_fixer(image_path),
            "images/580404.gif",
            "Wrong image path for MultipleAnswer!"
        )
