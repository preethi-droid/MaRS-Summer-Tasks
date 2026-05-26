from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'turtle_avoidance'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
    (
        'share/ament_index/resource_index/packages',
        ['resource/' + package_name]
    ),

    ('share/' + package_name, ['package.xml']),

    (
        os.path.join('share', package_name, 'launch'),
        glob('launch/*.py')
    ),
    (
    os.path.join('share', package_name, 'action'),
    glob('action/*.action')
    ),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='preethi',
    maintainer_email='preethiabhiramik@gmail.com',
    description='ROS package',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
    'console_scripts': [

        'collision_avoidance_node = turtle_avoidance.collision_avoidance_node:main',

        'circle_patrol_server = turtle_avoidance.circle_patrol_server:main',

        'circle_patrol_client = turtle_avoidance.circle_patrol_client:main',
    ],
    },
)
