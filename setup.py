from setuptools import setup, find_packages

setup(
    name='daily-git',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'GitPython',
        'rich',
    ],
    entry_points={
        'console_scripts': [
            'daily-git=daily_git.cli:main',
        ],
    },
    author='Luca Bruno Knaack',
    author_email='l.knaack93@gmail.com',
    description='A tool for tracking daily coding statistics from Git repositories.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/SithHades/daily-git',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)