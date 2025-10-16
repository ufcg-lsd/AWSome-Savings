FROM registry-git.lsd.ufcg.edu.br/pedro.serey/awsome-savings:or-tools

COPY implementations/cpp_sp_only/*.cpp implementations/cpp_sp_only/*.h Makefile util/*.sh /optimizer/

WORKDIR /optimizer

RUN make docker-compile && \
    chmod +x ./run_optimization_cpp.sh && \
    chmod +x ./collect-cpu-usage.sh && \
    chmod +x ./collect-memory-usage.sh

VOLUME ["/optimizer-files"]
VOLUME ["/optimizer-logs"]

ENV LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

CMD ["/bin/sh", "-c", "echo AWSome-Savings!"]
