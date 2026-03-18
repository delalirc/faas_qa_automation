"""
Setup script for FAAS QA Automation package
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="faas-qa-automation",
    version="1.0.0",
    author="FAAS QA Team",
    description="Centralized QA automation for FAAS platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/retail-capital/faas_qa_automation",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "qa-wait=scripts.wait_for_qa_tests:main",
            "qa-check=scripts.check_qa_results:main",
            "qa-report=framework.utils.reporting:main",
            "qa-s2o-report=framework.utils.s2o_report_generator:main",
        ],
    },
)
