FROM civ-phase1:lyrical-resolute

ADD civ-runtime.tar /opt/civ-state/

RUN ln -sfn \
      /opt/civ-state/python/cpython-3.12.11-linux-x86_64-gnu/bin/python3.12 \
      /opt/civ-state/venv/bin/python \
    && sed -i '1s#/opt/civ-runtime/venv#/opt/civ-state/venv#' /opt/civ-state/venv/bin/civ

ENV PATH="/opt/civ-state/venv/bin:${PATH}"
WORKDIR /work

LABEL desktop.docker.io/mounts/0/Source="" \
      desktop.docker.io/mounts/0/SourceKind="" \
      desktop.docker.io/mounts/0/Target="" \
      desktop.docker.io/ports.scheme="" \
      org.opencontainers.image.revision="558e85c0eb50e99a14b819735445d995c7644989"

ENTRYPOINT ["/opt/civ-state/venv/bin/civ"]
CMD ["--help"]
