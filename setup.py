import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
    README = f.read()

# I'm going to just give exact versions that I know will work
requires = [
    'alembic==0.6.3',
    'Mako==0.9.1',
    'pbkdf2==1.3',
    'pyramid==1.5',
    'pyramid_beaker==0.8',
    'pyramid_exclog==0.7',
    'pyramid_tm==0.7',
    'SQLAlchemy==0.8.3',
    'transaction==1.4.1',
    'waitress==0.8.7',
    'WTForms==1.0.5',
    'zope.sqlalchemy==0.7.3',
]

setup(name='asb',
      version='0.0',
      description='asb',
      long_description=README,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='asb',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = asb:main
      [console_scripts]
      asbdb = asb.db.cli:main
      """,
      )
