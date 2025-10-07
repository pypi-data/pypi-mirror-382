from setuptools import setup

setup(
    name='mlab_amo_async',
    version='0.0.5',
    author='MLAB',
    description='Небольшая библиотека для работы с AmoCRM+MongoDB',
    install_requires=[
        'requests',
        'pyjwt',
        'motor',
        'importlib-metadata; python_version<"3.11"',
    ],
)