from setuptools import setup, find_packages

def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='flibbyno',
    version='0.0.1',
    author='ornichola',
    author_email='test@axample.com',
    description='Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://ornicho.la/flibbyno',
    packages=find_packages(),
    install_requires=['requests'],
    classifiers=[
        'Programming Language :: Python :: 3.13',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    keywords='test development example',
    project_urls={
        'GitHub': '',
    },
    python_requires='>=3.13',
)
