import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'hydra_mesh_bringup'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), ['launch/my_custom_simulation_launch.py']),
        (os.path.join('share', package_name, 'launch'), ['launch/hydra_nav2_integration_launch.yaml']),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'worlds'), glob('worlds/*.sdf.xacro')),
        # --- REMOVE THIS LINE: (os.path.join('share', package_name, 'worlds'), glob('worlds/*.stl')),
        # --- ADD THESE NEW LINES FOR office_model ---
        (os.path.join('share', package_name, 'worlds', 'office_model'), glob('worlds/office_model/*.*')), # model.config, model.sdf
        (os.path.join('share', package_name, 'worlds', 'office_model',
                      'meshes'), glob('worlds/office_model/meshes/*.glb')), # Change the extension
        (os.path.join('share', package_name, 'worlds', 'office_model',
                      'meshes'), glob('worlds/office_model/meshes/*.bin')),
        (os.path.join('share', package_name, 'worlds', 'office_model',
                      'meshes'), glob('worlds/office_model/meshes/*.dae')),
        (os.path.join('share', package_name, 'worlds', 'office_model',
                      'meshes'), glob('worlds/office_model/meshes/*.obj')),
        (os.path.join('share', package_name, 'worlds', 'office_model',
                      'meshes'), glob('worlds/office_model/meshes/*.mtl')),
        (os.path.join('share', package_name, 'worlds', 'office_model',
                      'meshes'), glob('worlds/office_model/meshes/*.png')),

        # --- END OF NEW LINES FOR office_model ---
        # --- ADD THESE NEW LINES FOR house_model ---
        (os.path.join('share', package_name, 'worlds', 'house_model'), glob('worlds/house_model/*.*')),
        (os.path.join('share', package_name, 'worlds', 'house_model',
                      'meshes'), glob('worlds/house_model/meshes/textures/*.jpg')),
        (os.path.join('share', package_name, 'worlds', 'house_model',
                      'meshes'), glob('worlds/house_model/meshes/*.obj')),
        (os.path.join('share', package_name, 'worlds', 'house_model',
                      'meshes'), glob('worlds/house_model/meshes/*.mtl')),

        # --- END OF NEW LINES ---
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='João Lucas',
    maintainer_email='joaolmbc@al.insper.edu.br',
    description='Bringup package using the Hydra-generated mesh in Gazebo',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [],
    },
)
