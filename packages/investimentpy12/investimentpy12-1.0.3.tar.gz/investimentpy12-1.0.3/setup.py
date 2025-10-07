from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='investimentpy12',
    version='1.0.3',
    packages=find_packages(),
    description='Uma biblioteca para análise de investimentos',
    author='Luciana Estevam',
    author_email='luesteva@gmail.com',
    url='https://github.com/luestevam/investimentpy12',  
    license='MIT',  
    long_description=long_description,
    long_description_content_type='text/markdown' 
)