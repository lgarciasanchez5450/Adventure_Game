from distutils.core import setup, Extension

module1 = Extension('entity_manager',
            include_dirs = ['/Users/Leo/AppData/Local/Programs/Python/Python310/include'],
            #libraries = [''],
            sources = ['entitymanagermodule.c'])

setup(name = 'entity_manager', version = '0.27',description = 'hehehehaw', author='hithere32123',url='https://www.example.com',ext_modules=[module1])
