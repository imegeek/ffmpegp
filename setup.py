from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '1.12'
DESCRIPTION = 'ffmpegp is an enhanced version of FFmpeg, offering additional features and functionalities to extend its powerful media processing capabilities.'

# Setting up
setup(
    name="ffmpegp",
    version=VERSION,
    author="Im Geek (Ankush Bhagat)",
    author_email="<imegeek@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    entry_points={
        'console_scripts': ['ffmpegp = ffmpegp:main'],
    },
    packages=find_packages(),
    install_requires=["jsonpath_ng"],
    keywords=['python', 'ffmpeg', 'ffmpegp', "automation", "converter", "encoding", "progressbar"],
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)