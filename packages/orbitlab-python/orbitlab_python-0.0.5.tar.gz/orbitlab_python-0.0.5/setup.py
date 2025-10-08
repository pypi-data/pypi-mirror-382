import os
from setuptools import setup, find_packages

package_name = "orbitlab-python"

setup(
    name=package_name,
    version='0.0.5',
    package_dir={'':'src'},
    packages=find_packages(where='src'),
    data_files=[
    ],
    install_requires=['setuptools', 'numpy', 'opencv-python'],
    zip_safe=True,
    maintainer='Kalebu',
    maintainer_email='calebndatimana@gmail.com',
    description='TODO: package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
)