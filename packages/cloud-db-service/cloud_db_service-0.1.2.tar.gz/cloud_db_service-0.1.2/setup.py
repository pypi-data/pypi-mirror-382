from setuptools import setup, find_packages

setup(
    name="cloud_db_service",
    version="0.1.2",
    author="Aaditya Muleva, Vinay Shankar Miryala",
    author_email="aaditya.muleva@trovehealth.io, vinay.miryala@trovehealth.io",
    description="A unified cloud db package for AWS, Azure, and GCP",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires='>=3.6',
    license='MIT',
    install_requires=[
        # "boto3",
        "pymysql",
        "pyodbc"    ]
)