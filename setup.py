import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyctlmbatchtoolbox",
    version="0.0.3",
    author="Jose Morales Aragon",
    author_email="jmoralesaragon@users.noreply.github.com",
    description="Set of command line tools used to interact with Control-M.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AmadeusITGroup/pyctlmbatchtoolbox",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    python_requires='>=3.6',
    install_requires=[
        'requests','urllib3'
    ],
    keywords='bmc controlm batch',
    project_urls={
        'Homepage': 'https://github.com/AmadeusITGroup/pyctlmbatchtoolbox'
    },
    entry_points={
        'console_scripts': [
            'batch_token=pyctlmbatchtoolbox.command_token:main',
            'batch_order=pyctlmbatchtoolbox.command_order:main',
            'batch_status=pyctlmbatchtoolbox.command_status:main',
            'batch_logs=pyctlmbatchtoolbox.command_logs:main',
            'batch_deploy=pyctlmbatchtoolbox.command_deploy:main',
            'batch_condition=pyctlmbatchtoolbox.command_condition:main',
            'batch_hostgroup=pyctlmbatchtoolbox.command_hostgroup:main',
            'batch_connectionprofile=pyctlmbatchtoolbox.command_connectionprofiles:main'
        ],
    },
)
