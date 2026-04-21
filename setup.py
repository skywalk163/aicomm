import os

from setuptools import find_packages
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, "README.rst"), encoding="utf-8").read()
except IOError:
    README = ""
try:
    CHANGES = open(os.path.join(here, "CHANGES.rst"), encoding="utf-8").read()
except IOError:
    CHANGES = ""

version = "0.1.0"

install_requires = [
    "Kotti>=2.0.0,<3.0.0",
    "kotti_g4f>=0.1.0,<1.0.0",  # AI 助手集成
]

tests_require = [
    "WebTest>=3.0.0",
    "mock>=5.0.0",
    "pytest>=7.0.0,<9.0.0",
    "pytest-cov>=4.0.0",
    "zope.testbrowser>=5.0.0,<7.0.0",
]

setup(
    name="kotti_ai_community",
    version=version,
    description="AI共创社区 - AI资源互助平台，点子共享，实践落地",
    long_description="\n\n".join([README, CHANGES]),
    long_description_content_type="text/x-rst",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "License :: OSI Approved :: MIT License",
    ],
    author="AI共创社区",
    author_email="ai-community@example.com",
    url="https://github.com/kotti-ai-community",
    keywords="kotti ai community collaboration ideas resources",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    entry_points={
        "kotti.component": [
            "idea = kotti_ai_community.resources:Idea",
            "resource_item = kotti_ai_community.resources:ResourceItem",
        ],
    },
    extras_require={
        "testing": tests_require,
    },
)
