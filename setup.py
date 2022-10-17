import os
from setuptools import setup, Extension
from setuptools.command.build_clib import build_clib
from wheel.bdist_wheel import bdist_wheel as bdist_wheel_


class bdist_wheel(bdist_wheel_):
    def get_tag(self):
        _, _, plat_name = bdist_wheel_.get_tag(self)
        return 'py2.py3', 'none', plat_name

from sys import platform
from shutil import copyfile, copytree
import glob

OpenBLASVersion = '0.3.20'
name = 'pylib_openblas'
des = "Python packaging of OpenBLAS {version}".format(version=OpenBLASVersion)


class MyBuildCLib(build_clib):
    def run(self):
        try:
            import urllib.request as request
        except ImportError:
            import urllib as request

        fname = "OpenBLAS-{version}.tar.gz".format(version=OpenBLASVersion)
        print("Downloading OpenBLAS version {}".format(OpenBLASVersion))
        request.urlretrieve("https://github.com/xianyi/OpenBLAS/releases/download/v{version}/OpenBLAS-{version}.tar.gz".format(version=OpenBLASVersion), fname)
        import tarfile
        print("Extracting OpenBLAS version {}".format(OpenBLASVersion))
        with tarfile.open(fname, "r:gz") as tar:
            tar.extractall()

        import subprocess
        print("Building OpenBLAS version {}".format(OpenBLASVersion))
        dynamic_arch = int(platform != "win32")
        if platform == "win32":
            dynamic_arch = 0
            builder = ["cmake", "--build", '.']
        else:
            dynamic_arch = 1
            builder = ['make', '-j2']

        try:
            os.makedirs(self.build_temp)
        except OSError:
            pass

        cwd = os.getcwd()
        os.chdir(self.build_temp)
        # this is clumsy <3
        guess_libplat = glob.glob(os.path.join(cwd, 'build', 'lib*'))[0]
        install_prefix = os.path.join(guess_libplat, 'pylib_openblas')
        subprocess.check_call(["cmake",
                               '-DCMAKE_BUILD_TYPE=Release',
                               '-DDYNAMIC_ARCH=1',
                               '-DNOFORTRAN=1',
                               '-DNO_LAPACK=1',
                               '-DBUILD_SHARED_LIBS=OFF',
                               os.path.join(cwd, 'OpenBLAS-{version}'.format(version=OpenBLASVersion)),
                               "-DCMAKE_INSTALL_PREFIX="+install_prefix])
        subprocess.check_call(builder)
        subprocess.check_call(["cmake", "--build", '.', '--target', 'install'])

        guess_libblas = glob.glob(os.path.join(install_prefix, 'lib*', '*openblas*'))[0]
        target_libblas = guess_libblas.replace('openblas', 'pylib_openblas')
        copyfile(guess_libblas, os.path.basename(target_libblas))

        os.chdir(cwd)

setup(name=name,
      version='0.0.1',
      packages=[name],
      libraries=[(name, {'sources': []})],
      description=des,
      long_description='Binary distribution of OpenBLAS static libraries',
      author='chenkui164',
      ext_modules=[Extension("pylib_openblas.placeholder", ['pylib_openblas/placeholder.c'])],
      cmdclass={'build_clib': MyBuildCLib,'bdist_wheel': bdist_wheel},
      options={'bdist_wheel':{'universal':True}})

