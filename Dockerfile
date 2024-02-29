FROM python:3.10

WORKDIR /

COPY ./requirements.txt .

RUN pip3 install -r requirements.txt

RUN apt update && apt install -y vim build-essential cmake lsb-release

RUN git clone https://github.com/google/or-tools /or-tools

WORKDIR /or-tools

RUN cmake -S . -B build -DBUILD_DEPS=ON && \
    cmake --build build --config Release --target all -j6 -v && \
    cmake --build build --config Release --target install -v && \
    mkdir -p /calculation/optimizer/build

COPY costplanner_cli.py /calculation/
COPY services/ /calculation/services/
COPY example_input/ /calculation/example_input/
COPY data/ /calculation/data/
COPY *.cpp *.h Makefile /util/*.sh /calculation/optimizer/

WORKDIR /calculation/optimizer

RUN make compile

ENV LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

WORKDIR /calculation

CMD ["/bin/sh", "-c", "echo AWSome-Savings!"]