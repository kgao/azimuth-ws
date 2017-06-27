from setuptools import setup

setup(name='azimuth-ws',
      version='1.0',
      author='Kevin Gao',
      description=("The Web Service for Machine Learning-Based Predictive Modelling of CRISPR/Cas9 guide efficiency"),
      install_requires=['flask','azimuth', 'azure-storage>=0.34.0,<0.35.0', 'pandas>=0.20.0,<0.21.0'],
      license="BSD",
      )
