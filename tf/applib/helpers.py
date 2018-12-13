import os
from importlib import import_module, util
from IPython.display import display, Markdown, HTML

from ..parameters import EXPRESS_BASE, GH_BASE
from ..core.helpers import console, camel

RESULT = 'result'


def dm(md):
  display(Markdown(md))


def dh(html):
  display(HTML(html))


# FIND AN APP


def findAppConfigX(dataSource):
  config = None

  try:
    config = import_module('.config', package=f'tf.apps.{dataSource}')
  except Exception as e:
    console(f'findAppConfig: {str(e)}', error=True)
    console(f'findAppConfig: Configuration for "{dataSource}" not found', error=True)
  return config


def findAppConfig(dataSource):
  config = None
  appPath = os.path.expanduser(f'~/text-fabric-data/__apps__/{dataSource}/config.py')

  try:
    spec = util.spec_from_file_location(f'tf.apps.{dataSource}.config', appPath)
    config = util.module_from_spec(spec)
    spec.loader.exec_module(config)
  except Exception as e:
    console(f'findAppConfig: {str(e)}', error=True)
    console(f'findAppConfig: Configuration for "{dataSource}" not found', error=True)
  return config


def findAppClassX(dataSource):
  appClass = None

  try:
    code = import_module(f'.app', package=f'tf.apps.{dataSource}')
    appClass = code.TfApp
  except Exception as e:
    console(f'findAppClass: {str(e)}', error=True)
    console(f'findAppClass: Api for "{dataSource}" not found')
  return appClass


def findAppClass(dataSource):
  appClass = None
  appPath = os.path.expanduser(f'~/text-fabric-data/__apps__/{dataSource}/app.py')

  try:
    spec = util.spec_from_file_location(f'tf.apps.{dataSource}.app', appPath)
    code = util.module_from_spec(spec)
    spec.loader.exec_module(code)
    appClass = code.TfApp
  except Exception as e:
    console(f'findAppClass: {str(e)}', error=True)
    console(f'findAppClass: Api for "{dataSource}" not found')
  return appClass


# COLLECT CONFIG SETTINGS IN A DICT

def configureNames(names, myDir):
  '''
  Collect the all-uppercase globals from a config file
  and put them in a dict in camel case.
  '''
  result = {camel(key): value for (key, value) in names.items() if key == key.upper()}

  with open(f'{myDir}/static/display.css') as fh:
    result['css'] = fh.read()

  return result


def configure(config, lgc, version):
  (names, path) = config.deliver()
  result = configureNames(names, path)
  result['version'] = config.VERSION if version is None else version
  return result


def getLocalDir(names, lgc, version):
  org = names['org']
  repo = names['repo']
  relative = names['relative']
  version = names['version'] if version is None else version
  base = hasData(lgc, org, repo, version, relative)

  if not base:
    base = EXPRESS_BASE

  return os.path.expanduser(f'{base}/{org}/{repo}/_temp')


def hasData(lgc, org, repo, version, relative):
  versionRep = f'/{version}' if version else ''
  if lgc:
    ghBase = os.path.expanduser(GH_BASE)
    ghTarget = f'{ghBase}/{org}/{repo}/{relative}{versionRep}'
    if os.path.exists(ghTarget):
      return ghBase

  expressBase = os.path.expanduser(EXPRESS_BASE)
  expressTarget = f'{expressBase}/{org}/{repo}/{relative}{versionRep}'
  if os.path.exists(expressTarget):
    return expressBase
  return False
