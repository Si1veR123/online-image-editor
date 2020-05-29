from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings
from django.contrib.sessions.models import Session
from image_editor.custom_session import SessionStore
import os
import shutil
import time


def session_clean(testing=True):
    """Runs at set periods, cleans session images and database"""
    if settings.TESTING and testing:
        return
    print("\n\tRUNNING CLEAN")
    max_time = 1_209_600 # 2 weeks
    # clear expired
    SessionStore.clear_expired()
    print("\tCLEARED EXPIRED 1 WEEK AFTER INACTIVITY")
    cleared_after_max_time = []
    cleared_if_no_folder = []
    # get queryset to iterate over sessions
    sessions = Session.objects.get_queryset()
    for s in sessions:
        # clear after max_time
        if s.get_decoded()["start"] + max_time < time.time():
            SessionStore(s.session_key).flush()
            cleared_after_max_time.append(s.session_key)
        # if folder doesn't exist
        if not os.path.exists(os.path.join(settings.UPLOADED_IMAGES_ROOT, s.session_key)):
            cleared_if_no_folder.append(s.session_key)
            SessionStore(s.session_key).flush()

    cleared_folders = []
    session_keys = [s.session_key for s in sessions] # all session keys

    for session_folder in [x for x in os.walk(settings.UPLOADED_IMAGES_ROOT)][0][1]:
        # clear if folder does not have session key
        if session_folder not in session_keys:
            path = os.path.join(settings.UPLOADED_IMAGES_ROOT, session_folder)
            shutil.rmtree(path)
            cleared_folders.append(session_folder)

    # output clear details
    print(f"""\tCleared after {max_time} seconds: {cleared_after_max_time}
    \tCleared because it had no folder: {cleared_if_no_folder}
    \tCleared because folder had no key in database: {cleared_folders}
    \tSessions in database: {len(session_keys)}\n""")


# clears all session keys and images
def clear_all():
    sessions = Session.objects.get_queryset()
    for s in sessions:
        SessionStore(s.session_key).flush()

    for session_folder in [x for x in os.walk(settings.UPLOADED_IMAGES_ROOT)][0][1]:
        path = os.path.join(settings.UPLOADED_IMAGES_ROOT, session_folder)
        shutil.rmtree(path)


scheduler = BackgroundScheduler()
# run cleaner every 10 mins
scheduler.add_job(session_clean, 'interval', seconds=600, max_instances=1)
# run full clear every month
scheduler.add_job(clear_all, 'cron', day="last", max_instances=1)
scheduler.start()
