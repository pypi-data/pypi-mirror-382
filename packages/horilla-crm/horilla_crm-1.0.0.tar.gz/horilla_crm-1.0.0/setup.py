from setuptools import setup, find_packages

setup(
    name="horilla-crm",
    version="1.0.0",
    packages=find_packages(include=["horilla_crm", "horilla_crm.*"]),
    include_package_data=True,
    install_requires=[],
    description="Horilla CRM Django apps package",
    author="Your Name",
    author_email="your_email@example.com",
    url="https://github.com/horilla-opensource/horilla",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Django",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
