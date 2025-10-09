from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="django-markdown-renderer",
    version="0.2.0",
    author="xoxxel",
    author_email="",
    description="A Django app for rendering Markdown with real-time preview",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xoxxel/django-markdown-renderer",
    project_urls={
        "Bug Tracker": "https://github.com/xoxxel/django-markdown-renderer/issues",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "Django>=3.2",
        "markdown2>=2.4.0",
        "bleach>=4.1.0",
    ],
)