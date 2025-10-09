from setuptools import setup, find_namespace_packages

setup(
    name='brynq_sdk_zoho',
    version='3.1.0',
    description='ZOHO wrapper from BrynQ',
    long_description='ZOHO wrapper from BrynQ',
    author='BrynQ',
    author_email='support@brynq.com',
    packages=find_namespace_packages(include=['brynq_sdk*']),
    license='BrynQ License',
    install_requires=[
        'brynq-sdk-brynq>=2'
    ],
    zip_safe=False,
)
