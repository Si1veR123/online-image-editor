from django.test import TestCase, override_settings
from django.shortcuts import render
from django.http import HttpRequest, Http404
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from image_editor.custom_session import SessionStore
from django.contrib.sessions.models import Session
from io import BytesIO
from .. import views
from bs4 import BeautifulSoup
from PIL import Image
from re import match
import json
import numpy as np
import os
import time


IM_SIZE = (50, 50, 3)


class CustomReadRequest(HttpRequest):
    def __init__(self, read_data):
        self.read_data = read_data.encode()
        self.encoding = "utf-8"
        super().__init__()

    def read(self, *args, **kwargs):
        return self.read_data


def array_to_django_image(image_array: np.ndarray, im_format="JPEG") -> InMemoryUploadedFile:
    # get PIL.Image object from array
    image = Image.fromarray(image_array, mode="RGB")
    # get BytesIO object
    image_bytes = BytesIO()
    # save Image to BytesIO
    image.save(image_bytes, format=im_format)
    # get an InMemoryUploadedFile from BytesIO object as this is expected when uploading images through django
    image_obj = InMemoryUploadedFile(image_bytes, "image", "current", "image/*", len(image.tobytes()), None)
    # reset cursor to start of file as (i think) .tobytes() moves cursor to end of file
    image_bytes.seek(0)
    return image_obj


