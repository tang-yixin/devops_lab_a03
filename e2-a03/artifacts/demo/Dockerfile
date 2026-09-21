FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends gcc make libc6-dev && rm -rf /var/lib/apt/lists/*
WORKDIR /workspace/project
COPY . .
RUN make && make test EXPECTED=1
