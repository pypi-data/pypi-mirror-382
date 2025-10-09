#coding: utf-8
"""
File: app_meta.py
Author: Rinat F Sabitov
Description:
"""


import controller
import actions
from m3_ext.ui.app_ui import DesktopLoader, DesktopLauncher, DesktopLaunchGroup
from django.conf import urls



def register_urlpatterns():
    """
    Регистрация конфигурации урлов для приложения
    """
    return urls.defaults.patterns(
        "",
        (r"^excelreporting/", controller.action_controller.process_request),
    )


def register_desktop_menu():
    rosters = DesktopLaunchGroup(name=u"Отчеты excelreporting")

    for action in controller.action_controller.find_pack(actions.DemoExcelReporingActionPack).reports_list:
        rosters.subitems.append(DesktopLauncher(name=action.title, url=action.get_absolute_url()))

    DesktopLoader.add('', DesktopLoader.START_MENU, rosters)


def register_actions():
    """
    Метод регистрации Action'ов для приложения в котором описан
    """
    controller.action_controller.packs.append(actions.DemoExcelReporingActionPack())

