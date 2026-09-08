"""Execute the public quickstarts and check their displayed output."""

import re
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


def main() -> None:
    """Run each self-contained quickstart in a fresh temporary directory."""
    content = Path(__file__).resolve().parent / "src" / "content"
    for name in ("vectors", "structures", "databases"):
        page = content / f"quickstart-{name}.md"
        text = page.read_text(encoding="utf-8")
        script = ["import contextlib, io"]
        blocks = list(re.finditer(r"^```python\n(.*?)^```", text, re.MULTILINE | re.DOTALL))
        assert blocks, f"{page}: no examples found"
        for index, block in enumerate(blocks):
            script.append("output = io.StringIO()")
            script.append("with contextlib.redirect_stdout(output):")
            script.append(f"    exec(compile({block[1]!r}, {str(page)!r}, 'exec'))")
            end = blocks[index + 1].start() if index + 1 < len(blocks) else len(text)
            expected = re.search(r"Running[^\n]*output:\n```\n(.*?)\n```", text[block.end() : end], re.DOTALL)
            if expected:
                script.append(f"assert output.getvalue().strip() == {expected[1].strip()!r}, output.getvalue()")
        with TemporaryDirectory(prefix="httk-website-example-") as directory:
            subprocess.run([sys.executable, "-I", "-c", "\n".join(script)], cwd=directory, check=True, timeout=180)
        print(f"{page.name}: {len(blocks)} examples passed")


if __name__ == "__main__":
    main()
