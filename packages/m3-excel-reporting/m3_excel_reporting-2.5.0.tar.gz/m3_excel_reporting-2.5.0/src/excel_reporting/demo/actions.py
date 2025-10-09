#coding: utf-8

"""
File: actions.py
Author: Rinat F Sabitov
Description:
"""

import os
import uuid
import tempfile
from django.conf import settings
from m3.actions import Action, ActionPack, OperationResult
from excel_reporting import report_gen


class DemoExcelReporingActionPack(ActionPack):
    r"""Действие для зарегистрированных отчетов."""
    url = r"/registered-reports"
    shortname = "reports-registered-action-pack"
    title = 'Отчеты excelreporting'


    def __init__(self):
        super(DemoExcelReporingActionPack, self).__init__()
        self.reports_list = [
            ExampleReportAction(),
        ]

        self.actions.extend(self.reports_list)

class Generator(report_gen.BaseReport):
    template = 'example-template.xls'
    template_name = os.path.abspath(os.path.join(os.path.dirname(__file__), template))
    result_name = os.path.join(settings.MEDIA_ROOT, "%s.xls" % str(uuid.uuid4())[0:16])


    def get_fake_data(self, count):
        import random
        import string

        return [{
            u'Номер':idx,
            u'Код':''.join(random.sample((string.ascii_uppercase+string.digits)*4,4)),
            u'Имя':''.join(random.sample(string.ascii_lowercase*6,6))
        } for idx in range(count)]


    def collect(self, *args, **kwargs):
        result = {u'ПримерДанных': self.get_fake_data(25)}
        return result


class ExampleReportAction(Action):
    title = u'Пример отчета'
    url = '/example-report$'

    def _to_url(self, filename):
        return os.path.join(settings.MEDIA_URL, os.path.split(filename)[1])

    def run(self, request, context):
        generator = Generator()
        generator.make_report()
        return OperationResult(code="function(){location.href='%s';}" \
                               % self._to_url(generator.result_name))
