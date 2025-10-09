# xl_dashboard/templatetags/xl_dashboard_tags.py

from django import template
from django.apps import apps
from django.conf import settings
from django.contrib.admin.sites import site as admin_site
from django.urls import reverse

register = template.Library()


@register.inclusion_tag('xl_dashboard/xl_dashboard.html', takes_context=True)
def show_xl_dashboard(context, side_menu_list=None):
    """Рендерит элементы XL Dashboard.

    По умолчанию строит разделы на основании настроек ``XL_DASHBOARD``.
    Если передать ``side_menu_list`` (результат ``get_side_menu`` из jazzmin),
    то для каждой установленной в админке модели будет создан свой элемент в
    том же стиле, что и для настроек ``XL_DASHBOARD``.
    
    Поддерживает два формата конфигурации:
    
    1. Простой формат (строка):
        XL_DASHBOARD = {
            'Users': {
                'Users': 'core.User',
                'Profiles': 'crm.Profile',
            }
        }
    
    2. Расширенный формат (словарь с настройками):
        XL_DASHBOARD = {
            'users_section': {  # ключ секции
                '__name__': 'Пользователи',  # отображаемое имя секции
                '__background__': '#ffee55',  # фоновый цвет секции
                'Users': 'core.User',
                'Profiles': {
                    'name': 'Профили',  # отображаемое имя элемента
                    'background': '#fe4',  # фоновый цвет элемента
                    'icon': '/static/images/profiles.png',  # иконка элемента
                    'model': 'crm.Profile',  # путь к модели
                },
            }
        }
    
    Вызывается в шаблоне как::

        {% load xl_dashboard_tags %}
        {% show_xl_dashboard %}               # из настроек
        {% show_xl_dashboard side_menu_list %}  # из списка приложений
    """
    sections: list[tuple[str, list[tuple[str, str, str | None, str | None]], str]] = []
    xl_dashboard = getattr(settings, 'XL_DASHBOARD', {}) or {}

    # Разделяем экшены и секции, чтобы явно понимать, есть ли пользовательские секции
    actions = xl_dashboard.get('xl-actions', {})
    xl_sections = [(k, v) for k, v in xl_dashboard.items() if k != 'xl-actions']

    if xl_sections:
        user = context['request'].user  # noqa
        for section_key, models_map in xl_sections:
            # Получаем настройки секции
            section_background = models_map.get('__background__', '#0003')
            section_name = models_map.get('__name__', section_key)  # Используем __name__ или ключ секции
            
            items = []
            for item_name, model_config in models_map.items():
                # Пропускаем служебные ключи
                if item_name.startswith('__'):
                    continue
                    
                # Обрабатываем конфигурацию элемента
                if isinstance(model_config, str):
                    # Простой формат: строка с путем к модели или URL
                    if model_config.startswith('/'):
                        # Если значение начинается с '/', считаем, что это готовая ссылка
                        admin_link = model_config
                        items.append((item_name, admin_link, None, None))
                        continue
                    try:
                        # Пытаемся получить модель через apps.get_model
                        try:
                            model = apps.get_model(model_config)
                        except LookupError:
                            # Если не получилось – пробуем импортировать напрямую
                            module_path, class_name = model_config.rsplit('.', 1)
                            mod = __import__(module_path, fromlist=[class_name])
                            model = getattr(mod, class_name)
                        # Если модель не зарегистрирована в админке, генерировать URL не получится
                        if model not in admin_site._registry:  # noqa
                            raise Exception('Model not registered in admin')
                        admin_link = reverse(
                            f'admin:{model._meta.app_label}_{model._meta.model_name}_changelist'  # noqa
                        )
                        items.append((item_name, admin_link, None, None))
                    except Exception as e:  # noqa
                        # print(f"Ошибка для модели {model_config}: {e}")  # Лог ошибки
                        items.append((item_name, '#invalid-model-path', None, None))
                elif isinstance(model_config, dict):
                    # Расширенный формат: словарь с настройками
                    model_path = model_config.get('model', '')
                    display_name = model_config.get('name', item_name)
                    background = model_config.get('background', None)
                    icon = model_config.get('icon', None)
                    
                    if model_path.startswith('/'):
                        # Если значение начинается с '/', считаем, что это готовая ссылка
                        admin_link = model_path
                        items.append((display_name, admin_link, background, icon))
                        continue
                    try:
                        # Пытаемся получить модель через apps.get_model
                        try:
                            model = apps.get_model(model_path)
                        except LookupError:
                            # Если не получилось – пробуем импортировать напрямую
                            module_path, class_name = model_path.rsplit('.', 1)
                            mod = __import__(module_path, fromlist=[class_name])
                            model = getattr(mod, class_name)
                        # Если модель не зарегистрирована в админке, генерировать URL не получится
                        if model not in admin_site._registry:  # noqa
                            raise Exception('Model not registered in admin')
                        admin_link = reverse(
                            f'admin:{model._meta.app_label}_{model._meta.model_name}_changelist'  # noqa
                        )
                        items.append((display_name, admin_link, background, icon))
                    except Exception as e:  # noqa
                        # print(f"Ошибка для модели {model_path}: {e}")  # Лог ошибки
                        items.append((display_name, '#invalid-model-path', background, icon))
                else:
                    items.append((item_name, '#unknown-type', None, None))
            sections.append((section_name, items, section_background))
    elif side_menu_list is not None:
        # Формируем список секций из доступных приложений и моделей

        # Добавляем ссылку на главную страницу админки
        sections.append(('Dashboard', [('Dashboard', reverse('admin:index'), None, None)], '#0003'))

        for app in side_menu_list:
            app_name = getattr(app, 'name', getattr(app, 'app_label', None))
            if app_name is None and isinstance(app, dict):
                app_name = app.get('name')

            models = getattr(app, 'models', None)
            if models is None and isinstance(app, dict):
                models = app.get('models', [])

            items = []
            for model in models or []:
                model_name = getattr(model, 'name', None)
                if model_name is None and isinstance(model, dict):
                    model_name = model.get('name')

                model_url = getattr(model, 'url', None)
                if model_url is None and isinstance(model, dict):
                    model_url = model.get('url')

                if model_url:
                    items.append((model_name, model_url, None, None))
                else:
                    items.append((model_name, '#', None, None))

            sections.append((app_name, items, '#0003'))

    return {
        'sections': sections,
        'actions': actions,
        'request': context['request']
    }
