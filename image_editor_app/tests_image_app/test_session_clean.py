from django.test import override_settings, TestCase
from django.conf import settings
from django.contrib.sessions.models import Session
from image_editor.custom_session import SessionStore
from image_editor_app import session_cleaner
import os
import time
import shutil


@override_settings(UPLOADED_IMAGES_ROOT=os.path.join(settings.BASE_DIR, 'test_uploaded_images'))
class TestSessionClean(TestCase):
    def setUp(self):
        self.s = SessionStore()

    def test_clear_inactive(self):
        # set expiry to 1 second
        self.s.set_expiry(1)
        # create session
        self.s.create()
        # wait 3 seconds
        time.sleep(3)
        # call the cleaner with False testing argument as, with testing=True, function returns instantly
        session_cleaner.session_clean(False)
        # check expired session is cleared
        self.assertTrue([s for s in Session.objects.get_queryset()] == [])

    def test_max_time(self):
        # set start to 0, should be expired
        self.s["start"] = 0
        # set to high value, shouldn't be cleared from activity expiration
        self.s.set_expiry(1000)
        self.s.create()

        # call the cleaner with False testing argument as, with testing=True, function returns instantly
        session_cleaner.session_clean(False)

        # check session deleted
        self.assertTrue([s for s in Session.objects.get_queryset()] == [])

    def test_no_session_key(self):
        # make a folder in uploaded images directory
        path = os.path.join(settings.UPLOADED_IMAGES_ROOT, "test_should_be_deleted")
        os.mkdir(path)

        # call the cleaner with False testing argument as, with testing=True, function returns instantly
        session_cleaner.session_clean(False)

        # check folder is deleted
        self.assertFalse(os.path.exists(path))

    def test_no_folder(self):
        # create session
        self.s["start"] = time.time()
        self.s.set_expiry(1000)
        self.s.create()

        # remove folder
        shutil.rmtree(os.path.join(settings.UPLOADED_IMAGES_ROOT, self.s.session_key))

        # call the cleaner with False testing argument as, with testing=True, function returns instantly
        session_cleaner.session_clean(False)

        # check session is cleared
        self.assertTrue([s for s in Session.objects.get_queryset()] == [])

    def test_valid(self):
        # no expiry, with folder, nothing should be removed
        self.s["start"] = time.time()
        self.s.set_expiry(1000)
        self.s.create()

        # call the cleaner with False testing argument as, with testing=True, function returns instantly
        session_cleaner.session_clean(False)

        # check sessions in database is a list with the session key
        self.assertTrue([s.session_key for s in Session.objects.get_queryset()] == [self.s.session_key])

    def tearDown(self):
        if self.s.exists(self.s.session_key):
            self.s.flush()
