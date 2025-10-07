from setuptools import setup, find_packages

setup(
    name='uploadi',
    version='2.0.0',
    description='Приложение для загрузки проектов python',
    long_description=open('./README.md', encoding='utf8').read(),
    long_description_content_type='text/markdown',
    author='Ilia Miheev',
    author_email='waggle-pout-sprawl@duck.com',
    packages=find_packages(),
    license='MIT',
    entry_points={
        'console_scripts': [
            'uploadi=uploadi.uploadi:uploadi',
        ],
    },
)
