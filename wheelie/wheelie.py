
# coding: utf-8

# In[1]:



try:
    from . import setup
except: 
    import setup
    
from IPython import get_ipython


# In[2]:


import sys, nbconvert.nbconvertapp, tempfile, setuptools.command, wheel.bdist_wheel
from traitlets import *
from pathlib import Path
import json
import shutil
import os
from itertools import chain


# In[3]:


nbconvert.nbconvertapp.NbConvertApp.export_format.default_value = 'python'


# In[4]:


def move_files_with_parents(build_directory, root, *files, log=None):
    for file in chain(
        *(Path(root).glob(file) if '*' in file else (Path(file),) for file in files)
    ):
        (build_directory/(file).relative_to('.')).parent.mkdir(exist_ok=True)
        shutil.copy(
            file, build_directory / file.relative_to(root))
        log and log.info("""Moving {file} to the package.""".format(file=file))
def create_modules(build_directory): 
    for file in filter(Path.is_dir, build_directory.iterdir()):
        init = file / '__init__.py'
        init.exists() or init.touch()


# In[5]:


def create_package_data(build_directory, package_data):
    from collections import defaultdict
    package_data = defaultdict(list)
    name = build_directory.stem
    for file in build_directory.rglob('*'):
        if file.is_file() and file.suffix != '.py':
            package_data['.'.join(file.relative_to(build_directory).parent.parts)].append(str(file))
    return package_data


# In[6]:


class WheelApp(nbconvert.nbconvertapp.NbConvertApp):
    name = Unicode(allow_none=True).tag(config=True)
    version = Unicode(default_value='0.0.1').tag(config=True)
    root = Unicode(default_value='.').tag(config=True)
    output = Unicode('.').tag(config=True)
    
    python_files = List(default_value=[]).tag(config=True)
    package_data = List(default_value=[]).tag(config=True)
    
    def convert_notebooks(self):
        self.notebooks = [str(Path(self.root)/notebook) for notebook in self.notebooks]
        self.exporter = nbconvert.get_exporter(self.export_format)(config=self.config)
        self.initialize(argv=tuple())
        with tempfile.TemporaryDirectory() as path:
            path = Path(path)
            build_directory = path / self.name
                        
            for notebook in self.notebooks:
                self.writer = nbconvert.writers.files.FilesWriter(
                    build_directory=str((build_directory / notebook).parent))
                self.convert_single_notebook(notebook)
            
            
            move_files_with_parents(build_directory, self.root, *self.python_files, *self.package_data)
            create_modules(build_directory)                        
            
            distribution = setup.setup(
                self.name, build_directory, wheel_dir=self.output,
                package_data=create_package_data(build_directory, self.package_data),
                version=self.version)
            
#             # Add the ability to include python files and data files
            
                  
            distribution.run_command('bdist_wheel')
            wheel = Path(self.output) / distribution.wheel_info
            self.log.info("""{0} created.  
Run "pip install {1} --no-cache-dir --upgrade" to reuse this package.""".format(
                distribution.wheel_info, wheel
            ))
            
        
        
        return wheel


# In[ ]:


main = WheelApp.launch_instance


# In[ ]:


if __name__ == '__main__':
    get_ipython().system('jupyter nbconvert --to python wheelie.ipynb')


# WheelApp(name='testable', notebooks='*.ipynb **/*.ipynb'.split(), python_files='*.py'.split(), package_data=[], output='somewhere').convert_notebooks()
