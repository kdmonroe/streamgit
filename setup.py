from setuptools import setup, find_packages

setup(
    name="streamgit",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True, 
    install_requires=[
        "streamlit",
        "pandas",
        "pygithub",
        "plotly",
        "python-dotenv",
        "kaleido",
        "openpyxl"
    ],
    extras_require={
        'test': [
            'pytest>=6.2.5',
            'pytest-cov>=2.12.1',
            'freezegun>=1.2.0',
        ],
    },
    entry_points={
        "console_scripts": [
            "streamgit=app.cli:main",
        ],
    },
    author="Keon Monroe",
    author_email="keon.monroe@gmail.com",
    description="A GitHub analytics tool using PyGithub and Streamlit",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/keonmonroe/streamgit",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)