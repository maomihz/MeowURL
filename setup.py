from setuptools import setup

setup(
    name='meowurl',
    version='0.1',
    description='MeowURL URL Shortener & Pastebin',
    long_description=open('README.rst').read(),
    url='https://github.com/maomihz/MeowURL',
    author='Dexter MaomiHz',
    author_email='maomihz@gmail.com',
    license='MIT',
    packages=['meowurl'],
    include_package_data=True,
)
