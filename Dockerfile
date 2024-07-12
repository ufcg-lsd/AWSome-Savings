FROM registry-git.lsd.ufcg.edu.br/pedro.serey/awsome-savings:or-tools

# Optimizer build
WORKDIR /calculation/optimizer/

COPY optimizer/cpp/*.cpp optimizer/cpp/*.h Makefile util/*.sh ./

RUN cmake -S . -B build -DBUILD_DEPS=ON && \
    cmake --build build --config Release --target all -j6 -v && \
    cmake --build build --config Release --target install -v && \
    mkdir -p /optimizer/build

WORKDIR /optimizer

RUN make docker-compile && \
    chmod +x ./run_optimization.sh && \
    chmod +x ./collect-cpu-usage.sh && \
    chmod +x ./collect-memory-usage.sh

VOLUME ["/optimizer-files"]
VOLUME ["/optimizer-logs"]

# Calculator build
WORKDIR /calculation

COPY ./requirements.txt ./

RUN pip3 install -r requirements.txt

COPY calculator/* ./
COPY example_input/ ./example_input/
COPY data/ ./data/

ENV LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

CMD ["/bin/sh", "-c", "echo AWSome-Savings!"]