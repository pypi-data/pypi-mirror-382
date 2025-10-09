import os
import sys

CURRENT_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.dirname(CURRENT_DIR)
PROJECT_DIR = os.path.join(CURRENT_DIR, 'project')
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, PROJECT_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

import django
from django.test import RequestFactory, override_settings

django.setup()

from xldashboard.templatetags.xl_dashboard_tags import show_xl_dashboard


def _dummy_user():
    class DummyUser:
        is_authenticated = True
    return DummyUser()


def test_show_xl_dashboard_uses_settings_order_and_names():
    rf = RequestFactory()
    request = rf.get('/')
    request.user = _dummy_user()

    dashboard = {
        'Events': {
            'Profiles': '/profiles/',
            'Events': '/events/',
            'Demo keys': '/demo/',
            'Host keys': '/host/',
        }
    }

    side_menu_list = [
        {
            'name': 'Wrong',
            'models': [
                {'name': 'Bad1', 'url': '/bad1/'},
                {'name': 'Bad2', 'url': '/bad2/'},
            ],
        }
    ]

    with override_settings(XL_DASHBOARD=dashboard):
        result = show_xl_dashboard({'request': request}, side_menu_list)

    assert [sec[0] for sec in result['sections']] == ['Events']
    assert [name for name, _, _, _ in result['sections'][0][1]] == [
        'Profiles',
        'Events',
        'Demo keys',
        'Host keys',
    ]


def test_show_xl_dashboard_preserves_multiple_section_order():
    rf = RequestFactory()
    request = rf.get('/')
    request.user = _dummy_user()

    dashboard = {
        'General': {
            'Users': '/users/',
            'Social links': '/social-links/',
        },
        'Events': {
            'Profiles': '/profiles/',
            'Events': '/events/',
        },
    }

    with override_settings(XL_DASHBOARD=dashboard):
        result = show_xl_dashboard({'request': request}, [])

    assert [sec[0] for sec in result['sections']] == ['General', 'Events']
    assert [name for name, _, _, _ in result['sections'][0][1]] == ['Users', 'Social links']
    assert [name for name, _, _, _ in result['sections'][1][1]] == ['Profiles', 'Events']


def test_show_xl_dashboard_uses_custom_names_for_model_paths():
    rf = RequestFactory()
    request = rf.get('/')
    request.user = _dummy_user()

    dashboard = {
        'General': {
            'Account users': 'app.User',
        }
    }

    with override_settings(XL_DASHBOARD=dashboard):
        result = show_xl_dashboard({'request': request}, [])

    assert result['sections'][0][1][0][0] == 'Account users'


def test_show_xl_dashboard_supports_extended_format():
    """Тест поддержки расширенного формата конфигурации с фонами и иконками."""
    rf = RequestFactory()
    request = rf.get('/')
    request.user = _dummy_user()

    dashboard = {
        'Users': {
            '__background__': '#ffee55',
            'Users': 'core.User',
            'Profiles': {
                'name': 'Profiles',
                'background': '#fe4',
                'icon': '/static/images/profiles.png',
                'model': 'crm.Profile',
            },
            'Organizations': 'crm.Organization',
        },
        'Clients': {
            '__background__': '#55eeff',
            'Clients': 'crm.Client',
            'Regions': 'crm.Region',
        }
    }

    with override_settings(XL_DASHBOARD=dashboard):
        result = show_xl_dashboard({'request': request}, [])

    # Проверяем, что секции созданы
    assert len(result['sections']) == 2
    assert result['sections'][0][0] == 'Users'
    assert result['sections'][1][0] == 'Clients'
    
    # Проверяем фоновые цвета секций
    assert result['sections'][0][2] == '#ffee55'  # Users section background
    assert result['sections'][1][2] == '#55eeff'  # Clients section background
    
    # Проверяем элементы секции Users
    users_items = result['sections'][0][1]
    assert len(users_items) == 3
    
    # Users - простой формат
    assert users_items[0] == ('Users', '#invalid-model-path', None, None)
    
    # Profiles - расширенный формат
    assert users_items[1] == ('Profiles', '#invalid-model-path', '#fe4', '/static/images/profiles.png')
    
    # Organizations - простой формат
    assert users_items[2] == ('Organizations', '#invalid-model-path', None, None)


def test_show_xl_dashboard_mixed_format():
    """Тест смешанного формата - простые строки и расширенные словари."""
    rf = RequestFactory()
    request = rf.get('/')
    request.user = _dummy_user()

    dashboard = {
        'Mixed': {
            '__background__': '#ff0000',
            'Simple': '/admin/simple/',
            'Extended': {
                'name': 'Extended Model',
                'background': '#00ff00',
                'icon': '/static/icon.png',
                'model': 'app.Model',
            },
            'Direct': '/admin/direct/',
        }
    }

    with override_settings(XL_DASHBOARD=dashboard):
        result = show_xl_dashboard({'request': request}, [])

    assert len(result['sections']) == 1
    section = result['sections'][0]
    assert section[0] == 'Mixed'
    assert section[2] == '#ff0000'  # section background
    
    items = section[1]
    assert len(items) == 3
    
    # Simple - прямая ссылка
    assert items[0] == ('Simple', '/admin/simple/', None, None)
    
    # Extended - расширенный формат
    assert items[1] == ('Extended Model', '#invalid-model-path', '#00ff00', '/static/icon.png')
    
    # Direct - прямая ссылка
    assert items[2] == ('Direct', '/admin/direct/', None, None)


def test_show_xl_dashboard_section_name_override():
    """Тест переопределения имени секции через __name__."""
    rf = RequestFactory()
    request = rf.get('/')
    request.user = _dummy_user()

    dashboard = {
        'users_section': {  # ключ секции
            '__name__': 'Пользователи и профили',  # отображаемое имя
            '__background__': '#ffaa00',
            'Users': 'core.User',
            'Profiles': 'crm.Profile',
        },
        'clients_section': {  # ключ секции без __name__
            '__background__': '#00aaff',
            'Clients': 'crm.Client',
        }
    }

    with override_settings(XL_DASHBOARD=dashboard):
        result = show_xl_dashboard({'request': request}, [])

    assert len(result['sections']) == 2
    
    # Первая секция - с переопределенным именем
    assert result['sections'][0][0] == 'Пользователи и профили'  # отображаемое имя
    assert result['sections'][0][2] == '#ffaa00'  # фоновый цвет
    
    # Вторая секция - без переопределения имени
    assert result['sections'][1][0] == 'clients_section'  # ключ секции как имя
    assert result['sections'][1][2] == '#00aaff'  # фоновый цвет
