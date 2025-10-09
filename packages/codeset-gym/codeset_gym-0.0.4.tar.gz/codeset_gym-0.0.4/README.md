# Codeset Gym

A Python package for testing code patches in Docker containers.

## Installation

```bash
uv sync
```

## Usage

```bash
docker login -u <USER> -p <PASSWORD> <REPOSITORY>
python -m codeset_gym <instance_id> <repository> <dataset>
```

## Build and Publich

```bash
export UV_PUBLISH_TOKEN=pypi-your-token-here
uv build
uv publish
```

## License

MIT
