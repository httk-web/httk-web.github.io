"""Execute the quickstart's CIF/JSON example and query its real HTTP API."""

import json
import re
import runpy
import shutil
import socket
import sys
import threading
import time
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import urlencode
from urllib.request import urlopen

import uvicorn
from httk.serve.optimade import create_asgi_app


def main() -> None:
    """Load the published inputs and verify structures, energies, and links."""
    page = Path(sys.argv[1]).resolve()
    section = page.read_text(encoding="utf-8").split("Serve data over OPTIMADE", 1)[1]
    blocks = re.findall(r"^```(\w+)\n(.*?)^```", section, re.MULTILINE | re.DOTALL)
    python = [code for language, code in blocks if language == "python"]
    inputs = next(code for language, code in blocks if language == "json")
    assert len(python) == 1
    with TemporaryDirectory(prefix="httk-serving-example-") as directory:
        root = Path(directory)
        (root / "cifs").mkdir()
        downloads = re.findall(r"\]\((examples/optimade/[^)]+\.cif)\)", section)
        assert len(downloads) == 2
        for download in downloads:
            shutil.copyfile(page.parents[1] / "static" / download, root / "cifs" / Path(download).name)
        (root / "results.json").write_text(inputs, encoding="utf-8")
        (root / "api.py").write_text(python[0], encoding="utf-8")
        api = runpy.run_path(str(root / "api.py"))
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            port = listener.getsockname()[1]
            server = uvicorn.Server(uvicorn.Config(create_asgi_app(api["adapter"]), log_level="error"))
            thread = threading.Thread(target=server.run, kwargs={"sockets": [listener]}, daemon=True)
            thread.start()
            try:
                deadline = time.monotonic() + 15
                while not server.started and thread.is_alive() and time.monotonic() < deadline:
                    time.sleep(0.05)
                assert server.started, "OPTIMADE server did not start"
                base = f"http://127.0.0.1:{port}"

                def get(path, **params):
                    with urlopen(base + path + "?" + urlencode(params), timeout=15) as response:
                        return json.load(response)

                records = get("/v1/_httk_records")["data"]
                structures = get("/v1/structures")["data"]
                assert len(records) == len(structures) == 2
                assert {s["attributes"]["nsites"] for s in structures} == {8}
                assert {s["attributes"]["chemical_formula_reduced"] for s in structures} == {"ClNa", "MgO"}
                for record in records:
                    row = next(row for row in json.loads(inputs) if row["sample"] == record["id"])
                    assert record["attributes"]["_httk_custom_formation_energy"] == row["formation_energy"]
                    assert record["relationships"]["structures"]["data"] == [
                        {
                            "id": row["cif"],
                            "type": "structures",
                            "meta": {"_httk_label": "structure", "role": "subject"},
                        }
                    ]
                info = get("/v1/info/_httk_records")["data"]["properties"]
                assert info["_httk_custom_formation_energy"]["x-optimade-unit"] == "eV"
                payload = get(
                    "/v1/_httk_records",
                    filter="_httk_custom_formation_energy < -1",
                    include="structures",
                )
                assert [r["id"] for r in payload["data"]] == ["nacl-demo"]
                assert [(s["type"], s["id"]) for s in payload["included"]] == [("structures", "NaCl.cif")]
                related = get("/v1/_httk_records", filter='structures.elements HAS "Na"')
                assert [r["id"] for r in related["data"]] == ["nacl-demo"]
            finally:
                server.should_exit = True
                thread.join(timeout=15)
                assert not thread.is_alive(), "OPTIMADE server did not stop"
    print(f"{page.name}: CIF/JSON loading, structures, energies, and HTTP relationships passed")


if __name__ == "__main__":
    main()
