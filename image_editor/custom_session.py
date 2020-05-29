from django.contrib.sessions.backends.db import SessionStore as DjangoDBSessionStore
from django.conf import settings
import os
import shutil


class SessionStore(DjangoDBSessionStore):
    """Custom session store to override delete and create method. Adds behavior for removing folder from
    uploaded_images folder and creating folder
    """
    def delete(self, session_key=None):
        # if there is a session key
        if self.session_key:
            try:
                # try to remove the images
                path = os.path.join(settings.UPLOADED_IMAGES_ROOT, self.session_key)
                shutil.rmtree(path, ignore_errors=True)
            except FileNotFoundError:
                pass
        # run default delete method (removes from database)
        super().delete(session_key)

    def create(self):
        super().create()
        path = os.path.join(settings.UPLOADED_IMAGES_ROOT, self.session_key)

        try:
            # make directory for session
            os.mkdir(path)

            # make undo directory for session
            os.mkdir(os.path.join(path, "undo"))

            # make redo directory for session
            os.mkdir(os.path.join(path, "redo"))
        except FileExistsError:
            raise
