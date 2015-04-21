from django.core.files.storage import FileSystemStorage

from django.conf import settings

fs = FileSystemStorage(location=settings.CURR_STORAGE_PATH)
