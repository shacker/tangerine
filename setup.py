import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'readme.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-tangerine',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    license='BSD License',
    description='A pluggable Django blogging engine.',
    long_description=README,
    url='http://software.birdhouse.org/',
    author='Scot Hacker',
    author_email='shacker@birdhouse.org',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.0',  # replace "X.Y" as appropriate
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
        'factory_boy',
        'titlecase',
        'libgravatar',
        'bleach',
        'python-aksismet',
        'django-ipware',
    ],

)
