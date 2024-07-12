FROM registry-git.lsd.ufcg.edu.br/pedro.serey/awsome-savings:or-tools

# Optimizer build
WORKDIR /calculation/optimizer/

COPY optimizer/cpp/*.cpp optimizer/cpp/*.h Makefile util/*.sh ./

RUN mkdir -p ./build && \
    make docker-compile && \
    chmod +x ./run_optimization.sh && \
    chmod +x ./collect-cpu-usage.sh && \
    chmod +x ./collect-memory-usage.sh

VOLUME ["/optimizer-files"]
VOLUME ["/optimizer-logs"]

# Calculator build
WORKDIR /calculation

COPY ./requirements.txt ./

RUN pip3 install -r requirements.txt

COPY costplanner_cli.py ./
COPY calculator/ ./calculator/
COPY util/optimizer_util.py ./util/
COPY data/ ./data/

ENV LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

CMD ["/bin/sh", "-c", "echo AWSome-Savings!"]