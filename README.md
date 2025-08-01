
```bash
uv run pytest

uv run flask --app bazel_app run
```

```bash
# Server image
docker build .

# Tests using the image
docker build . -f ./Dockerfile.test
```
