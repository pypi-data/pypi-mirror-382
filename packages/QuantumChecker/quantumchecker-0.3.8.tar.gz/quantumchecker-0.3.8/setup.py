from setuptools import setup, find_packages

setup(
    name="QuantumChecker",
    version="0.3.8",
    author="Qobiljon",
    author_email="qobiljonkhayrullayev@gmail.com",
    description="A package to evaluate homework submissions in Python, SQL, PowerBI, and SSIS.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    license_files=["LICENSE.txt"],
    python_requires=">=3.6",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "tenacity>=8.2.3",
        "pdf2image>=1.16.3",
        "python-dotenv>=1.0.0",
        "Pillow>=10.0.0",
        "PyPDF2>=3.0.1",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
)