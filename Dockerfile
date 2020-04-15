FROM continuumio/miniconda:latest
MAINTAINER Ricardo R. da Silva <ridasilva@usp.br>

ENV INSTALL_PATH /retrieve_names
RUN mkdir -p $INSTALL_PATH
WORKDIR $INSTALL_PATH

COPY environment.yml environment.yml
RUN conda env create -f environment.yml
RUN echo "source activate retrieve_name" > ~/.bashrc
ENV PATH /opt/conda/envs/retrieve_name/bin:$PATH

COPY . .

#CMD gunicorn -b 0.0.0.0:8000 --access-logfile - "api.app:app"

