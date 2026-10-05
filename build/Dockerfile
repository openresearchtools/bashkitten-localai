# Mainstream native Linux build, adapted from llama-cpp-arm64-builds d6e2239e.
# SPDX-License-Identifier: AGPL-3.0-only
FROM node:24-bookworm-slim@sha256:0e0ff40c39bc087845bfb27465a0df4ea419520094bc35842ff83dd8cbe6f9b6 AS node
FROM ubuntu:24.04@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55 AS build
ARG TARGETARCH
ARG ENGINE
ARG BACKEND
ARG SOURCE_COMMIT
ARG UPSTREAM_VERSION
ARG RELEASE_TAG
ENV DEBIAN_FRONTEND=noninteractive
COPY --from=node /usr/local/ /usr/local/
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates curl gnupg git build-essential cmake ninja-build pkg-config python3 libgomp1 libvulkan-dev glslc spirv-headers xz-utils && rm -rf /var/lib/apt/lists/*
RUN if [ "$BACKEND" = cuda ]; then \
    case "$TARGETARCH" in amd64) cuda_arch=x86_64;; arm64) cuda_arch=sbsa;; *) exit 1;; esac; \
    cuda_repo="https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/$cuda_arch"; \
    curl -fLsS "$cuda_repo/3bf863cc.pub" | gpg --dearmor -o /usr/share/keyrings/nvidia-cuda.gpg; \
    printf 'deb [signed-by=/usr/share/keyrings/nvidia-cuda.gpg] %s /\n' "$cuda_repo" > /etc/apt/sources.list.d/cuda.list; \
    apt-get update && apt-get install -y --no-install-recommends cuda-nvcc-13-2 cuda-cudart-dev-13-2 libcublas-dev-13-2 && rm -rf /var/lib/apt/lists/*; \
    fi
ENV PATH=/usr/local/cuda-13.2/bin:${PATH}
ENV CUDAToolkit_ROOT=/usr/local/cuda-13.2
WORKDIR /src
COPY src/ ./
COPY build/package.py /package.py
COPY build/DONOR-LICENSE /donor-license
COPY LICENSE /build-license
RUN python3 /package.py build
FROM scratch AS artifact
COPY --from=build /out/ /
