from setuptools import setup, find_packages

setup(
    name="streamgit",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "streamlit",
        "streamlit-option-menu",
        "pandas",
        "pygithub",
        "plotly",
        "python-dotenv",
        "kaleido"
    ],
    entry_points={
        "console_scripts": [
            "streamgit=cli:main",
        ],
    },
    author="Keon Monroe",
    author_email="keon.monroe@gmail.com",
    description="A fluid GitHub analytics tool using PyGithub and Streamlit",
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