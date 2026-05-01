FROM ubuntu:26.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        bash \
        bats \
        ca-certificates \
        coreutils \
        git \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --shell /bin/bash tester

WORKDIR /work/repo
COPY . /work/repo
RUN chown -R tester:tester /work/repo

USER tester
ENV HOME=/home/tester
ENV USER=tester

CMD ["bats", "tests/bash/bootstrap_relink_integration.bats"]
