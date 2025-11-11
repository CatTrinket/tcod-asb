import os

import setuptools

# I'm going to just give exact versions that I know will work
requires = [
    'alembic==1.0.9',
    'bbcode==1.0.33',
    'bleach==6.1.0',
    'Markdown==2.4.1',
    'pbkdf2==1.3',
    'pyramid==1.5',
    'pyramid_beaker==0.8',
    'pyramid_exclog==0.7',
    'pyramid_mako==1.0.2',
    'pyramid_tm==0.7',
    'SQLAlchemy==1.3.3',
    'transaction==2.4.0',
    'waitress==2.1.2',
    'WTForms==2.2.1',
    'zope.sqlalchemy==1.1',
]

extras_require = {
    'production': [
        'gunicorn==21.2.0',
        'psycopg2==2.9.9',
        'pycrypto==2.6.1',
    ]
}

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
    extras_require=extras_require,
    entry_points=entry_points
)
