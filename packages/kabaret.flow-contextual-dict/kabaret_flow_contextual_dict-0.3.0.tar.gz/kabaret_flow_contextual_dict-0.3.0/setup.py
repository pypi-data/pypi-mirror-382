import os
import sys
from setuptools import setup, find_packages

import versioneer

readme = os.path.normpath(os.path.join(__file__, "..", "README.md"))
with open(readme, "r") as fh:
    long_description = fh.read()

setup(
    cmdclass=versioneer.get_cmdclass(),
    name="kabaret.flow_contextual_dict",
    version=versioneer.get_version(),
    description="kabaret.flow contextual dict",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/kabaretstudio/kabaret.flow_contextual_dict",
    author='Damien "dee" Coureau',
    author_email="kabaret-dev@googlegroups.com",
    license="LGPLv3+",
    classifiers=[
        # "Development Status :: 1 - Planning",
        # 'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 3 - Alpha',
        "Development Status :: 4 - Beta",
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
        # "Topic :: System :: Shells",
        # "Intended Audience :: Developers",
        # 'Intended Audience :: End Users/Desktop',
        # "Operating System :: Microsoft :: Windows :: Windows 10",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.7",
        (
            "License :: OSI Approved :: "
            "GNU Lesser General Public License v3 or later (LGPLv3+)"
        ),
    ],
    keywords="vfx animation pipeline asset library",
    install_requires=["kabaret>=2.4.0rc6"],
    extras_require={"dev": ["twine", "flake8", "black",],},
    python_requires=">=2.7,!=3.0.*,!=3.1.*,!=3.2.*",
    packages=find_packages("src"),
    package_dir={"": "src"},
    package_data={"": ["*.css", "*.png", "*.svg", "*.gif"],},
)
