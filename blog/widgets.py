from django.forms.widgets import ClearableFileInput


class CustomClearableFileInput(ClearableFileInput):
    template_name = 'blog/custom_widget_templates/custom_clearable_file_input.html'
