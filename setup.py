from setuptools import setup

setup(
    name="bme280_dashboard",
    version="0.1.0",
    install_requires=[
        *open("requirements.txt").read().splitlines()
    ],
    entry_points={
        'console_scripts': [
            'bme280_dashboard = bme280_dashboard.main:main'
        ]
    },
)
