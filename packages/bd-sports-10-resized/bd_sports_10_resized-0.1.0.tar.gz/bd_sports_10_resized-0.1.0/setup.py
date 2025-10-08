from setuptools import setup, find_packages

setup(
    name="bd_sports_10_resized",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "requests",
        "tqdm"
    ],
    description="Resized version of BD Sports 10 dataset with downloader and progress bar",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Wazih Ullah Tanzim, Syed Md. Minhaz Hossain",
    license="CC BY 4.0",
    url="https://data.mendeley.com/datasets/rnh3x48nfb/1",
    python_requires=">=3.11",
)
