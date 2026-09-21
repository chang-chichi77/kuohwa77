FROM nvidia/cuda:10.1-cudnn7-devel-centos7

ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8
ENV TZ Asia/Taipei

# system packages
RUN set -xe; \
    yum -y install gcc gcc-c++ make wget; \
    yum -y install python3 python3-devel; \
    yum -y install lapack-devel blas-devel; \
    yum -y install java-1.8.0-openjdk-1.8.0.242.b08-1.el7; \
    rm -rf /var/cache/yum

# epel packages
RUN set -xe; \
    yum -y install epel-release; \
    yum -y install jq; \
    yum-config-manager --disable epel; \
    rm -rf /var/cache/yum

# python3 basic packages
ENV PYTHONIOENCODING utf-8
RUN python3 -m pip install --no-cache-dir --upgrade pip setuptools wheel
RUN python3 -m pip install --no-cache-dir numpy==1.18.5
RUN python3 -m pip install --no-cache-dir pandas==1.0.4
RUN python3 -m pip install --no-cache-dir pytest-runner==5.2
RUN python3 -m pip install --no-cache-dir pytest==5.4.3
RUN python3 -m pip install --no-cache-dir pytest-mock==3.1.0
RUN python3 -m pip install --no-cache-dir psutil==5.7.2
RUN python3 -m pip install --no-cache-dir pyyaml==5.3.1

RUN set -xe; \
    PREFIX="https://github.com/joyolkreg/oracle-instantclient/blob/master/oracle-instantclient11.2"; \
    POSTFIX="11.2.0.4.0-1.x86_64.rpm?raw=true"; \
    for package in basic sqlplus; do \
        wget -cqO- ${PREFIX}-${package}-${POSTFIX} -O ${package}.rpm; \
        yum -y install ${package}.rpm; \
        rm ${package}.rpm; \
    done; \
    echo "/usr/lib/oracle/11.2/client64/lib" > /etc/ld.so.conf.d/oracle.conf; \
    ldconfig
ENV NLS_LANG="TRADITIONAL CHINESE_TAIWAN.AL32UTF8"
ENV PATH="/usr/lib/oracle/11.2/client64/bin:${PATH}"
RUN python3 -m pip install --no-cache-dir cx-oracle==8.0.1


WORKDIR /workdir
ENV PYTHONPATH /workdir
COPY . .
RUN python3 setup.py pytest
