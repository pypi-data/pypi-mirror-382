from distutils.core import setup
setup(
  name = 'make_spirals',
  packages = ['make_spirals'],
  version = '0.2',
  license='apache-2.0',
  description = 'make_spirals generates a synthetic data set composed of interlaced Archimedean spirals.',
  author = 'Fernando Ortega',
  author_email = 'fernando.ortega@upm.es',
  url = 'https://github.com/KNODIS-Research-Group/make_spirals',
  download_url = 'https://github.com/KNODIS-Research-Group/make_spirals/archive/v0_1.tar.gz',
  keywords = ['scikit-learn', 'supervised-learning', 'classification', 'dataset', 'spirals'],
  install_requires=[            # I get to this in a second
          'numpy',
          'scikit-learn',
      ],
  classifiers=[
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: Apache Software License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)
