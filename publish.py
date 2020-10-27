#!/usr/bin/env python3

import os, shutil, sys

from httk.httkweb import publish

if not os.path.exists("docs"):
    os.mkdir("docs")

for filename in os.listdir("docs"):
    if not filename.startswith("."):
        f = os.path.join("docs",filename)
        if os.path.isdir(f):
            shutil.rmtree(f)
        else:
            os.unlink(f)

publish("src","docs",'http://127.0.0.1/')
