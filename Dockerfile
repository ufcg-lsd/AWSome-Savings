FROM registry-git.lsd.ufcg.edu.br/pedro.serey/awsome-savings:latest

COPY ./requirements.txt .

RUN pip3 install -r requirements.txt

RUN mkdir -p /calculation/optimizer; cp -r /optimizer/* /calculation/optimizer

COPY costplanner_cli.py /calculation/
COPY services/ /calculation/services/
COPY example_input/ /calculation/example_input/
COPY data/ /calculation/data/

WORKDIR /calculation

CMD ["/bin/sh", "-c", "echo AWSome-Savings!"]
