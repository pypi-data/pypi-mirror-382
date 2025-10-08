from setuptools import setup, find_packages


def readme():
    with open("README.md", "r") as f:
        return f.read()


setup(
    name="telegram-bot-discussion",
    version="0.0.27",
    author="ILYA",
    description="Telegram-bot framework `telegram-bot-discussion` based on native Telegram Bot API Python-library `python-telegram-bot`.",
    long_description=readme(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=["python-telegram-bot>=22.0"],
    classifiers=[
        "Programming Language :: Python :: 3.9",
        # "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Operating System :: OS Independent",
    ],
    keywords="Python Telegram-bot Framework",
    # project_urls={"Documentation": "link"},
    python_requires=">=3.9",
)
