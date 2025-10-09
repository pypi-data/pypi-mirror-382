# coding: utf-8
from setuptools import (
    find_packages,
    setup,
)


requirements_filename = 'requirements.txt'

requirements = []

with open(requirements_filename, 'r') as requirements_file:
    for rawline in requirements_file:
        line = rawline.strip()

        if not line.startswith('#'):
            requirements.append(line)


setup(
    name='edureception',
    author='BARS Group',
    description='Пакет "Приема специалиста"',
    classifiers=[
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Natural Language :: Russian',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 4.0',
        'Framework :: Django :: 4.2',
    ],
    url=('https://stash.bars-open.ru/projects/EDUBASE/repos/specialist_reception'),
    version='1.6.0',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    install_requires=requirements,
    include_package_data=True,
)
