"""Execute the quickstart's import and serving scripts against a real HTTP API."""

import json
import re
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import urlopen


def main() -> None:
    """Verify durable import, reopening, structures, energies, and strong links."""
    page = Path(sys.argv[1]).resolve()
    section = page.read_text(encoding="utf-8").split("Serve data over OPTIMADE", 1)[1]
    blocks = re.findall(r"^```(\w+)\n(.*?)^```", section, re.MULTILINE | re.DOTALL)
    python = [code for language, code in blocks if language == "python"]
    inputs = next(code for language, code in blocks if language == "json")
    assert len(python) == 2
    with TemporaryDirectory(prefix="httk-serving-example-") as directory:
        root = Path(directory)
        (root / "cifs").mkdir()
        downloads = re.findall(r"\]\((examples/optimade/[^)]+\.cif)\)", section)
        assert len(downloads) == 2
        for download in downloads:
            shutil.copyfile(page.parents[1] / "static" / download, root / "cifs" / Path(download).name)
        (root / "results.json").write_text(inputs, encoding="utf-8")
        (root / "import_data.py").write_text(python[0], encoding="utf-8")
        # The second import must deduplicate; serving must not read the source files.
        for _ in range(2):
            subprocess.run([sys.executable, "import_data.py"], cwd=root, check=True, timeout=60)
        (root / "results.json").unlink()
        shutil.rmtree(root / "cifs")
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            port = listener.getsockname()[1]
        (root / "api.py").write_text(python[1].replace("port=8080", f"port={port}"), encoding="utf-8")
        base = f"http://127.0.0.1:{port}"

        def get(path, **params):
            with urlopen(base + path + "?" + urlencode(params), timeout=15) as response:
                return json.load(response)

        with (root / "server.log").open("w+") as log:
            server = subprocess.Popen([sys.executable, "api.py"], cwd=root, stdout=log, stderr=log)
            try:
                deadline = time.monotonic() + 20
                while True:
                    if server.poll() is not None or time.monotonic() > deadline:
                        log.seek(0)
                        raise AssertionError(f"OPTIMADE server did not start:\n{log.read()}")
                    try:
                        get("/v1/info")
                        break
                    except URLError:
                        time.sleep(0.05)
                records = get("/v1/_httk_records")["data"]
                structures = get("/v1/structures")["data"]
                assert len(records) == len(structures) == 2
                assert {s["attributes"]["nsites"] for s in structures} == {8}
                formulas = {s["id"]: s["attributes"]["chemical_formula_reduced"] for s in structures}
                assert set(formulas.values()) == {"ClNa", "MgO"}
                expected = {"ClNa": -1.2, "MgO": -0.8}
                for record in records:
                    (link,) = record["relationships"]["_httk_structure"]["data"]
                    assert link["type"] == "structures"
                    assert link["meta"] == {"_httk_label": "structure", "role": "subject"}
                    assert record["attributes"]["_httk_custom_formation_energy"] == expected[formulas[link["id"]]]
                info = get("/v1/info/_httk_records")["data"]["properties"]
                assert info["_httk_custom_formation_energy"]["x-optimade-unit"] == "eV"
                payload = get(
                    "/v1/_httk_records",
                    filter="_httk_custom_formation_energy < -1",
                    include="structures",
                )
                (result,) = payload["data"]
                assert result["attributes"]["_httk_custom_formation_energy"] == -1.2
                (structure,) = payload["included"]
                assert structure["attributes"]["chemical_formula_reduced"] == "ClNa"
                assert result["relationships"]["_httk_structure"]["data"][0]["id"] == structure["id"]
                related = get(
                    "/v1/_httk_records",
                    filter=f'_httk_relationships._httk_structure.id HAS "{structure["id"]}"',
                )
                assert [r["id"] for r in related["data"]] == [result["id"]]
            finally:
                server.terminate()
                try:
                    server.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    server.kill()
                    server.wait()
                    raise AssertionError("OPTIMADE server did not stop") from None
    print(f"{page.name}: import, deduplication, reopening without inputs, and HTTP strong links passed")


if __name__ == "__main__":
    main()
