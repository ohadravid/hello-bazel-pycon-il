## Intro 👋🌿

This repo is part of a short talk for PyCon IL 2025,
which shows how to use [Bazel](https://bazel.build/) to build Python code (and why that can be useful).

It contains a small Flask server that can classify images using `resnet50` from [PyTorch Hub](https://pytorch.org/hub/),
that can be built (as a Docker image) using either Docker or Bazel.

The Bazel build requires more complex initial configuration but delivers significantly better caching performance and supports more complex builds (such as Rust native extensions, cross building from macOS to linux aarch64/x86_64, linux specific-lock files, multiarch images, and more).

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

First, install [bazelisk](https://github.com/bazelbuild/bazelisk) (`brew install bazelisk`), which is a Bazel launcher / version manager.

Then, we can use Bazel to execute basic flows:

```bash
# Running unit tests.
bazel test :test

# Launching the server.
bazel run :main

# Building a docker image.
bazel run :image_load
docker run --rm -p 5000:5000 gcr.io/demo:latest
```

Or, to run the integration test:

```bash
bazel test --test_output=streamed :integration_test
```


And to build a multiarch (linux amd64 + aarch64):

```bash

bazel run :image_load_multiarch
docker run --platform linux/amd64 --rm -p 5001:5000 gcr.io/demo:latest-multiarch
```


To create a local virtual env which includes all the deps (but not the libraries or app):

```bash
bazel run //:create_venv
```

### Updating the requirement lock files

We use the `project.toml`'s dependencies as the "source" of dependencies in this example.

For Bazel to be able to build our code, we need to lock these

To update the `requirements_lock.txt` lock file from , run:

```bash
bazel run //:requirements.update
```

And to update the linux-specific file:

```bash
docker run --platform linux/amd64 -it --entrypoint=/bin/bash -v $(pwd):/workspace gcr.io/bazel-public/bazel:latest
bazel run //:requirements.update
```