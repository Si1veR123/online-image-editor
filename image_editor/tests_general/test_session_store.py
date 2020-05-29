from django.contrib.sessions.models import Session
from django.test import TestCase, override_settings
from django.conf import settings
from image_editor.custom_session import SessionStore
import os


@override_settings(UPLOADED_IMAGES_ROOT=os.path.join(settings.BASE_DIR, 'test_uploaded_images'))
class SesssonStoreTest(TestCase):
    def setUp(self):
        # create session and key
        self.session = SessionStore()
        self.session.create()
        self.session_key = self.session.session_key

    def test_flush(self):
        # check that folder and key exists
        self.assertTrue(os.path.exists(os.path.join(settings.UPLOADED_IMAGES_ROOT, self.session_key)))
        Session.objects.get(session_key=self.session_key)

        # flush the session
        self.session.flush()

        # check that session doesnt exist and folder is deleted
        with self.assertRaises(Session.DoesNotExist):
            Session.objects.get(session_key=self.session_key)
        self.assertFalse(os.path.exists(os.path.join(settings.UPLOADED_IMAGES_ROOT, self.session_key)))

    def test_create(self):
        self.assertTrue(self.session.exists(self.session_key))
        root = os.path.join(settings.UPLOADED_IMAGES_ROOT, self.session_key)
        self.assertTrue(os.path.exists(root))
        self.assertTrue(os.path.exists(os.path.join(root, "undo")))
        self.assertTrue(os.path.exists(os.path.join(root, "redo")))

    def tearDown(self):
        if self.session.exists(self.session_key):
            self.session.flush()