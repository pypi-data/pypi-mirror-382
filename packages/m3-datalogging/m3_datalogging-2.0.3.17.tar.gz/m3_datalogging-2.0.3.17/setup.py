# coding: utf-8
from setuptools import setup, find_packages


setup(
    name='m3-datalogging',
    version='2.0.3.17',
    author='Andrew Torsunov, Kirill Borisov',
    author_email='torsunov@bars-open.ru, borisov@bars-open.ru',
    packages=find_packages('src', exclude=['tests']),
    package_dir={'': 'src'},
    include_package_data=True,
    url='https://bitbucket.org/barsgroup/data-logging',
    license='MIT',
    description='Logging system to spy on users.',
    exclude_package_data={'': ['*.pyc', '*.pyo']},
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
    install_requires=[
        'django-json-field>=0.5.8',
        'm3_legacy>=2.1.1',
        'architect==0.6.0',
    ],
)
