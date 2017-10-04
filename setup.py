from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='Messagerie',
      description='Custom wrapper to aws services',
      long_description=readme(),
      author='stikks',
      author_email='styccs@gmail.com',
      include_package_data=True,
      packages=['messagerie'],
      install_requires=[
          'requests',
          'boto3',
          'pyshorteners'
      ])
