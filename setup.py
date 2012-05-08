from setuptools import setup, find_packages
from restfulgrok.version import version


setup(name = 'restfulgrok',
      description = 'RESTful interface for grok (and five.grok).',
      version = version,
      license='BSD',
      url = 'https://github.com/espenak/restfulgrok',
      author = 'Espen Angell Kristiansen',
      packages=find_packages(exclude=['ez_setup']),
      install_requires = ['distribute', 'PyYAML', 'Jinja2', 'negotiator'],
      long_description=open('README.rst').read(),
      include_package_data=True,
      zip_safe=True,
      classifiers=[
                   'Development Status :: 5 - Production/Stable',
                   'Environment :: Web Environment',
                   'Framework :: Zope',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python'
                  ]
)
