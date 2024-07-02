from setuptools import setup, find_packages

# Read README content
with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

config = {
    'description': 'An open-source Python toolkit offering a collection of efficient, easy-to-use functions for seismic data analysis.',
    'author': 'Gabriele Paoletti',
    'url': 'https://github.com/gabrielepaoletti/quakepro',
    'download_url': 'https://github.com/gabrielepaoletti/quakepro',
    'author_email': 'gabriele.paoletti@uniroma1.it',
    'version': '0.1.0',
    'python_requires': '>=3.9',
    'install_requires': ['h5py', 'matplotlib', 'numpy', 'obspy', 'pandas', 'scipy', 'typing', 'tqdm'],
    'packages': find_packages(),
    'name': 'quakepro',
    'license': 'MIT',
    'keywords': 'seismology earthquake catalog waveform download processing geophysics data-analysis',
    'long_description': long_description,
    'long_description_content_type': 'text/markdown',
}

setup(**config)