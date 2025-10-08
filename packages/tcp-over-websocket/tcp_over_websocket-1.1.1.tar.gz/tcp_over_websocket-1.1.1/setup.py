import os
import shutil

from setuptools import find_packages
from setuptools import setup

from tcp_over_websocket.util.windows_util import isWindows

###############################################################################
# Define variables
#
# Modify these values to fork a new plugin
#

author = "Synerty"
author_email = "contact@synerty.com"
py_package_name = "tcp_over_websocket"
pip_package_name = py_package_name.replace("_", "-")
package_version = "1.1.1"
description = "TCP over HTTPS Upgraded Websocket with Mutual TLS"

download_url = (
    "https://codeload.github.com/Synerty/tcp-over-websocket"
    "/zip/refs/heads/master"
)
url = "https://github.com/Synerty/tcp-over-websocket"

###############################################################################
# Customise the package file finder code

egg_info = "%s.egg-info" % pip_package_name
if os.path.isdir(egg_info):
    shutil.rmtree(egg_info)

if os.path.isfile("MANIFEST"):
    os.remove("MANIFEST")

excludePathContains = ("__pycache__", "node_modules", "platforms", "dist")
excludeFilesEndWith = (".pyc", ".js", ".js.map", ".lastHash")
excludeFilesStartWith = ()


def find_package_files():
    paths = []
    for path, directories, filenames in os.walk(py_package_name):
        if [e for e in excludePathContains if e in path]:
            continue

        for filename in filenames:
            if [e for e in excludeFilesEndWith if filename.endswith(e)]:
                continue

            if [e for e in excludeFilesStartWith if filename.startswith(e)]:
                continue

            paths.append(
                os.path.join(path[len(py_package_name) + 1 :], filename)
            )

    return paths


package_files = find_package_files()

###############################################################################
# Define the dependencies

# Ensure the dependency is the same major number
# and no older than this version

requirements = [
    "vortexpy==3.4.3",
    "txhttputil==1.2.8",
    "json-cfg-rw==0.5.0",
    "twisted[tls]==22.10.0",
    "reactivex==4.0.4",
]

if isWindows:
    requirements.extend(
        [
            "pypiwin32",
        ]
    )

###############################################################################
# Call the setuptools

setup(
    entry_points={
        "console_scripts": [
            "run_tcp_over_websocket_service"
            " = tcp_over_websocket.run_tcp_over_websocket_service:main",
            "winsvc_tcp_over_websocket_service"
            " = tcp_over_websocket.winsvc_tcp_over_websocket_service:main",
        ],
    },
    name=pip_package_name,
    packages=find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests"]
    ),
    package_data={"": package_files},
    install_requires=requirements,
    zip_safe=False,
    version=package_version,
    description=description,
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author=author,
    author_email=author_email,
    url=url,
    download_url=download_url,
    keywords=["TCP", "Websocket", "MutualTLS", "synerty", "tunnel", "proxy"],
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: System :: Networking",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)