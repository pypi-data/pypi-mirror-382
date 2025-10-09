from setuptools import setup

setup(
    name='tromeda',
    version='0.1.10', 
    description='A tool for getting available data-files of TROPOS devices',
    url='https://github.com/ulysses78/tromeda',
    author='Andi Klamt',
    author_email='klamt@tropos.de',
    license='MIT License',
    packages=['tromeda'],
    install_requires=['toml',                     
                      'datetime',                     
                      'requests',                     
                      ],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',  
        'Operating System :: POSIX :: Linux',        
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
    ],
)
