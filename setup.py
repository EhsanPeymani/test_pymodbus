from setuptools import setup, find_packages

setup(
    name="your_library_name",           # Replace with your library's name
    version="0.1.0",                    # Initial version
    description="A short description of your library",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/your-repo",  # URL of the library's repository
    packages=find_packages(where="src"),  # Automatically find packages in the 'src' folder
    package_dir={"": "src"},              # Tell setuptools that packages are under 'src'
    install_requires=[
        # List your library's dependencies here, e.g.,
        # "requests>=2.25.1",
        # "numpy>=1.21.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",            # Minimum Python version requirement
)