@override_settings(UPLOADED_IMAGES_ROOT=os.path.join(settings.BASE_DIR, 'test_uploaded_images'))
class TestViews(TestCase):
    """
    Tests the views file in the image_editor_app app
    """
    def setUp(self):
        self.r = HttpRequest()
        self.r.session = SessionStore()
        self.r.session["ip"] = "127.0.0.1"

    def test_ip_limit_check(self):
        """Test the ip limit checker"""
        # should be True as: '1' ips >= 5
        max_sessions = [{"ip": "1"}, {"ip": "1"}, {"ip": "1"}, {"ip": "1"}, {"ip": "1"}, {"ip": "0"}]
        self.assertTrue(views.check_if_ip_limit_reached(max_sessions, "1", 5))

        # should be False as: '1' ips < 5
        under_sessions = [{"ip": "1"}, {"ip": "1"}, {"ip": "1"}, {"ip": "1"}, {"ip": "0"}]
        self.assertFalse(views.check_if_ip_limit_reached(under_sessions, "1", 5))

    def test_edit_page(self):
        """Checks if user has active session, and returns editor, if not redirects to upload"""
        # with no session, should redirect to upload
        response = views.image_editor(self.r)
        self.assertTrue(response._headers["location"][-1] == reverse("uploadpage"))

        # with session, should return the editor
        self.r.session.create()
        response = views.image_editor(self.r)
        self.assertTrue(response.getvalue() == render(self.r, "image_editor_app/editor.html").getvalue())

    def test_upload_page_with_session(self):
        try:
            self.r.session.create()
            # set request headers so the ip should be 127.0.0.1
            self.r.META.update({
                'HTTP_X_FORWARDED_FOR': '127.0.0.1',
            })

            response = views.image_upload_page(self.r)

            response_parse = BeautifulSoup(response.getvalue(), "html.parser")
            upload_page_parser = BeautifulSoup(render(self.r, "image_editor_app/upload.html").getvalue(), "html.parser")

            self.assertTrue(response_parse.get_text, upload_page_parser.get_text)

            sessions = []

            # create sessions
            for _ in range(3):
                s = SessionStore()
                s["ip"] = "127.0.0.1"
                s.create()
                sessions.append(s)

            response = views.image_upload_page(self.r)
            self.assertTrue(response._headers["location"][-1] == reverse("uploadpage") + "?error=iplimit")
        finally:
            try:
                for s in sessions:
                    s.flush()
            except NameError:
                pass

    def test_im_upload(self):
        """test request method"""
        self.r.method = "GET"
        # should raise 404 when not using POST method
        self.assertRaises(Http404, views.image_upload_api, self.r)

        """test with valid session already created"""
        # test redirect to /edit if session exists
        self.r.session.create()
        self.r.method = "POST"
        response = views.image_upload_api(self.r)
        self.assertTrue(response._headers["location"][-1] == "/edit")
        self.r.session.flush()

        """test with normal image"""
        # create array of random pixels
        image_array = np.random.randint(0, 255, size=IM_SIZE)
        # get django image object
        image_obj = array_to_django_image(image_array)

        # modify request object to include image
        self.r.FILES = {"image": image_obj}
        # send through view
        response = views.image_upload_api(self.r)
        # check session is created
        self.assertTrue(self.r.session.exists(self.r.session.session_key))
        # check image is saved
        path = os.path.join(settings.UPLOADED_IMAGES_ROOT, self.r.session.session_key, "current.jpeg")
        self.assertTrue(os.path.exists(path))
        # check response is a redirect to /edit
        self.assertTrue(response._headers["location"][-1] == "/edit")
        # flush session
        self.r.session.flush()

        """test invalid file type"""
        # create array of random pixels
        image_array = np.random.randint(0, 255, size=IM_SIZE)
        # get django image object
        image_obj = array_to_django_image(image_array, im_format="BMP")
        # modify request object to include image
        self.r.FILES = {"image": image_obj}
        # send through view
        response = views.image_upload_api(self.r)
        # check response is a redirect to /edit/upload?error=format
        self.assertTrue(response._headers["location"][-1] == "/edit/upload?error=format")

        """test max file size"""
        # read image in binary mode into a BytesIO object
        # MUST BE IMAGE LARGER THAN MAX SIZE, THIS ONE IS 3000x3000
        path = os.path.join(settings.BASE_DIR, "image_editor_app", "tests_image_app", "test_large_image.jpg")
        with open(path, "rb") as f:
            bytes_obj = BytesIO(f.read())
        # get django image object
        image_obj = InMemoryUploadedFile(bytes_obj, "image", "current", "image/*", len(bytes_obj.getvalue()), None)
        bytes_obj.seek(0)
        # modify request object to include image
        self.r.FILES = {"image": image_obj}
        # send through view
        response = views.image_upload_api(self.r)
        self.assertTrue(response._headers["location"][-1] == "/edit/upload?error=size")

    def test_get_image_link(self):
        """test that requesting a image link from api without session returns Invalid Session error"""
        error_response = views.get_image_link_api(self.r)
        # get json value, parse and get 'error' key, check it is 'Invalid Session'
        self.assertTrue(json.loads(error_response.getvalue())["error"] == "Invalid session.")

        """test that given link is correct with a valid session"""
        # create a session
        self.r.session.create()
        # set session image type
        self.r.session["type"] = ".jpeg"
        # get link from json
        link = json.loads(views.get_image_link_api(self.r).getvalue())["imageLink"]
        # regex for the link (  anything, session_key/current., any 3 or 4 characters (file extension)  )
        link_regex = ".*/" + self.r.session.session_key + "/current\.[a-z]{3,4}"
        # check match is not none
        self.assertIsNotNone(match(link_regex, link))

    def test_delete_api(self):
        self.r.session.create()
        response = views.delete_session(self.r)

        self.assertFalse(self.r.session.exists(self.r.session.session_key))
        self.assertTrue(response._headers["location"][-1] == "/edit")

    def test_perform_action(self):
        # json data for edit
        data = {"type": "rotate", "data": "1"}
        # create custom request object that returns the json data when read from
        self.r = CustomReadRequest(json.dumps(data))
        # create session object
        self.r.session = SessionStore()
        self.r.session["ip"] = "127.0.0.1"
        self.r.session["last"] = time.time()
        self.r.session["type"] = ".jpeg"
        self.r.session.create()

        """test only works with POST"""
        # check raises Http404 when not using POST
        self.assertRaises(Http404, views.perform_action, self.r)
        # set method to POST
        self.r.method = "POST"

        """test time throttling"""
        # check that number of edits is throttled
        self.r.session["last"] = time.time()
        self.assertTrue(json.loads(views.perform_action(self.r).getvalue())["error-type"] == "time")
        self.r.session["last"] = 0

        """test normal request"""
        # path of 'current.jpeg' image
        current_root = os.path.join(settings.UPLOADED_IMAGES_ROOT, self.r.session.session_key, "current.jpeg")
        # create random image
        image_array = np.random.randint(0, 255, size=(5, 10, 3))
        # save random image
        Image.fromarray(image_array, mode="RGB").save(current_root, format="JPEG")

        # get response
        response = views.perform_action(self.r)

        # regex for the link (  anything, session_key/current., any 3 or 4 characters (file extension)  )
        link_regex = ".*/" + self.r.session.session_key + "/current\.[a-z]{3,4}"
        link = json.loads(response.getvalue())["imageLink"]
        # check given link is correct against regex
        self.assertIsNotNone(match(link_regex, link))

        # check image has been rotated
        self.assertTrue(np.array(Image.open(current_root)).shape == (10, 5, 3))

        self.r.session.flush()

        """test incorrect json"""
        # incorrect json data for edit
        data = {"incorrectjson": "incorrect"}
        # create custom request object that returns the json data when read from
        self.r = CustomReadRequest(json.dumps(data))
        # create session object
        self.r.session = SessionStore()
        # set settings
        self.r.session["ip"] = "127.0.0.1"
        self.r.session["last"] = 0
        self.r.session["type"] = ".jpeg"
        self.r.session.create()
        self.r.method = "POST"

        # check error due to incorrect json
        self.assertTrue(json.loads(views.perform_action(self.r).getvalue())["type"] == "error")

        """test only works with valid session"""
        self.r.session.flush()
        self.assertRaises(Http404, views.perform_action, self.r)

    def test_remove_session(self):
        # set ip in request headers
        self.r.META.update({
            'HTTP_X_FORWARDED_FOR': '127.0.0.1',
        })

        # session ips to populate database with
        ips = ["127.0.0.1", "127.0.0.1", "0"]

        # in try, finally block to remove all sessions in case an error occurs
        try:
            # create other sessions
            sessions = []
            for ip in ips:
                s = SessionStore()
                s["ip"] = ip
                s.create()
                sessions.append(s)

            # send through view
            response = views.remove_session(self.r)
            # check for success
            self.assertTrue(json.loads(response.getvalue())["status"] == "success")
            # get all remaining ips
            all_ips = [s.get_decoded()["ip"] for s in Session.objects.get_queryset()]
            # check that 1 ip has been removed
            self.assertTrue(len(all_ips) == len(ips) - 1)
            # there should be 1 '127.0.0.1' and 1 '0' ip left
            self.assertTrue("127.0.0.1" in all_ips)
            self.assertTrue("0" in all_ips)

        finally:
            # clear other sessions
            for s in sessions:
                s.flush()

    def tearDown(self):
        if self.r.session.exists(self.r.session.session_key):
            self.r.session.flush()
