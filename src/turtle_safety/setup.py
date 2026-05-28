import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'turtle_safety'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.[pxy][yma]*'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='preethi',
    maintainer_email='preethiabhiramik@gmail.com',
    description='Collision avoidance',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'collision_avoidance_node = turtle_safety.collision_avoidance_node:main',
            'circle_patrol_server = turtle_safety.circle_patrol_server:main',
            'circle_patrol_client = turtle_safety.circle_patrol_client:main'
        ],
    },
)
