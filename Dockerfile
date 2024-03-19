FROM registry-git.lsd.ufcg.edu.br/pedro.serey/awsome-savings:or-tools

COPY cpp/*.cpp cpp/*.h cpp/Makefile util/*.sh /optimizer/

WORKDIR /optimizer

RUN make compile && \
    chmod +x ./run_optimization.sh && \
    chmod +x ./collect-cpu-usage.sh && \
    chmod +x ./collect-memory-usage.sh

VOLUME ["/optimizer-files"]
VOLUME ["/optimizer-logs"]

ENV LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

CMD ["/bin/sh", "-c", "echo AWSome-Savings!"]
