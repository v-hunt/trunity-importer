import os
from collections import namedtuple

from requests import HTTPError
from trunity_3_client import (
    get_auth_token,
    ContentsClient,
    ContentType,
    ResourceType
)

ENVIRON_USERNAME = 'T3_USERNAME'
ENVIRON_PASSWORD = 'T3_PWD'
CREDS = namedtuple('CREDS', ['username', 'password'])


def check_and_get_creds():
    """
    Get username and password from environmental variables.
    If fail, prompt the user.
    """
    username = os.environ.get(ENVIRON_USERNAME, None)
    password = os.environ.get(ENVIRON_PASSWORD, None)

    if username is not None and password is not None:
        return CREDS(username, password)

    auth_token = None

    while auth_token is None:
        username = input("Your username? ")
        password = input("Your password? ")
        try:
            print('Checking your credentials...', end='')
            auth_token = get_auth_token(username, password)
        except HTTPError:
            print('\t\t FAIL!', end='\n\n')
        else:
            print('\t\tOK!')
            os.environ[ENVIRON_USERNAME] = username
            os.environ[ENVIRON_PASSWORD] = username
            return CREDS(username, password)


def create_qst_pool(session, site_id, content_title, topic_id=None):
    cnt_client = ContentsClient(session)
    return cnt_client.list.post(
        site_id=site_id,
        content_title=content_title,
        content_type=ContentType.QUESTIONNAIRE,
        topic_id=topic_id,
        resource_type=ResourceType.QUESTION_POOL,
    )
