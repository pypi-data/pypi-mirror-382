from setuptools import setup, find_packages

setup(
    name='aws-resource-toggler',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'boto3>=1.34.0', # Requires Boto3 to interact with AWS
    ],
    author='Your Name or Company',
    description='A Python library to start and stop AWS resources (EC2, RDS, ECS) based on tags.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/aws-resource-toggler', # Customize this link
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: System :: Systems Administration',
    ],
    python_requires='>=3.8',
)
