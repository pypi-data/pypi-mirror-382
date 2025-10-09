from setuptools import setup

setup(
    name='reqx',
    version='2.0.0',
    py_modules=['reqx'],
    author='VIRUS',
    description='Bypass cookies and user agent protection',
    install_requires=['requests', 'pycryptodome'],
    python_requires='>=3.6',
)