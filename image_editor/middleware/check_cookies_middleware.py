from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin

"""
Cookie check works by:
If the cookiesenabled=true cookie isnt set, and there are no other cookies, set a test cookie
Return to a cookie check page (contains javascript to redirect page to www.domain.com/?a=verify)    TODO: make HTML redirect
On redirect to www.domain.com/?a=verify, server checks if there is the a=verify in url
If at url with a=verify, a test cookie should be set. If not, cookies are disabled. If test cookie is there, replace with cookiesenabled=true cookie
"""


class CookieCheckMiddleware(MiddlewareMixin):
    @staticmethod
    def process_request(r):
        # if there are cookies, don't process it anymore
        if len(r.COOKIES) != 0:
            return

        # NO COOKIES
        # if at verify page, and testcookie isn't set, ask to activate cookies
        if r.GET.get("a") == "verify":
            return render(r, "activateCookies.html")
        # if it isn't set, go to cookie check
        else:
            return render(r, "cookie_check.html")

    @staticmethod
    def process_response(r, response):
        if len(r.COOKIES) != 0:
            # if test cookie exists and we aren't trying to verify, delete it
            if r.COOKIES.get("testcookie") and not r.GET.get("a") == "verify":
                response.delete_cookie("testcookie")
            # if there is no cookiesenabled cookie, but cookies are set and we are trying to verify, then set the cookie
            if not r.COOKIES.get("cookiesenabled") and r.GET.get("a") == "verify":
                response.set_cookie("cookiesenabled", "true")
            # if session key doesn't exist, delete the sessionid cookie
            if not r.session.exists(r.session.session_key):
                response.delete_cookie("sessionid")
            return response

        response.set_cookie("testcookie", "true")
        return response
