with open('html_proto.html') as handle:
  prototype_html = handle.read()

with open('py_proto.py') as handle:
  prototype_py = handle.read()

prototype = prototype_html.replace('{{PYTHON_STARTUP}}', prototype_py)

with open('prototype_build.html', 'w+') as handle:
  handle.write(prototype)

import subprocess
subprocess.run(['firefox', 'prototype_build.html'])
