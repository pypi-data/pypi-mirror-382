from setuptools import setup, find_packages
import re

package = "powerbin"

def find_version():
    version_file = open(package + "/__init__.py", encoding="utf-8").read()
    rex = r'__version__\s*=\s*"([^"]+)"'
    return re.search(rex, version_file).group(1)

def read_docstring(name, file=None):
    if file is None:
        file = name + ".py"
    main_file = open(package + "/" + file, encoding="utf-8").read()
    rex = f'(?:def {name}[\\w\\W]+?|class {name}):\\n\\s*"""([\\W\\w]+?)"""'
    docstring = re.search(rex, main_file).group(1)
    return docstring.replace("\n    ", "\n")

setup(name=package,
      version=find_version(),
      description="PowerBin: Fast Adaptive Data Binning with Centroidal Power Diagrams",
      long_description_content_type= 'text/x-rst',
      long_description=open(package + "/README.rst", encoding="utf-8").read()
                       + read_docstring("PowerBin", file="powerbin.py")
                       + open(package + "/LICENSE.txt", encoding="utf-8").read()
                       + open(package + "/CHANGELOG.rst", encoding="utf-8").read(),
      url="https://pypi.org/project/powerbin/",
      author="Michele Cappellari",
      author_email="michele.cappellari@physics.ox.ac.uk",
      license="Other/Proprietary License",
      packages=find_packages(),
      package_data={package: ["*.rst", "*.txt", "*/*.txt"]},
      install_requires=["plotbin", "numpy", "scipy", "matplotlib"],
      classifiers=["Development Status :: 5 - Production/Stable",
                   "Intended Audience :: Developers",
                   "Intended Audience :: Science/Research",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python :: 3"],
      zip_safe=True)
