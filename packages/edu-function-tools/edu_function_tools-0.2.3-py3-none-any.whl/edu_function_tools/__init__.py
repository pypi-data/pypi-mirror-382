import django


if django.VERSION < (3, 2):
    default_app_config = 'edu_function_tools.apps.EduFunctionToolsConfig'
