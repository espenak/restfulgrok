from setuptools import setup, find_packages


setup(name = 'restfulgrok',
      description = 'RESTful interface for grok (and five.grok).',
      version = '1.0',
      license='BSD',
      url = 'https://github.com/espenak/restfulgrok',
      author = 'Espen Angell Kristiansen',
      packages=find_packages(exclude=['ez_setup']),
      install_requires = ['distribute', 'PyYAML', 'Jinja2'],
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
