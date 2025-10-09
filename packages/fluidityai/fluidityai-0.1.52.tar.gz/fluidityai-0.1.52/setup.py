from setuptools import setup, find_packages

setup(
    name='fluidityai',
    version='0.1.52',
    packages=find_packages(),
    install_requires=[
       'detoxify==0.5.2',
       'llm_guard==0.3.14',
       'openai==1.97.1',
       'pandas==1.5.3',
       'PyPDF2==3.0.1',
       'python-docx==1.2.0',
       'scikit_learn==1.7.1',
       'sentence_transformers==4.1.0',
       'duckdb==1.2.2',
       'beautifulsoup4==4.13.4'
    ],
    author='Ash Thakur',
    author_email='ash.thakur@yahoo.co.uk',
    description='Classes for AI workflow development',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/AshT-Python/Fluidity',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    include_package_data=True,
)

