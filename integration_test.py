# Based on https://github.com/aspect-build/bazel-examples/blob/main/oci_python_image/hello_world/integration_test.py

from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs
import logging


# This function is self container for easy-to-use by just copy-pasting.
def OCIImageContainer(image):
    import docker
    import tarfile
    import json
    import io
    import logging
    
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

    logger = logging.getLogger("incremental_loader")

    def tar(*args):
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode="w:") as t:
            for name, size, contents in args:
                info = tarfile.TarInfo(name=name)
                info.size = size
                if isinstance(contents, list) or isinstance(contents, dict):
                    content = json.dumps(contents).encode("utf-8")
                    info.size = len(content)
                    contents = io.BytesIO(content)

                t.addfile(info, fileobj=contents)
                contents.close()
        return buffer

    def config_json(diff_ids):
        return (
            "config.json",
            None,
            {"rootfs": {"type": "layers", "diff_ids": diff_ids}},
        )

    def manifest_json(layers):
        return (
            "manifest.json",
            None,
            [{"Config": "config.json", "RepoTags": [], "Layers": layers}],
        )

    def open_blob(image, digest):
        blob_path = "%s/blobs/%s" % (image, digest.replace(":", "/"))
        return open(blob_path, "rb")

    with open("%s/index.json" % image) as indexp:
        indexjson = json.load(indexp)

    with open_blob(image, indexjson["manifests"][0]["digest"]) as manifestp:
        manifest = json.load(manifestp)

    with open_blob(image, manifest["config"]["digest"]) as configp:
        config = json.load(configp)

    client = docker.from_env()
    
    layers = manifest["layers"]
    # Load all layers at once
    load = tar(
        *[
            (layer["digest"] + ".tar", layer["size"], open_blob(image, layer["digest"]))
            for layer in layers
        ],
        manifest_json(
            layers=[layer["digest"] + ".tar" for layer in manifest["layers"]]
        ),
        (
            "config.json",
            manifest["config"]["size"],
            open_blob(image, manifest["config"]["digest"]),
        ),
    )

    load_res = client.images.load(load.getvalue())

    return DockerContainer(load_res[0].id)


import requests
from pytest import fixture
from pathlib import Path
from typing import Generator

DOG = Path(__file__).parent / "tests" / "dog.jpg"


@fixture(scope="session")
def server() -> Generator[OCIImageContainer, None, None]:
    with OCIImageContainer("image").with_exposed_ports(5000) as container:
        wait_for_logs(container, "Running on")
        yield container


@fixture(scope="session")
def server_url(server: OCIImageContainer) -> str:
    host = server.get_container_host_ip()
    port = server.get_exposed_port(5000)
    server_url = f"http://{host}:{port}"
    logging.info("Server is ready at {server_url}")
    return server_url


def test_hello(server_url: str):
    resp = requests.get(f"{server_url}/", data=DOG.read_bytes())
    resp.raise_for_status()


def test_classify(server_url: str):
    resp = requests.post(f"{server_url}/classify", data=DOG.read_bytes())
    resp.raise_for_status()

    classification = resp.json()
    assert classification != {}, f"Unexpected classification: {classification}"
