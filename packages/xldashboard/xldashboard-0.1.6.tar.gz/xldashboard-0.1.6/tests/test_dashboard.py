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
    assert [name for name, _ in result['sections'][0][1]] == [
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
    assert [name for name, _ in result['sections'][0][1]] == ['Users', 'Social links']
    assert [name for name, _ in result['sections'][1][1]] == ['Profiles', 'Events']


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
