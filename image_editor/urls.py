from django.urls import path
from .settings import MEDIA_ROOT, MEDIA_URL, BASE_DIR, UPLOADED_IMAGES_ROOT, UPLOADED_IMAGES_URL
from django.conf.urls.static import static
import image_editor_app.views, os
import image_editor.views

urlpatterns = [
    path("", image_editor.views.home),
    path("image", image_editor_app.views.get_image),
    path("faq", image_editor.views.faq),
    path("edit", image_editor_app.views.image_editor),
    path("edit/upload", image_editor_app.views.image_upload_page, name="uploadpage"),
    path("edit/close", image_editor_app.views.delete_session),
    path("edit/api/upload", image_editor_app.views.image_upload_api),
    path("edit/api/makeEdit", image_editor_app.views.perform_action),
    path("edit/api/remsession", image_editor_app.views.remove_session),
]
urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)
urlpatterns += static(UPLOADED_IMAGES_URL, document_root=os.path.join(BASE_DIR, UPLOADED_IMAGES_ROOT))
