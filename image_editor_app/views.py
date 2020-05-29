from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404, JsonResponse, HttpResponse
from django.contrib.sessions.models import Session
from image_editor.custom_session import SessionStore
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from . import session_cleaner
from . import image_edits
from io import BytesIO
from PIL import Image
from ipware.ip2 import get_client_ip
import os, time, json

# roughly 5mb, divided by 2 as warning is raised when over max pixels, but error is raised when over double max pixels
# we need an error to catch it
MAX_SIZE = 5_242_880 / 2
Image.MAX_IMAGE_PIXELS = MAX_SIZE
IP_LIMIT = 2


def check_if_ip_limit_reached(sessions, ip, limit):
    """Checks if iplimit is reached from session list, ip and limit"""
    count = 0
    for s in sessions:
        if s["ip"] == ip:
            count += 1
        if count >= limit:
            return True
    return False

# Create your views here.


def image_editor(r):
    """redirects to upload page if session isn't available, or goes to editor"""
    if r.session.exists(r.session.session_key) and os.path.exists(os.path.join(settings.UPLOADED_IMAGES_ROOT, r.session.session_key)):
        # if a session cookie is available send to editor
        r.session["last"] = time.time()
        return render(r, "image_editor_app/editor.html")
    else:
        # send to upload page
        return redirect("/edit/upload")


def image_upload_page(r):
    """returns upload page, checks ip limit"""
    if r.GET.get("error") != "iplimit":
        # get all sessions
        sessions = Session.objects.get_queryset()
        sessions_data = [s.get_decoded() for s in sessions]

        # get clients ip, returns tuple with ip as first element
        client_ip, _ = get_client_ip(r)

        limit_reached = check_if_ip_limit_reached(sessions_data, client_ip, IP_LIMIT)
        # check ip limit reached? if yes, show ip error
        if limit_reached:
            return redirect("/edit/upload?error=iplimit")
        # no error, upload page
    return render(r, "image_editor_app/upload.html", {"error": r.GET.get("error", "")})


def image_upload_api(r):
    """POST requests sent here with images, creates session and checks image"""
    if r.method == "POST":
        if r.session.exists(r.session.session_key) and os.path.exists(os.path.join(settings.UPLOADED_IMAGES_ROOT, r.session.session_key)):
            # if session key exists, redirect to edit page
            return redirect("/edit")
        # image from request
        im = r.FILES.get("image")
        # if no image, redirect to edit
        if not im:
            return redirect("/edit")

        # try to open image, if format error, redirect to error page
        try:
            pil_im = Image.open(BytesIO(im.read()))
        except Image.DecompressionBombError:
            return redirect("/edit/upload?error=size")
        except Image.UnidentifiedImageError:
            return redirect("/edit/upload?error=format")

        file_suffix = "." + pil_im.format.lower()

        # check file extension is jpeg, jpg or png
        if file_suffix not in [".jpeg", ".jpg", ".png"]:
            return redirect("/edit/upload?error=format")

        # check if file is damaged
        try:
            pil_im.verify()
        except:
            return redirect("/edit/upload?error=damaged")

        # create new, unique session token and folders
        r.session.create()
        try:
            # save image
            path = os.path.join(settings.UPLOADED_IMAGES_ROOT, r.session.session_key)
            fs = FileSystemStorage(location=path, base_url=settings.UPLOADED_IMAGES_URL)
            fs.save("current" + file_suffix, im)
        except FileExistsError:
            r.session.flush()
            return redirect("/edit/upload?error=server")

        r.session["last"] = 0
        r.session["start"] = time.time()
        r.session["ip"] = get_client_ip(r)
        r.session.set_expiry(604_800)  # 1 week
        r.session["type"] = file_suffix

        return redirect("/edit")
    else:
        raise Http404


def get_image(r):
    if r.session.exists(r.session.session_key):
        path = os.path.join(settings.UPLOADED_IMAGES_ROOT, r.session.session_key, "current" + r.session["type"])
        with open(path, "rb") as f:
            data = f.read()
        return HttpResponse(data, content_type="image/*")
    else:
        raise Http404


def delete_session(r):
    """deletes session from db and deletes images"""
    r.session.flush()
    return redirect("/edit")


edits = {
    "undo": image_edits.undo,
    "redo": image_edits.redo,
    "crop": image_edits.crop,
    "rotate": image_edits.rotate,
    "adjust": image_edits.adjust,
}


@csrf_exempt
def perform_action(r):
    """Performs an edit"""
    if r.method == "POST" and r.session.exists(r.session.session_key):
        # throttles edits to 1 every 3 seconds
        if r.session["last"] + 3 > time.time():
            return JsonResponse({"type": "error", "error": "Please wait 3 seconds between edits.", "error-type": "time"})
        r.session["last"] = time.time()

        # get data from request by decoding and parsing JSON
        request_data = json.loads(r.read().decode(r.encoding))

        # perform the edit
        try:
            edits[request_data["type"]](r, request_data)
        except (ValueError, KeyError):
            # return error
            return JsonResponse({"type": "error", "error": "A server error occured! Error 502."})

        # create and return new link
        link = "/image?" + str(round(time.time()))
        return JsonResponse({"type": "link", "imageLink": link})
    else:
        raise Http404


@csrf_exempt
def remove_session(r):
    """Removes session from same ip"""
    # removes another session from same ip
    try:
        # get ip
        ip, _ = get_client_ip(r)

        # iterate over sessions
        for s in Session.objects.iterator():
            # decode session data
            decoded = s.get_decoded()
            # if session's ip is clients ip, remove it and break from loop
            if decoded["ip"] == ip:
                SessionStore(s.session_key).flush()
                return JsonResponse({"status": "success"})
        return JsonResponse({"status": "fail"})
    except:
        return JsonResponse({"status": "fail"})
