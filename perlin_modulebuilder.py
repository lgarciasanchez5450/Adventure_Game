from distutils.core import setup, Extension

module1 = Extension('Perlin',
            include_dirs = ['/Users/Leo/AppData/Local/Programs/Python/Python310/include'],
            #libraries = [''],
            sources = ['perlin.c'])

setup(name = 'Perlin', version = '0.22',description = 'hehehehaw', author='hithere32123',url='https://www.example.com',ext_modules=[module1])
