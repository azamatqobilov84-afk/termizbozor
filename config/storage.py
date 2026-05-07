"""
ImageKit.io uchun maxsus Django storage class.
Vercel'da rasm yuklash uchun ishlatiladi.
"""
import os
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from imagekitio import ImageKit


@deconstructible
class ImageKitStorage(Storage):
    def __init__(self):
        self.imagekit = ImageKit(
            public_key=os.environ.get('IMAGEKIT_PUBLIC_KEY'),
            private_key=os.environ.get('IMAGEKIT_PRIVATE_KEY'),
            url_endpoint=os.environ.get('IMAGEKIT_URL_ENDPOINT'),
        )
        self.url_endpoint = os.environ.get('IMAGEKIT_URL_ENDPOINT', '').rstrip('/')

    def _save(self, name, content):
        """Faylni ImageKit'ga yuklaydi"""
        content.seek(0)
        file_data = content.read()

        result = self.imagekit.upload_file(
            file=file_data,
            file_name=os.path.basename(name),
            options={
                "folder": os.path.dirname(name) or "/",
                "use_unique_file_name": True,
            }
        )

        if hasattr(result, 'url') and result.url:
            return result.url
        if hasattr(result, 'response_metadata'):
            return result.response_metadata.raw.get('url', name)
        return name

    def url(self, name):
        """Rasm uchun to'liq URL qaytaradi"""
        if not name:
            return ''
        if name.startswith('http'):
            return name
        return f"{self.url_endpoint}/{name.lstrip('/')}"

    def exists(self, name):
        return False

    def delete(self, name):
        pass

    def size(self, name):
        return 0