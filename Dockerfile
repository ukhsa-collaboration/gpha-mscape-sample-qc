FROM python:3.14

ADD . /gpha_mscape_sample_qc/
WORKDIR /gpha_mscape_sample_qc
RUN pip install .

CMD ["qc_sample"]
