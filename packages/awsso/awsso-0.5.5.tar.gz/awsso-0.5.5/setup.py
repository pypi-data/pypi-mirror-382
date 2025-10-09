import setuptools
import awsso

with open("README.md","r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="awsso",
    version="0.5.5",
    author="linhan",
    author_email="lynnpen@gmail.com",  
    description="aws command line tool",
    long_description=long_description, 
    long_description_content_type="text/markdown",
    url="https://github.com/Hireteammate/tools.git",
    packages=setuptools.find_packages(),
    install_requires=[
        'PyYAML >= 6.0',
        'inquirer >= 2.9.1',
        'boto3 >= 1.21.19',
        'argcomplete >= 2.0',
        'jira==3.8.0'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points='''
        [console_scripts]
        awsso=awsso.awsso:main
    ''',
#    data_files=[
#      ('/etc/bash_completion.d/', ['extra/some_completion_script']),
#    ]
)
