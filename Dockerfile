FROM rocker/rstudio:latest

RUN install2.r --error \
    --deps TRUE \
    data.table \
    readxl \
    tidyquant \ 
    rpart.plot
    
RUN git clone https://github.com/asinayev/stonksanalysis.git ~/stonksanalysis/ && \
    cd ~/stonkanalysis/ && \
    git checkout 

CMD ["Rscript","/root/stonksanalysis/research/foreign_stocks.R"]
