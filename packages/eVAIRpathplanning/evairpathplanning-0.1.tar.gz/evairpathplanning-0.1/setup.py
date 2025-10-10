from setuptools import setup, find_packages

setup(
    name='eVAIRpathplanning',
    version='0.1',
    description='eVAIR Path Planning codes',
    author='Eugene H. Kim',
    author_email='eugenekim00000@gmail.com',
    packages=find_packages(),
    install_requires=[
        'numpy>=2.1.1'
        ],
    )