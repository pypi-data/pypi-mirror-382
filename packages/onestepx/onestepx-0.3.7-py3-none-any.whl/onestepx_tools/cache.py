
import json, pathlib
def load(path):
    p = pathlib.Path(path)
    return json.loads(p.read_text()) if p.exists() else {}
def save(obj, path):
    p = pathlib.Path(path)
    p.write_text(json.dumps(obj, indent=2))
    return p
