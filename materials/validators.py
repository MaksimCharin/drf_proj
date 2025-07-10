from rest_framework.serializers import ValidationError


class LinkValidator:
    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        link = value.get(self.field)
        if link and "youtube.com" not in link:
            raise ValidationError("Ссылки на сторонние ресурсы, кроме youtube.com, запрещены.")
