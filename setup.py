from setuptools import setup

setup(
    name='iris-cortexanalyzer-module',
    python_requires='>=3.9',
    version='0.1.0',
    packages=['iris_cortexanalyzer_module', 'iris_cortexanalyzer_module.cortexanalyzer_handler'],
    url='https://github.com/socfortress/iris-cortexanalyzer-module',
    license='MIT',
    author='SOCFortress',
    author_email='info@socfortress.co',
    description='`iris-cortexanalyzer-module` is a IRIS pipeline/processor module created with https://github.com/dfir-iris/iris-skeleton-module',
    install_requires=[]
)
