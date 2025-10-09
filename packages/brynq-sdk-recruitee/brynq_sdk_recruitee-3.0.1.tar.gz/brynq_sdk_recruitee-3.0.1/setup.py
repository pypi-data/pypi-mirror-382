from setuptools import setup, find_namespace_packages

setup(
    name='brynq_sdk_recruitee',
    version='3.0.1',
    description='Recruitee API SDK from BrynQ',
    long_description='A Python SDK for interacting with the Recruitee API',
    author='BrynQ',
    author_email='support@brynq.com',
    packages=find_namespace_packages(include=['brynq_sdk*']),
    license='BrynQ License',
    install_requires=[
        'brynq-sdk-brynq>=4,<5',
        'requests>=2.31.0,<3.0.0'
    ],
    zip_safe=False
)
