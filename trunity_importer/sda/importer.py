from zipfile import ZipFile

from bs4 import BeautifulSoup
from trunity_3_client.clients.auth import initialize_session_from_creds
from trunity_3_client.clients.endpoints import (
    TopicsClient,
    FilesClient,
)
from trunity_3_client.builders import Questionnaire


from trunity_importer.sda.parser import Parser, QuestionType, MultipleChoice
from trunity_importer.utils import create_qst_pool


class Importer(object):
    """
    Import Science Dimensions Assessments to Trunity.
    """

    def __init__(self, username: str, password: str, book_id: int,
                 path_to_zip: str, topic_id=None):

        self._book_id = book_id
        self._zip_file = ZipFile(path_to_zip)
        self.t3_session = initialize_session_from_creds(username, password)

        self._topic_client = TopicsClient(self.t3_session)
        self._files_client = FilesClient(self.t3_session)

        # we need json content type for uploading questionnaires:
        self.t3_json_session = initialize_session_from_creds(
            username, password, content_type='application/json')

        self._topic_id = topic_id

    def _get_xml_file_name(self):
        """
        Pattern is XML_Export_DDDD.xml
        """
        for file_name in self._zip_file.namelist():
            if file_name.startswith('XML_Export') and file_name.endswith('.xml'):
                return file_name

    def questionnaire_name(self) -> str:
        """
        Construct questionnaire name from zip file full path.

        Example:
            if full_path is '/home/username/bla-bla.zip',
            the result will be 'bla-bla'
        """
        file_name = self._zip_file.filename
        return file_name.split("/")[-1].replace('.zip', '')

    def _upload_images(self, html: str):
        """
        Upload all images to Trunity and replace src attributes with new urls.
        """
        def fix_image_src(image_path: str) -> str:
            return image_path.replace("\\", "/") + ".gif"

        soup = BeautifulSoup(html, "lxml")
        for img in soup.find_all("img"):
            image_src = fix_image_src(img['src'])
            file_obj = self._zip_file.open(image_src)
            cdn_file_url = self._files_client.list.post(file_obj=file_obj)
            img['src'] = cdn_file_url

        return soup.decode()

    def _upload_images_in_question(self, question: MultipleChoice):
        question.text = self._upload_images(question.text)

        for answer in question.answers:
            answer.text = self._upload_images(answer.text)

        return question

    def perform_import(self):

        xml_file_name = self._get_xml_file_name()
        with self._zip_file.open(xml_file_name) as file_obj:
            xml = file_obj.read()

        parser = Parser(xml)

        questionnaire_id = create_qst_pool(
            session=self.t3_session,
            site_id=self._book_id,
            content_title=self.questionnaire_name(),
            topic_id=self._topic_id,
        )

        questionnaire = Questionnaire(self.t3_json_session)

        for question in parser.get_questions():
            question['question'] = self._upload_images_in_question(
                question['question']
            )

            if question['type'] == QuestionType.MULTIPLE_CHOICE:
                questionnaire.add_multiple_choice(
                    question['question'].text,
                    question['question'].answers,
                )

        questionnaire.upload(questionnaire_id)
