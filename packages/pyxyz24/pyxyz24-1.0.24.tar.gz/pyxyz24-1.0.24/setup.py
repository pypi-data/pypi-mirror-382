import platform
import glob
import ntpath
import os
from setuptools import setup

# OS specifics
CUR_OS = platform.system()
SHAREDOBJ_TEMPLATE = {
    'Windows': "pyxyz_base.cp{py_ver}-win_amd64.pyd",
    'Linux': "pyxyz_base.cpython-{py_ver}*-x86_64-linux-gnu.so",
}

# assert CUR_OS in ['Linux',
#                   'Windows'], "Only Linux and Windows platforms are supported"
assert CUR_OS == 'Linux', "Only Linux platform is currently supported 🤗"

# Python version specifics
python_version_tuple = platform.python_version_tuple()
py_ver = int(f"{python_version_tuple[0]}{python_version_tuple[1]}")

pyxyz_so_list = glob.glob(
    os.path.join('./pyxyz', SHAREDOBJ_TEMPLATE[CUR_OS].format(py_ver=py_ver)))
assert len(pyxyz_so_list) == 1
pyxyz_object_name = ntpath.basename(pyxyz_so_list[0])

for file in glob.glob('./pyxyz/*.pyd') + glob.glob('./pyxyz/*.so'):
    if ntpath.basename(file) != pyxyz_object_name:
        os.remove(file)

if CUR_OS == 'Windows':
    ADDITIONAL_FILES = ['*.dll']
elif CUR_OS == 'Linux':
    ADDITIONAL_FILES = []


def all_py(dir='.', exts=('.py', '.pyi')):
    result = []
    for root, _, files in os.walk(dir):
        for file in files:
            if any(file.endswith(ext) for ext in exts):
                result.append(
                    os.path.join(
                        *(os.path.join(root, file).split(os.sep)[1:])))
    return result


setup(
    name='pyxyz24',
    version='1.0.24',
    author='Nikolai Krivoshchapov',
    python_requires=f'=={python_version_tuple[0]}.{python_version_tuple[1]}.*',
    install_requires=[
        'numpy',
        'networkx',
    ],
    platforms=['Linux'],
    packages=['pyxyz'],
    package_data={
        'pyxyz': [
            pyxyz_object_name,
            *all_py('pyxyz'),  # All python files
            *all_py('pyxyz',
                    exts=('.xyz', )),  # Structures for built-in testing
            *all_py('pyxyz',
                    exts=('.sdf', )),  # Structures for built-in testing
            *ADDITIONAL_FILES,
        ]
    })
