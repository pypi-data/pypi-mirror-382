from setuptools import setup, find_packages
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()
'not in use'
setup(
    name='nurtelecom_gras_library',
    long_description=long_description,
    long_description_content_type='text/markdown',
    version='1.2.3',
    license='MIT',
    author="Beksultan Tuleev",
    author_email='beksultan.tuleev.ds@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/beksultantuleev/nurtelecom_gras_library.git',
    keywords='NurTelecom',
    install_requires=[
        #   'scikit-learn',
        'cx_Oracle',
        'pandas',
        'sqlalchemy',
        'openpyxl',
        'tabulate',
        'requests',
        'transliterate',
        'hvac'
        #   'shapely',
        # 'matplotlib'
    ],
    classifiers=[
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Development Status :: 5 - Production/Stable',
        # Define that your audience are developers
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',   # Again, pick a license
        # Specify which pyhton versions that you want to support
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
