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
        def build4linux():
            try:
                import urllib.request as request
            except ImportError:
                import urllib as request

            fname = "OpenBLAS-{version}.tar.gz".format(version=OpenBLASVersion)
            print("Downloading OpenBLAS version {}".format(OpenBLASVersion))
            request.urlretrieve(
                "https://github.com/xianyi/OpenBLAS/releases/download/v{version}/OpenBLAS-{version}.tar.gz".format(version=OpenBLASVersion), fname)
            import tarfile
            print("Extracting OpenBLAS version {}".format(OpenBLASVersion))
            with tarfile.open(fname, "r:gz") as tar:
                tar.extractall()

            import subprocess
            print("Building OpenBLAS version {}".format(OpenBLASVersion))
            os.makedirs(self.build_temp)

            cwd = os.getcwd()
            os.chdir(self.build_temp)
            guess_libplat = glob.glob(os.path.join(cwd, 'build', 'lib*'))[0]
            install_prefix = os.path.join(guess_libplat, 'pylib_openblas')
            import platform
            if platform.machine() == "aarch64":
                cmake_cmd = ["cmake",
                             '-DTARGET=ARMV8',
                             '-DCMAKE_BUILD_TYPE=Release',
                             '-DDYNAMIC_ARCH=1',
                             '-DNOFORTRAN=1',
                             '-DNO_LAPACK=1',
                             '-DBUILD_SHARED_LIBS=OFF',
                             os.path.join(
                                 cwd, 'OpenBLAS-{version}'.format(version=OpenBLASVersion)),
                             "-DCMAKE_INSTALL_PREFIX=" + install_prefix]
            else:
                cmake_cmd = ["cmake",
                             '-DCMAKE_BUILD_TYPE=Release',
                             '-DDYNAMIC_ARCH=1',
                             '-DNOFORTRAN=1',
                             '-DNO_LAPACK=1',
                             '-DBUILD_SHARED_LIBS=OFF',
                             os.path.join(
                                 cwd, 'OpenBLAS-{version}'.format(version=OpenBLASVersion)),
                             "-DCMAKE_INSTALL_PREFIX=" + install_prefix]

            subprocess.check_call(cmake_cmd)
            subprocess.check_call(['make', '-j2'])
            subprocess.check_call(
                ["cmake", "--build", '.', '--target', 'install'])

            guess_libblas = glob.glob(os.path.join(
                install_prefix, 'lib*', '*openblas*'))[0]
            target_libblas = guess_libblas.replace(
                'openblas', 'pylib_openblas')
            copyfile(guess_libblas, os.path.basename(target_libblas))

            os.chdir(cwd)

        def build4win():
            try:
                import urllib.request as request
            except ImportError:
                import urllib as request

            arch = 'x64'
            import platform
            if platform.architecture()[0] == '32bit':
                arch = 'x86'

            fname = "OpenBLAS-{version}-{tarch}".format(
                version=OpenBLASVersion, tarch=arch)

            fname_zip = fname + ".zip"

            print("Downloading OpenBLAS version {} arch {}".format(
                OpenBLASVersion, arch))
            request.urlretrieve(
                "https://github.com/xianyi/OpenBLAS/releases/download/v{version}/OpenBLAS-{version}-{tarch}.zip".format(version=OpenBLASVersion, tarch=arch), fname_zip)

            cwd = os.getcwd()
            guess_libplat = glob.glob(os.path.join(cwd, 'build', 'lib*'))[0]
            install_dir = os.path.join(guess_libplat, 'pylib_openblas')

            import zipfile
            print("Extracting OpenBLAS version {}".format(OpenBLASVersion))
            with zipfile.ZipFile(fname_zip, 'r') as zip_ref:
                zip_ref.extractall(install_dir)

            try:
                os.makedirs(self.build_temp)
            except OSError:
                pass

            guess_libblas = glob.glob(os.path.join(
                install_dir, 'lib', '*.lib'))[0]
            print('guess_libblas is {}'.format(guess_libblas))
            libplacehoder = os.path.join(self.build_temp, name + ".lib")
            copyfile(guess_libblas, libplacehoder)

        if platform == "win32":
            build4win()
        else:
            build4linux()


setup(name=name,
      version='0.0.2',
      packages=[name],
      libraries=[(name, {'sources': ['pylib_openblas/libplacehoder.c']})],
      description=des,
      long_description='Binary distribution of OpenBLAS static libraries',
      author='chenkui164',
      ext_modules=[Extension("pylib_openblas.placeholder", [
                             'pylib_openblas/placeholder.c'])],
      cmdclass={'build_clib': MyBuildCLib, 'bdist_wheel': bdist_wheel},
      options={'bdist_wheel': {'universal': True}})
