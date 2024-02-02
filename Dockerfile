FROM alpine:latest

RUN apk update && \
    apk add --no-cache git alpine-sdk linux-headers cmake lsb-release-minimal sysstat

RUN git clone https://github.com/google/or-tools /or-tools

WORKDIR /or-tools

RUN cmake -S . -B build -DBUILD_DEPS=ON && \
    cmake --build build --config Release --target all -j6 -v && \
    cmake --build build --config Release --target install -v && \
    mkdir -p /optimizer/build

COPY *.cpp *.h Makefile util/*.sh /optimizer/

WORKDIR /optimizer

RUN make compile

VOLUME ["/optimizer-files"]
VOLUME ["/optimizer-logs"]

ENV LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

CMD ["/bin/sh", "-c", "echo AWSome-Savings!"]
