from setuptools import setup, find_packages

setup(
    name='modxpy',
    version='1.8.3',
    description='ModX — The Python Module Universe at Your Fingertips',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Austin Wang',
    author_email='austinw87654@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3.7',
)
