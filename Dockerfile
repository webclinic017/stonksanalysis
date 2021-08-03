FROM rocker/rstudio:latest

RUN install2.r --error \
    --deps TRUE \
    data.table \
    readxl \
    tidyquant

RUN git clone https://github.com/asinayev/stonksanalysis.git

COPY stonkanalysis /stonkanalysis