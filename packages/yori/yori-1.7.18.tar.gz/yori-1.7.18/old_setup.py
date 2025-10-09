from setuptools import setup, find_packages

setup(name='yori',
      description='Set of tools to grid satellite data',
      author='Paolo Veglio',
      author_email='paolo.veglio@ssec.wisc.edu',
      url='https://gitlab.ssec.wisc.edu/pveglio/yori',
      use_scm_version=True,
      packages=find_packages(),
      python_requires='>=3.9',
      setup_requires=['setuptools_scm'],
      # install_requires=['numpy', 'ruamel.yaml', 'netcdf4', 'pyproj'],
      entry_points={'console_scripts': [
            'yori-grid = yori.tools.grid:main',
            'yori-aggr = yori.tools.aggr:main',
            'yori-merge = yori.tools.merge:main', ]},
      )
