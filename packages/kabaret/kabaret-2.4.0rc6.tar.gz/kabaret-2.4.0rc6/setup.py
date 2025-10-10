import os
import sys
from setuptools import setup, find_packages
import versioneer


if 0:
    long_description = (
        'VFX/Animation Studio Framework '
        'tailored for TDs/Scripters '
        'managing pipelines and workflows '
        'used by Production Managers and CGI Artists.\n\n'
        'Read the doc here: http://kabaret.readthedocs.io'
    )
else:
    readme = os.path.normpath(os.path.join(__file__, '..', 'README.rst'))
    with open(readme, 'r') as fh:
        long_description = fh.read()

    long_description += '\n\n'
    changelog = os.path.normpath(os.path.join(__file__, '..', 'CHANGELOG.md'))
    with open(changelog, 'r') as fh:
        long_description += fh.read()



setup(
    name='kabaret',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='VFX/Animation Studio Framework',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='http://www.kabaretstudio.com',
    author='Damien dee Coureau',
    author_email='kabaret-dev@googlegroups.com',
    license='LGPLv3+',
    classifiers=[
        'Development Status :: 5 - Production/Stable',

        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Desktop Environment :: File Managers',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Office/Business :: Groupware',
        'Topic :: Office/Business :: Scheduling',

        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Information Technology',

        'Operating System :: OS Independent',

        'Programming Language :: Python :: 3.7',

        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
    ],
    keywords='vfx animation framewok dataflow workflow asset manager production tracker',
    install_requires=[
        'pluggy',
        'redis',
        'six',
        'qtpy',
    ],
    python_requires='>=3.7',
    packages=find_packages('python'),
    package_dir={'': 'python'},
    package_data={
        '': ['*.css', '*.png', '*.svg', '*.gif'],
    },
)
