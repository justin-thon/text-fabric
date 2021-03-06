from ..fabric import Fabric
from ..lib import readSets
from ..core.helpers import console, setDir
from .app import findAppConfig
from .helpers import getLocalDir, configure
from .links import linksApi
from .sections import sectionsApi
from .displaysettings import displaySettingsApi
from .display import displayApi
from .search import searchApi
from .data import getModulesData


# SET UP A TF API FOR AN APP

def setupApi(
    app,
    appName,
    appDir,
    commit,
    hoist=False,
    version=None,
    mod=None,
    lgc=False,
    check=False,
    locations=None,
    modules=None,
    api=None,
    setFile='',
    silent=False,
    _asApp=False,
):
  for (key, value) in dict(
      appName=appName,
      _asApp=_asApp,
      api=api,
      version=version,
      silent=silent,
  ).items():
    setattr(app, key, value)

  app.appDir = appDir
  app.commit = commit

  config = findAppConfig(appName, appDir)
  cfg = configure(config, lgc, version)
  version = cfg['version']
  cfg['localDir'] = getLocalDir(cfg, lgc, version)
  for (key, value) in cfg.items():
    setattr(app, key, value)

  setDir(app)

  if app.api:
    if app.standardFeatures is None:
      allFeatures = app.api.TF.explore(silent=True, show=True)
      loadableFeatures = allFeatures['nodes'] + allFeatures['edges']
      app.standardFeatures = loadableFeatures
  else:
    app.sets = None
    if setFile:
      sets = readSets(setFile)
      if sets:
        app.sets = sets
        console(f'Sets from {setFile}: {", ".join(sets)}')
    specs = getModulesData(
        app,
        mod,
        locations,
        modules,
        version,
        lgc,
        check,
        silent,
    )
    if specs:
      (locations, modules) = specs
      TF = Fabric(locations=locations, modules=modules, silent=True)
      api = TF.load('', silent=True)
      if api:
        app.api = api
        allFeatures = TF.explore(silent=True, show=True)
        loadableFeatures = allFeatures['nodes'] + allFeatures['edges']
        if app.standardFeatures is None:
          app.standardFeatures = loadableFeatures
        useFeatures = [f for f in loadableFeatures if f not in app.excludedFeatures]
        result = TF.load(useFeatures, add=True, silent=True)
        if result is False:
          app.api = None
    else:
      app.api = None

  if app.api:
    linksApi(app, appName, silent)
    searchApi(app)
    sectionsApi(app)
    displaySettingsApi(app)
    displayApi(app, silent, hoist)
  else:
    if not _asApp:
      console(
          f'''
There were problems with loading data.
The Text-Fabric API has not been loaded!
The app "{appName}" will not work!
''',
          error=True,
      )
