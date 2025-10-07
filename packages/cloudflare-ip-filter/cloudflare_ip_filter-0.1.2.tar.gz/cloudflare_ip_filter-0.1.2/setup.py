from setuptools import setup, find_packages

setup(
    name="cloudflare-ip-filter",
    version="0.1.2",
    description="Flask middleware to restrict access to Cloudflare IP ranges",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Mert Cahit Yigit",
    packages=find_packages(),
    install_requires=[
        "flask",
        "requests",
        "logging",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
