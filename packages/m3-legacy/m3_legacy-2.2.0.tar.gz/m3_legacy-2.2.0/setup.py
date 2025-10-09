import os
from setuptools import setup, find_packages


def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__),
            fname)).read()
    except IOError:
        return ''


setup(name='m3-legacy',
      version='2.2.0',
      url='https://bitbucket.org/barsgroup/m3-legacy',
      license='MIT',
      author='BARS Group',
      author_email='bars@bars-open.ru',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      description=read('DESCRIPTION'),
      install_requires=[
            'six>=1.11',
            'django>=1.4',
            'm3-django-compatibility>=1.12.0',
            'm3-core',
      ],
      long_description=read('README'),
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
)
