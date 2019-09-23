import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='finances',
    version='1.5.0',
    author='Hugo Delatte',
    author_email='delatte.hugo@gmail.com',
    description='Analyse your HSBC statements ',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/hugdel/finances.git',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
