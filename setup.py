import re
import setuptools


setuptools.setup(
    name='ciao',
    version=(
        re
        .compile(r".*__version__ = '(.*?)'", re.S)
        .match(open('ciao.py').read())
        .group(1)
    ),
    url='https://github.com/bninja/ciao',
    license='BSD',
    author='mikey',
    author_email='mikey@corleone.it',
    description='Michael Corleone says ...',
    long_description=open('README.rst').read(),
    py_modules=['ciao'],
    include_package_data=True,
    platforms='any',
    install_requires=[
    ],
    extras_require={
        'tests': [
            'pytest >=2.5.2,<3',
            'pytest-cov >=1.7,<2',
        ],
    },
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
