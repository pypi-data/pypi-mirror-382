import os
import ruamel.yaml
import json


from sphinx.application import Sphinx
from sphinx.util.fileutil import copy_asset_file

try:
    from ._version import version as __version__
except ImportError:
    __version__ = "1.0.0"

def copy_buttons(app: Sphinx, exc: None) -> None:
    print("[sphinx-launch-buttons] initialised, adding directories.")

    # Define path to js file 
    current_dir = os.path.dirname(__file__)
    js_file = os.path.join(current_dir, 'static', 'launch_buttons.js')

    if app.builder.format == 'html' and not exc:
        
        # Define paths to data files
        staticdir = os.path.join(app.builder.outdir, '_static')
        launch_buttons_yaml = os.path.join(app.builder.srcdir, '_launch_buttons.yml')
    
        # Convert _launch_buttons.yaml to _launch_buttons.json so it can be read in javascript
        # Only proceed if the YAML exists. If it doesn't, don't copy assets or write files
        # so no buttons will be shown in the frontend.
        if not os.path.exists(launch_buttons_yaml):
            print(f"[sphinx-launch-buttons] no _launch_buttons.yml found; skipping asset install.")
            return

        # Ensure the static directory exists
        try:
            os.makedirs(staticdir, exist_ok=True)
        except Exception:
            print(f"[sphinx-launch-buttons] could not create static dir: {staticdir}")

        json_target = os.path.join(staticdir, '_launch_buttons.json')

        try:
            yaml_to_json(launch_buttons_yaml, json_target)
        except Exception as e:
            print(f"[sphinx-launch-buttons] error converting yaml to json: {e}")

        # Copy the JS and YAML assets
        try:
            copy_asset_file(js_file, staticdir)
        except Exception as e:
            print(f"[sphinx-launch-buttons] error copying js asset: {e}")
        try:
            copy_asset_file(launch_buttons_yaml, staticdir)
        except Exception as e:
            print(f"[sphinx-launch-buttons] error copying yaml asset: {e}")

# Function to convert yaml to json to prevent mixing of yaml and json for the user.
def yaml_to_json(yaml_file: str, json_file: str) -> None:
    with open(yaml_file, 'r') as ymlfile:
        yaml = ruamel.yaml.YAML(typ='safe')
        data = yaml.load(ymlfile)
        with open(json_file, 'w') as jsonfile:
            json.dump(data, jsonfile, indent=4)

def setup(app: Sphinx) -> dict[str, str]:
    # Only register the JS and the build-finished handler if the project provides
    # a `_launch_buttons.yml` file. If we always add the JS, Sphinx will reference
    # `launch_buttons.js` even when it's not copied into `_static`, causing a 404.
    launch_buttons_yaml = os.path.join(getattr(app, 'srcdir', ''), '_launch_buttons.yml')
    if os.path.exists(launch_buttons_yaml):
        app.add_js_file('launch_buttons.js')
        app.connect('build-finished', copy_buttons)
    else:
        # No config present: don't register assets or handlers.
        print('[sphinx-launch-buttons] no _launch_buttons.yml found during setup; not registering assets')

    return {'parallel_read_safe': True, 'parallel_write_safe': True}
