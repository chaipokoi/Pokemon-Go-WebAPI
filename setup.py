from setuptools import setup

setup(name='Pokemon-Go-WebAPI',
      version='1.0',
      description='',
      author='Clovis Portron',
      author_email='portron.cl@gmail.com',
      url='http://www.python.org/sigs/distutils-sig/',
      install_requires=[ 'bottle' , 'geopy', 'gpsoauth', 'protobuf>=3.0.0a3', 'pycryptodomex', 'requests', 'winrandom', 'pycrypto', 's2sphere' ],
)