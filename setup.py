import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.txt')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

# I'm going to just give exact versions that I know will work
requires = [
    'pyramid==1.5a2',
    'SQLAlchemy==0.8.3',
    'transaction==1.4.1',
    'pyramid_tm==0.7',
    'pyramid_debugtoolbar==1.0.8',
    'zope.sqlalchemy==0.7.3',
    'waitress==0.8.7',

    'pbkdf2==1.3',
    'pyramid_beaker==0.8',
    'WTForms==1.0.5'
]

setup(name='asb',
      version='0.0',
      description='asb',
      long_description=README + '\n\n' + CHANGES,
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
      initialize_asb_db = asb.scripts.initializedb:main
      """,
      )
