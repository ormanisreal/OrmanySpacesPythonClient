import yaml, os
from pathlib import Path as GetHomePath 
# If you want to override the default config path, 
# change False to that directory with no leading slash
# e.g. 
#       OVERRIDE_CFG_PATH=/srv/an/ass/who/hates/defaults
OVERRIDE_CFG_PATH=False
# Note: Override path entered above will be 
# appended with /.orman , e.g. ...defaults/.orman
# This is the ONLY setting that can or should be 
# configured outside of the orman.yml file 
def Config(Path=None,File="orman.yml"):
    """
    This function opens the orman.yml config file and cnverts it to json.
    By default it looks in your home directory under .orman:
            ~/.orman/orman.yml
    Returns a dict with the paths for orman.key and namespace.orman
    """
    if Path == None:
        if OVERRIDE_CFG_PATH:
            Path = OVERRIDE_CFG_PATH
        else:
            Path = ( "%s/.orman" % ( str( GetHomePath.home() ) ) )
    config_path = ( "%s/%s" % (Path, File) )
    with open(config_path) as yml_config:
        c = yaml.full_load(yml_config)
    Paths = c['orman']['Paths']
    paths = dict()
    for path in Paths:
        paths[path] = Paths[path]['Path']
    spaces_endpoint = c['orman']['Endpoints']['OrmanSpaces']
    os.environ["ORMAN_SPACES_ENDPOINT"] = spaces_endpoint
    return paths
