from setuptools import setup

setup(
    name='text-fabric',
    packages=[
        'tf',
        'tf.applib',
        'tf.convert',
        'tf.core',
        'tf.search',
        'tf.server',
        'tf.writing',
    ],
    install_requires=[
        'rpyc',
        'flask',
        'psutil',
        'markdown',
        'ipython',
        'requests',
    ],
    python_requires='>=3.6.3',
    include_package_data=True,
    exclude_package_data={'': ['text_fabric.egg-info', '__pycache__', '.DS_Store']},
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'text-fabric = tf.server.start:main',
            'text-fabric-zip = tf.applib.zipdata:main',
        ]
    },
    version='7.4.6',
    description='''Processor and browser for Text Fabric Data''',
    author='Dirk Roorda',
    author_email='dirk.roorda@dans.knaw.nl',
    url='https://github.com/annotation/text-fabric',
    keywords=[
        'text', 'linguistics',
        'database', 'graph',
        'hebrew', 'bible', 'cuneiform', 'uruk',
        'greek', 'syriac',
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Framework :: Jupyter",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Religion",
        "Intended Audience :: Science/Research",
        "License :: Public Domain",
        "Natural Language :: English",
        "Natural Language :: Hebrew",
        "Natural Language :: Greek",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Religion",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Text Processing :: Filters",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Text Processing :: Markup :: XML",
    ],
    long_description='''\
Tools to read text corpora with (linguistic) annotations
and process them efficiently.
With a built in web-interface for querying a corpus.
More info on https://annotation.github.io/text-fabric/
''',
)
