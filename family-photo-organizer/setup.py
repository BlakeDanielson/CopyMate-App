from setuptools import setup, find_packages

# Read the version from the package
with open('src/family_photo_organizer/__init__.py', 'r') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.strip().split('=')[1].strip(' \'"')
            break

# Read dependencies from requirements.txt
with open('requirements.txt', 'r') as f:
    requirements = [line.strip() for line in f if not line.startswith('#')]

setup(
    name="family-photo-organizer",
    version=version,
    description="A desktop application to organize family photos using AI analysis",
    author="BlakeDanielson",
    author_email="",  # Add your email if desired
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=requirements,
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "family-photo-organizer=family_photo_organizer.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Graphics",
        "Operating System :: OS Independent",
    ],
) 