from setuptools import setup, find_packages

setup(
    name='carthooks',
    version='0.2.3',
    packages=find_packages(),
    description='Carthooks Python SDK with Watcher for real-time data monitoring',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Carthooks',
    author_email='developer@carthooks.com',
    license='MIT',
    install_requires=[
        'httpx[http2]>=0.24.0',
        'boto3>=1.26.0',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
)