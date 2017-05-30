from setuptools import setup, find_packages

setup(
    name='sen2cor_wrapper',
    version='0.1',
    description='Python wrapper for Sen2Cor',
    author='Jonas Solvsteen',
    author_email='josl@dhi-gras.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'gdal_utils>=0.2',
        'sentinel_meta>=0.3'],
    dependency_links=[
        'https://github.com/DHI-GRAS/gdal_utils/archive/v0.2.tar.gz#egg=gdal_utils-0.2',
        'https://github.com/DHI-GRAS/sentinel_meta/archive/v0.3.tar.gz#egg=sentinel_meta-0.3'])
