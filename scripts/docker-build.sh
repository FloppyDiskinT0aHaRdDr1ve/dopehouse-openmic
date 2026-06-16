#!/bin/bash
# Build and push Docker images for DOPEHOUSE OPENMIC
set -e
VERSION="${1:-latest}"
IMAGE_GHCR="ghcr.io/floppydiskint0aharddr1ve/dopehouse-openmic:$VERSION"
IMAGE_DOCKERHUB="${DOCKER_USERNAME}/dopehouse-openmic:$VERSION"
echo "Building $IMAGE_GHCR ..."
docker build -t $IMAGE_GHCR .
docker tag $IMAGE_GHCR $IMAGE_DOCKERHUB
docker push $IMAGE_GHCR
docker push $IMAGE_DOCKERHUB
echo "Done"
