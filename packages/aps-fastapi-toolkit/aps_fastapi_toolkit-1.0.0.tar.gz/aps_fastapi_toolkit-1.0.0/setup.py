from setuptools import setup, find_packages

# Read README file for long description
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="aps_fastapi_toolkit",
    version="1.0.0",
    author="Abhay Pratap Singh",
    description="Common utils and services for FastAPI projects.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["*test*", ".venv*", ".circleci*"]),
    classifiers=[
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Framework :: FastAPI",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Database",
        "Topic :: Security",
    ],
    keywords="fastapi, jwt, authentication, database, sqlalchemy, security",
    install_requires=[
        "argon2-cffi==25.1.0",
        "SQLAlchemy==2.0.43",
        "PyJWT==2.10.1",
        "fastapi==0.118.0",
        "email-validator==2.3.0",
    ],
    python_requires=">=3.12",
    include_package_data=True,
    package_data={"fastapi_toolkit": ["py.typed"]},
)
