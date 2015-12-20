import os

import setuptools

# I'm going to just give exact versions that I know will work
requires = [
    'alembic==0.7.4',
    'beautifulsoup4==4.3.2',
    'bleach==1.4.1',
    'Markdown==2.4.1',
    'pbkdf2==1.3',
    'pyramid==1.5',
    'pyramid_beaker==0.8',
    'pyramid_exclog==0.7',
    'pyramid_mako==1.0.2',
    'pyramid_tm==0.7',
    'SQLAlchemy==0.9.8',
    'transaction==1.4.1',
    'waitress==0.8.7',
    'WTForms==1.0.5',
    'zope.sqlalchemy==0.7.3',
]

entry_points = {
    'paste.app_factory': 'main = asb:main',
    'console_scripts': 'asbdb = asb.db.cli:main'
}

setuptools.setup(
    name='asb',
    packages=setuptools.find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite='asb',
    install_requires=requires,
    entry_points=entry_points
)
