from setuptools import setup, find_packages

with open('README.md', 'r') as fh:
    long_description = fh.read()
    long_description = long_description.split('## Changelog')[0]
with open('CHANGELOG.md', 'r') as ch:
    long_description += "\n\n" + ch.read()

setup(
    name="fastapi_cacher",
    version="0.3.3",
    author="Fahad Mawlood",
    author_email="fahadukr@gmail.com",
    description="A caching library for FastAPI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Fahadukr/fastapi-cacher",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "redis",
        "cachelib",
        "motor",
        "pendulum",
        "pymongo",
        "aiomcache"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
)
