from setuptools import setup, Extension

__name__ = 'sysvipc-python'
__version__ = '1.0.0'

class get_pybind_include(object):
    """Helper class to determine the pybind11 include path
    The purpose of this class is to postpone importing pybind11
    until it is actually installed, so that the ``get_include()``
    method can be invoked. """

    def __init__(self, user=False):
        self.user = user

    def __str__(self):
        import pybind11
        return pybind11.get_include(self.user)


setup(
    name=__name__,
    version=__version__,
    author='Aivars Kalvans',
    author_email='aivars.kalvans@gmail.com',
    url='https://github.com/aivarsk/sysvipc-python',
    description='Python3 bindings for System V IPC',
    long_description=open('README.rst').read(),
    setup_requires=['pybind11>=2.4'],
    ext_modules=[
    Extension(
        name='sysvipc',
        sources=['sysvipcmodule.cpp'],
        include_dirs=[
            get_pybind_include(),
            get_pybind_include(user=True),
        ],
    ),

    ],
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: C',
        'Operating System :: POSIX',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development',
    ],
    zip_safe=False,
)
