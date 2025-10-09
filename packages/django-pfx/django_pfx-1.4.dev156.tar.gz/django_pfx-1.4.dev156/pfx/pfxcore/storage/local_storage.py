import hashlib
import logging
from pathlib import Path

from django.http import FileResponse

from pfx.pfxcore.shortcuts import settings

logger = logging.getLogger(__name__)


class LocalStorage:
    direct = True

    def to_python(self, value):
        return value

    def get_url(self, request, key):
        return Path(settings.STORAGE_LOCAL_ROOT, key)

    def upload(self, key, file, **kwargs):
        key_list = key.split('/')
        filename = key_list[-1]
        relative_path = Path(*key_list[:-1])
        dirname = Path(settings.STORAGE_LOCAL_ROOT, relative_path)
        dirname.mkdir(parents=True, exist_ok=True)
        ext = ''.join(filename.partition('.')[-2:])
        hashname = f'{hashlib.sha1(file).hexdigest()}{ext}'
        final_key = str(Path(relative_path, hashname))
        with open(Path(dirname, hashname), 'wb') as f:
            f.write(file)
        with open(Path(dirname, hashname), 'rb') as f:
            response = FileResponse(
                f, as_attachment=True, filename=filename)
            return {
                'key': final_key,
                'name': filename,
                'content-length': response.get('Content-Length'),
                'content-type': response.get('Content-Type'),
            }

    def delete(self, value):
        if not value or 'key' not in value:
            return value  # pragma: no cover
        path = Path(settings.STORAGE_LOCAL_ROOT, value['key'])
        path.unlink(missing_ok=True)
        while True:
            path = path.parent
            if path == Path(settings.STORAGE_LOCAL_ROOT):
                break
            if not path.exists():
                break
            if any(path.iterdir()):
                break
            try:
                path.rmdir()
            except FileNotFoundError:
                pass
