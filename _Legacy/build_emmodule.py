import setuptools
module1 = setuptools.Extension(
    'entity_manager2',
    include_dirs=['/Users/Leo/AppData/Local/Programs/Python/Python312/include'],
    sources=['C Files/entitymanagermodule.c']
)
setuptools.setup(name='entity_manager2',version='0.8',author='hithere32123',ext_modules=[module1])

