from setuptools import setup, find_packages

setup(
    name='IsarnConnect',
    version='1.4.4',
    author='C0MaE',
    author_email='jannis.koberg@icloud.com',
    packages=find_packages(),
    install_requires=[
        'psycopg2-binary>=2.9.9',
        'sqlalchemy>=2.0.27',
        'pandas>=2.2.1',
        'mysql-connector-python>=2.2.9'
    ],
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
)
