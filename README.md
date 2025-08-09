## Intro 👋🌿

This repo is part of a short talk for PyCon IL 2025,
which shows how to use [Bazel](https://bazel.build/) to build Python code (and why that can be useful).

It contains a small Flask server that can classify images using `resnet50` from [PyTorch Hub](https://pytorch.org/hub/),
that can be built (as a Docker image) using either Docker or Bazel.

The Bazel build requires more complex initial configuration but delivers significantly better caching performance and smaller resulting images.

## Using UV and Docker 🐳

```bash
uv run pytest ./tests

uv run flask --app demo.bazel_app run

wget -O - -q http://localhost:5000/classify --method=POST --body-file=./tests/dog.jpg
```

```bash
# Server image
docker build . -t app

docker run --rm -it -p 5000:5000 app

# Tests using the image
docker build . -f ./Dockerfile.test
```


## Using Bazel 🌿

First, install [bazelisk](https://github.com/bazelbuild/bazelisk) (`brew install bazelisk`).

Then:

```bash
bazel test :test
bazel run :main

bazel run :image_load
docker run --rm -it -p 5000:5000 gcr.io/demo:latest
```

Or, to run the integration test:

```bash
bazel test --test_output=streamed :integration_test
```

To update the `requirements.txt` lock file from the `project.toml`'s dependencies, run:

```bash
bazel run //:requirements.update
```

To create a local virtual env which includes all the deps (but not the libraries or app):

```bash
bazel run //:create_venv
```
