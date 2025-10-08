
from setuptools import setup, find_packages

VERSION = '8.0.0' 
DESCRIPTION = 'Framework para rotinas de ETL'
LONG_DESCRIPTION = 'Framework para simplificar o desenvolvimento de rotinas de ETL em python.'

# Setting up
setup(
        name="stnblipy", 
        version=VERSION,
        author="Secretaria do Tesouro Nacional",
        # author_email="",
        license="GPL v2",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[
            "beautifulsoup4==4.13.4",
            "bs4==0.0.2",
            "cffi==1.17.1",
            "cryptography==45.0.5",
            "et_xmlfile==2.0.0",
            "greenlet==3.2.3",
            "html5lib==1.1",
            "JayDeBeApi==1.2.3",
            "jpype1==1.5.2",
            "lxml==6.0.0",
            "multipledispatch==1.0.0",
            "numpy==2.3.2",
            "openpyxl==3.1.5",
            "oracledb==3.2.0",
            "packaging==25.0",
            "pandas==2.3.1",
            "pycparser==2.22",
            "python-dateutil==2.9.0.post0",
            "pytz==2025.2",
            "six==1.17.0",
            "soupsieve==2.7",
            "SQLAlchemy==2.0.41",
            "typing_extensions==4.14.1",
            "tzdata==2025.2",
            "webencodings==0.5.1",
            "wget==3.2",
            "xlrd==2.0.2"],
        keywords=['python', 'ETL', 'framework'],
        classifiers= [
            "Programming Language :: Python :: 3.13",
        ]
)

