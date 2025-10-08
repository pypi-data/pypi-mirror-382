from setuptools import setup, find_namespace_packages

setup(
    name='brynq_sdk_sharepoint',
    version='3.1.0',
    description='Sharepoint wrapper from BrynQ',
    long_description='Sharepoint wrapper from BrynQ',
    author='BrynQ',
    author_email='support@brynq.com',
    packages=find_namespace_packages(include=['brynq_sdk*']),
    license='BrynQ License',
    install_requires=[
        'brynq-sdk-brynq>=4,<5',
        'requests>=2,<=3'
    ],
    zip_safe=False,
)
