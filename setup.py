"""sffmsexport.
Export latex sffms files to rtf.
"""

from setuptools import setup

setup(
    name='sffmsexport',
    version='0.1.0',
    description='Convert sffms latex files to RTF.',
    url='https://github.com/barsanuphe/sffmsexport',
    author='barsanuphe',
    author_email='mon.adresse.publique@gmail.com',
    license='GPLv3+',
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 2 - Pre-Alpha'
        'Intended Audience :: End Users/Desktop',
        'Operating System :: POSIX :: Linux',
        'Topic :: Text Processing :: Markup :: LaTeX',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='sffms latex rtf',
    # packages=[],
    # install_requires=[],

    entry_points={
        'console_scripts': [
            'sffmsexport=sffmsexport:main',
        ],
    },


)
