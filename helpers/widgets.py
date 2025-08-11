from django.forms import widgets


class CkeditorWidget(widgets.Textarea):
    template_name = "widgets/ckeditor.html"


class DateWidget(widgets.DateInput):
    template_name = "widgets/date.html"


class ImageInput(widgets.ClearableFileInput):
    template_name = "widgets/image-input.html"

