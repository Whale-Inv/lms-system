import re

from rest_framework.exceptions import ValidationError


class LinkValidator:

    def __init__(self, field):
        self.field = field

    def __call__(self, value):

        reg = re.compile(
            r'^https?://(www\.)?(youtube\.com|youtu\.be)/'
            r'(watch\?v=|embed/)?([a-zA-Z0-9_-]{11})'
            r'(&.*)?$'
        )
        tmp_val = dict(value).get(self.field)
        if not bool(reg.match(tmp_val)):
            raise ValidationError("Ссылка на урок должна быть с youtube.com")
