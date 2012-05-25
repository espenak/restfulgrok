from setuptools import setup, find_packages
from restfulgrok import version


setup(name = 'restfulgrok',
      description = 'RESTful interface for grok (and five.grok).',
      version = version,
      license='BSD',
      url = 'https://github.com/espenak/restfulgrok',
      author = 'Espen Angell Kristiansen',
      author_email = 'post@espenak.net',
      packages=find_packages(exclude=['ez_setup']),
      install_requires = ['distribute', 'PyYAML', 'Jinja2', 'negotiator'],
      long_description='See https://github.com/espenak/restfulgrok',
      include_package_data=True,
      zip_safe=True,
      classifiers=[
                   'Development Status :: 5 - Production/Stable',
                   'Environment :: Web Environment',
                   'Framework :: Plone',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python'
                  ]
)
