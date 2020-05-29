from django.test import TestCase, override_settings
from django.conf import settings
import os
import shutil


class CustomSession:
    """
    Functions that use file tests require a session object with a dictionary like structure and the session_key property
    """
    def __init__(self, items, session_key):
        self.items = items
        self.session_key = session_key

    def __getitem__(self, item):
        return self.items[item]


class CustomRequest:
    """
    Functions that use file tests require a request object to access the session object
    """
    def __init__(self, items: dict, session_key: str):
        self.session = CustomSession(items, session_key)


@override_settings(UPLOADED_IMAGES_ROOT=os.path.join(settings.BASE_DIR, 'test_uploaded_images'))
class TestFileEnvironment(TestCase):
    """Creates a temporary file system and provides a request like object and session_key"""
    def setUp(self):
        """
        Creates the test directory and request object
        """
        # create test request and session
        self.r = CustomRequest(items={"type": ".jpg"}, session_key="test")
        # get root of session key folder
        self.session_key_root = os.path.join(settings.UPLOADED_IMAGES_ROOT, self.r.session.session_key)
        # make folders
        os.mkdir(self.session_key_root)
        os.mkdir(os.path.join(self.session_key_root, "undo"))
        os.mkdir(os.path.join(self.session_key_root, "redo"))

    def tearDown(self):
        # cleanup, remove test folder
        shutil.rmtree(os.path.join(settings.UPLOADED_IMAGES_ROOT, self.r.session.session_key))
