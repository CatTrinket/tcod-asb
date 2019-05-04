import os

import setuptools

# I'm going to just give exact versions that I know will work
requires = [
    'alembic==1.0.9',
    'bbcode==1.0.33',
    'beautifulsoup4==4.5.1',
    'bleach==1.4.3',
    'Markdown==2.4.1',
    'pbkdf2==1.3',
    'pyramid==1.5',
    'pyramid_beaker==0.8',
    'pyramid_exclog==0.7',
    'pyramid_mako==1.0.2',
    'pyramid_tm==0.7',
    'SQLAlchemy==1.3.3',
    'transaction==2.4.0',
    'waitress==0.8.7',
    'WTForms==2.2.1',
    'zope.sqlalchemy==1.1',
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
