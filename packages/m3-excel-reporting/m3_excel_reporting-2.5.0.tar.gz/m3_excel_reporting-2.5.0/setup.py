# coding: utf-8
import os

from setuptools import (
    find_packages,
    setup,
)


def _read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()


setup(
    name='m3-excel-reporting',
    url='https://bitbucket.org/barsgroup/excel-reporting',
    license='MIT',
    author='BARS Group',
    author_email='bars@bars-open.ru',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    description=_read('DESCRIPTION.md'),
    install_requires=(
        'm3_django_compatibility>=1.12.0,<2',
        'django>=1.4,<5.0',
        'm3-builder>=1.0.1,<=1.2.0',
    ),
    long_description=_read('README.md'),
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Natural Language :: Russian',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Development Status :: 5 - Production/Stable',
    ],
    dependency_links=('http://pypi.bars-open.ru/simple/m3-builder',),
    setup_requires=('m3-builder>=1.0.1,<=1.2.0',),
    set_build_info=os.path.dirname(__file__),
)
