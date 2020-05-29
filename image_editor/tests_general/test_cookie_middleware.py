from django.test import TestCase
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from ..middleware.check_cookies_middleware import CookieCheckMiddleware
from bs4 import BeautifulSoup


class CustomSession:
    def __init__(self, should_exist: bool):
        self.session_key = "test"
        self.should_exist = should_exist

    def exists(self, _):
        return self.should_exist


class CookieMiddlewareTest(TestCase):
    """
    Test suite for the cookie check middleware
    Expected: With no cookies and no GET data, send to cookie check page (test cookie should be set)
              With no cookies but GET data: a=verify, send to activate cookie page
              With cookies, send to normal page
              With cookies and GET, send to normal page
              Invalid session IDs are removed
              testcookie is removed if present with other cookies
              cookiesenabled should be set on verify page when cookies are present
    """
    def setUp(self):
        self.r = HttpRequest()
        self.set_session_id = False
        self.r.session = CustomSession(should_exist=True)

    def process_middleware(self) -> HttpResponse:
        # send request and response through middleware
        returned = CookieCheckMiddleware.process_request(self.r)
        # if returned is a response, use that in process_response. If not make a new response object
        if isinstance(returned, HttpResponse):
            response = returned
        else:
            response = HttpResponse()
        if self.set_session_id:
            response.set_cookie("sessionid", "test")
        response = CookieCheckMiddleware.process_response(self.r, response)
        return response

    def test_no_cookies_no_get(self):
        """
        Test that testcookie is set when current cookies and GET is empty
        """
        # set cookies and GET data to empty
        self.r.COOKIES = {}
        self.r.GET = {}

        response = self.process_middleware()

        # check that test cookie is present in response
        self.assertTrue([cookie for cookie in response.cookies.keys() if cookie == "testcookie"])

        # check that page is on cookie check by parsing html, and getting meta tag that contains a description
        self.parser = BeautifulSoup(str(response.getvalue()), "html.parser")
        self.assertTrue(self.parser.find("meta", {"id": "page-info"}).attrs["content"] == "cookiecheck")

    def test_no_cookies(self):
        """Test that you are redirected to activate cookie page when going to a=verify without cookies"""
        self.r.COOKIES = {}
        self.r.GET = {"a": "verify"}

        response = self.process_middleware()

        # check that page is on cookie check by parsing html, and getting meta tag that contains a description
        self.parser = BeautifulSoup(str(response.getvalue()), "html.parser")
        self.assertTrue(self.parser.find("meta", {"id": "page-info"}).attrs["content"] == "activatecookie")

    def test_cookies_and_get(self):
        """Test that request is unchanged by middleware when there are cookies are present, even with GET: a=verify"""
        self.r.COOKIES = {"randomcookie": "randomvalue"}
        self.r.GET = {"a": "verify"}

        response = self.process_middleware()

        # the content should be empty. This is because a page should be untouched if cookies are present.
        self.assertFalse(response.content)

    def test_cookies(self):
        """Test that request is unchanged by middleware when there are cookies are present"""
        self.r.COOKIES = {"randomcookie": "randomvalue"}
        self.r.GET = {}

        response = self.process_middleware()

        # the content should be empty. This is because a page should be untouched if cookies are present.
        self.assertFalse(response.content)

    def test_invalid_session_removed(self):
        """Test that sessionid is removed if it doesn't exist"""
        # set the CustomSession's should_exist False so it should be removed
        self.r.session.should_exist = False
        self.r.COOKIES = {"randomcookie": "randomvalue"}
        self.r.GET = {}

        # tells middleware process function to set a sessionid cookie to the response, before it is processed
        self.set_session_id = True
        response = self.process_middleware()

        # check that max age of sessionid is 0 (deleted)
        self.assertTrue(response.cookies.get("sessionid").get("max-age") == 0)

    def test_testcookie_removed(self):
        """
        Test that testcookie is removed when not verifying.
        """
        self.r.COOKIES = {"testcookie": "true"}
        self.r.GET = {}

        response = self.process_middleware()

        # check that max age of testcookie is 0 (deleted)
        self.assertTrue(response.cookies.get("testcookie").get("max-age") == 0)

    def test_cookiesenabled_set(self):
        """Test that cookieenabled is set when verifying and other cookies present"""
        self.r.COOKIES = {"testcookie": "true"}
        self.r.GET = {"a": "verify"}

        response = self.process_middleware()

        # check cookiesenabled exists
        self.assertTrue(response.cookies.get("cookiesenabled"))
