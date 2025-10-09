# coding: utf-8
import os

from setuptools import (
    find_packages,
    setup,
)


setup(
    name='m3-users',
    url='https://github.com/barsgroup/m3-users',
    license='MIT',
    author='BARS Group',
    author_email='bars@bars-open.ru',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    description='Пользователи и роли',
    install_requires=(
        'm3-builder>=1.0.1',
        'm3_django_compatibility>=1.12.0',
        'm3-ui',
    ),
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Natural Language :: Russian',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 4.0',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: MIT License',
        'Development Status :: 5 - Production/Stable',
    ],
    dependency_links=('http://pypi.bars-open.ru/simple/m3-builder',),
    setup_requires=('m3-builder>=1.0.1',),
    set_build_info=os.path.dirname(__file__),
)
