from setuptools import setup, find_packages

setup(
    name="prisma-tui",
    version="0.2.0",
    description="A TUI framework based on the idea of \"multi-layered transparency\" composition.",
    keywords="tui terminal user interface transparency layers layered curses",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="DiegoBarMor",
    author_email="diegobarmor42@gmail.com",
    url="https://github.com/diegobarmor/prisma-tui",
    license="MIT",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
