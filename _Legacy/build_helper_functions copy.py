
from distutils.core import setup, Extension
import sysconfig
extra_compile_args = [] #sysconfig.get_config_var('CFLAGS').split()
extra_compile_args += ['-DNDEBUG','-O3'] #dndebug means to disable assertions
module1 = Extension('helper_functions',
            include_dirs = ['/Users/Leo/AppData/Local/Programs/Python/Python310/include'],
            #libraries = [''],
            sources = ['helper_functions.c'],
            extra_compile_args=extra_compile_args
            )

setup(name = 'helper_functions', version = '0.9',description = 'hehehehaw', author='hithere32123',url='https://www.example.com',ext_modules=[module1])
