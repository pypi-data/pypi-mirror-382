from django import forms
from django.core.files.base import ContentFile
from PIL import Image
from io import BytesIO

class ThumbnailImageFormField(forms.ImageField):
    def __init__(self, output_format='WEBP', quality=70, *args, **kwargs):
        self.output_format = output_format.upper()
        self.quality = max(1, min(quality, 100))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        file = super().clean(data, initial)
        if not file:
            return initial
        if not initial or getattr(file, 'name', '') != getattr(initial, 'name', ''):
            processed = self._process_image(file)
            name = f"{file.name.rsplit('.', 1)[0]}.{self.output_format.lower()}"
            file = ContentFile(processed.getvalue(), name=name)
        return file

    def _process_image(self, file):
        img = Image.open(file)
        fmt = self.output_format
        if fmt == 'JPEG':
            img = img.convert('RGB')
        else:
            img = img.convert('RGBA')
        buf = BytesIO()
        opts = {'JPEG': dict(format='JPEG', quality=self.quality, optimize=True, progressive=True), 'WEBP': dict(format='WEBP', quality=self.quality, method=6, lossless=False), 'PNG':  dict(format='PNG', optimize=True, compress_level=9 - self.quality // 10), 'GIF':  dict(format='GIF', optimize=True, save_all=False) }.get(fmt, dict(format=fmt, quality=self.quality))
        img.save(buf, **opts)
        buf.seek(0)
        return buf