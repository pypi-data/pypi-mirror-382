import os

# configuration
PACKAGE_VERSION = '1.4.100'
DUCKDB_VERSION = '1.4.1'

DEPENDENCIES = [
    'jupyter',
    'graphviz==0.21',
    'checkmarkandcross'
]

if os.getenv('SQLITE') != '1' and os.getenv('DUCKDB') != '0':
    DEPENDENCIES += [f'duckdb=={DUCKDB_VERSION}']

# main setup
if __name__ == '__main__':
    from setuptools import setup, find_namespace_packages

    # load README.md as long_description
    with open('README.md', 'r', encoding='utf-8') as file:
        long_description = file.read()

    # main setup call
    setup(
        name='jupyter-duckdb',
        version=PACKAGE_VERSION,
        python_requires='>=3.10',
        install_requires=DEPENDENCIES,
        author='Eric Tröbs',
        author_email='eric.troebs@tu-ilmenau.de',
        description='a basic wrapper kernel for DuckDB',
        long_description=long_description,
        long_description_content_type='text/markdown',
        url='https://github.com/erictroebs/jupyter-duckdb',
        project_urls={
            'Bug Tracker': 'https://github.com/erictroebs/jupyter-duckdb/issues',
        },
        classifiers=[
            'Programming Language :: Python :: 3',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
        ],
        package_dir={'': 'src'},
        packages=find_namespace_packages(where='src'),
        include_package_data=True,
        package_data={
            'duckdb_kernel': [
                'kernel.json',
                'visualization/lib/*.css',
                'visualization/lib/*.js',
            ]
        }
    )
