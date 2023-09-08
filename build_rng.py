from distutils.core import setup, Extension

module1 = Extension('rng',
            include_dirs = ['/Users/Leo/AppData/Local/Programs/Python/Python310/include'],
            #libraries = [''],
            sources = ['rngmodule.c'])

setup(name = 'rng', version = '0.2',description = 'contains code for LCG and PCG rng', author='hithere32123',url='https://www.example.com',ext_modules=[module1])
