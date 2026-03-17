from django.core.files.storage import FileSystemStorage
from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent.parent


class CustomStorage(FileSystemStorage):
    location = os.path.join(BASE_DIR, "media/uploads_model")
    base_url = "media/uploads_model/"