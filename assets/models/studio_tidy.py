"""Tidies a map's imported props and monsters in Roblox Studio, after the owner's import (docs/MAP_RECIPE.md step 8).

    python3 assets/models/studio_tidy.py EclipseTemple build_eclipse_temple build_eclipse_temple_monsters

Reads each model's role colours from the build scripts (through Blender), then runs studio_tidy.luau in the open
Studio through its MCP server (memory: studio-mcp-connection). Models it can't find in Workspace are listed.
"""
import json
import select
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
BLENDER = "/Applications/Blender.app/Contents/MacOS/Blender"
STUDIO_MCP = "/Applications/RobloxStudio.app/Contents/MacOS/StudioMCP"

DUMP = """
import json, sys
sys.path.insert(0, %r)
import importlib
import build_forest as kit
out, chrome = {}, {}
for name in %r:
    module = importlib.import_module(name)
    metal = getattr(module, "METAL", {})  # role -> MaterialVariant, for this script's models only
    for make in module.ALL:
        m = make()
        out[m.name] = {role: m.colours[role] for role in m.parts}
        chrome[m.name] = {role: metal[role] for role in m.parts if role in metal}
print("JSON" + json.dumps({"colours": out, "nostuds": sorted(kit.NO_STUDS), "chrome": chrome}))
"""


def colours(modules):
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(DUMP % (str(HERE), modules))
    out = subprocess.run([BLENDER, "-b", "--python", f.name], capture_output=True, text=True).stdout
    return json.loads(next(line[4:] for line in out.splitlines() if line.startswith("JSON")))


def lua(value):
    if isinstance(value, dict):
        return "{" + ", ".join(f'["{k}"] = {lua(v)}' for k, v in value.items()) + "}"
    return f'"{value}"'


class Studio:
    def __init__(self):
        self.p = subprocess.Popen([STUDIO_MCP], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        self.n = 0
        self.call("initialize", {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "tidy", "version": "1"}})
        self.p.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
        self.p.stdin.flush()

    def call(self, method, params):
        self.n += 1
        self.p.stdin.write(json.dumps({"jsonrpc": "2.0", "id": self.n, "method": method, "params": params}) + "\n")
        self.p.stdin.flush()
        end = time.time() + 300
        while time.time() < end:
            if select.select([self.p.stdout], [], [], 1)[0]:
                d = json.loads(self.p.stdout.readline())
                if d.get("id") == self.n:
                    return d
        sys.exit("Studio didn't answer")

    def text(self, tool, args):
        return "\n".join(c.get("text", "") for c in self.call("tools/call", {"name": tool, "arguments": args})["result"]["content"])


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    world, modules = sys.argv[1], sys.argv[2:]
    data = colours(modules)
    code = (f'local WORLD = "{world}"\nlocal COLOURS = {lua(data["colours"])}\n'
            f'local NOSTUDS = {{{", ".join(f"[{chr(34)}{r}{chr(34)}] = true" for r in data["nostuds"])}}}\n'
            + f'local CHROME = {lua(data["chrome"])}\n'
            + (HERE / "studio_tidy.luau").read_text())
    studio = Studio()
    sid = json.loads(studio.text("list_roblox_studios", {}))["studios"][0]["id"]
    print(studio.text("execute_luau", {"studio_id": sid, "datamodel_type": "Edit", "code": code}))
    studio.p.terminate()


main()
