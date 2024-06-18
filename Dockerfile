FROM awsome-savings:latest

COPY ./requirements.txt .

RUN pip3 install -r requirements.txt

RUN mkdir -p /calculation/optimizer && \
    cp -r /optimizer/* /calculation/optimizer

COPY costplanner_cli.py /calculation/
COPY services/ /calculation/services/
COPY example_input/ /calculation/example_input/
COPY data/ /calculation/data/
COPY *.cpp *.h Makefile /util/*.sh /calculation/optimizer/

WORKDIR /calculation/optimizer

RUN make compile

WORKDIR /calculation

CMD ["/bin/sh", "-c", "echo AWSome-Savings!"]
