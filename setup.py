from pathlib import Path
from setuptools import setup, find_packages

from aoirint_matvtool import __VERSION__ as VERSION

setup(
    name='aoirint_matvtool',
    version=VERSION, # '0.1.0-alpha', # == 0.1.0-alpha0 == 0.1.0a0
    license='MIT',

    packages=find_packages(),
    include_package_data=True,

    entry_points = {
      'console_scripts': [
        'matvtool = aoirint_matvtool.scripts.cli:main',
      ],
    },

    install_requires=Path('requirements.in').read_text(encoding='utf-8').splitlines(),

    author='aoirint',
    author_email='aoirint@gmail.com',

    url='https://github.com/aoirint/matvtoolpy',
    description='A command line tool to handle a multi audio track video file',

    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)
