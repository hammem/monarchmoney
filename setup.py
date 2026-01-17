from setuptools import setup
from pathlib import Path

here = Path(__file__).resolve().parent
requirements_path = here / "requirements.txt"
install_requires = []
if requirements_path.exists():
    install_requires = requirements_path.read_text().splitlines()

setup(
    name="monarchmoneycommunity",
    description="Monarch Money API for Python",
    long_description=(here / "README.md").read_text(),
    long_description_content_type="text/markdown",
    url="https://github.com/bradleyseanf/monarchmoneycommunity",
    author="bradleyseanf",
    author_email="bradleyseanf@users.noreply.github.com",
    license="MIT",
    license_files=[],
    keywords="monarch money, financial, money, personal finance",
    install_requires=install_requires,
    packages=["monarchmoney"],
    include_package_data=True,
    zip_safe=False,
    platforms="any",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Topic :: Office/Business :: Financial",
    ],
)
