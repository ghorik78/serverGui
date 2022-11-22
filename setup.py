from cx_Freeze import setup, Executable

executables = [Executable('main.py')]


excludes = ['unicodedata', 'logging', 'unittest', 'email', 'html', 'http', 'urllib',
            'xml', 'pydoc', 'doctest', 'argparse', 'datetime', 'zipfile',
            'subprocess', 'pickle', 'threading', 'locale', 'calendar', 'tokenize', 'base64', 'gettext',
            'bz2', 'getopt', 'stringprep', 'quopri', 'copy', 'imp', 'linecache']

includes = ['re', 'json']

zip_include_packages = ['collections', 'encodings', 'importlib']

options = {
    'build_exe': {
        'include_msvcr': True,
        'includes': includes,
        'zip_include_packages': zip_include_packages,
    }
}

setup(name='RoboApp',
      version='1.0',
      executables=executables,
      options=options)