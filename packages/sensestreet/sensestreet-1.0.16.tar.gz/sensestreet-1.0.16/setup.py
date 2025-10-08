from setuptools import setup, find_packages
# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()


setup(
    name='sensestreet',
    version='1.0.16',
    license='Apache',
    packages=find_packages('src'),
    author="Sense Street",
    author_email="engineering@sensestreet.com",
    url="https://sensestreet.com",
    package_dir={'': 'src'},
    install_requires=[
          'requests',
          'Authlib',
          'cryptography',
          'lxml',
      ],
    long_description=long_description,
    long_description_content_type='text/markdown'

)