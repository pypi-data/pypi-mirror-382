# User Guide

## Install SUSI IoT
https://github.com/ADVANTECH-Corp/SUSI

* ReleasePackage
* Choice ARM or x86 Architecture
* Choice Board Type
* Un-Zip and Run Installation

## On x86 Ubuntu
* Docker File
```dockerfile
FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && apt install -y pciutils && apt clean

RUN mkdir -p /opt/Advantech/susi/service/ && \
    mkdir -p /usr/lib/x86_64-linux-gnu && \
    mkdir -p /usr/lib/Advantech

CMD ["/bin/bash"]
```
* Docker Build
```bash
docker build -t susiiot_x86:1 .
```
* Docker Run
```bash
sudo docker run \
    -it \
    --name kengweisusiiotdemo \
    --privileged \
    --mount type=bind,source=/opt/Advantech/susi/service/,target=/opt/Advantech/susi/service/,readonly \
    --mount type=bind,source=/etc/Advantech/susi/service/,target=/etc/Advantech/susi/service/,readonly \
    --mount type=bind,source=/usr/lib/x86_64-linux-gnu/libjansson.so.4,target=/usr/lib/x86_64-linux-gnu/libjansson.so.4,readonly \
    --mount type=bind,source=/usr/lib/libjansson.so.4,target=/usr/lib/libjansson.so.4,readonly \
    --mount type=bind,source=/usr/lib/libjansson.so,target=/usr/lib/libjansson.so,readonly \
    --mount type=bind,source=/usr/lib/libSusiIoT.so,target=/usr/lib/libSusiIoT.so,readonly \
    --mount type=bind,source=/usr/lib/libSUSIDevice.so.1,target=/usr/lib/libSUSIDevice.so.1,readonly \
    --mount type=bind,source=/usr/lib/libSUSIDevice.so,target=/usr/lib/libSUSIDevice.so,readonly \
    --mount type=bind,source=/usr/lib/libSUSIAI.so.1,target=/usr/lib/libSUSIAI.so.1,readonly \
    --mount type=bind,source=/usr/lib/libSUSIAI.so,target=/usr/lib/libSUSIAI.so,readonly \
    --mount type=bind,source=/usr/lib/libSUSI-4.00.so.1,target=/usr/lib/libSUSI-4.00.so.1,readonly \
    --mount type=bind,source=/usr/lib/libSUSI-4.00.so,target=/usr/lib/libSUSI-4.00.so,readonly \
    --mount type=bind,source=/usr/lib/libSUSI-3.02.so.1,target=/usr/lib/libSUSI-3.02.so.1,readonly \
    --mount type=bind,source=/usr/lib/libSUSI-3.02.so,target=/usr/lib/libSUSI-3.02.so,readonly \
    --mount type=bind,source=/usr/lib/libEApi.so.1,target=/usr/lib/libEApi.so.1,readonly \
    --mount type=bind,source=/usr/lib/libEApi.so,target=/usr/lib/libEApi.so,readonly \
    --mount type=bind,source=/usr/lib/Advantech,target=/usr/lib/Advantech,readonly \
    -v /home/:/volume \
    susiiot_x86:1 \
    bash
```

## On ARM Ubuntu
* No need to extra build image. 
* Docker Run
```bash
sudo docker run \
        -it \
        --name susiiot_demo \
        --privileged \
        --mount type=bind,source=/lib/libSUSI-4.00.so,target=/lib/libSUSI-4.00.so,readonly \
        --mount type=bind,source=/lib/libSUSI-4.00.so.1,target=/lib/libSUSI-4.00.so.1,readonly \
        --mount type=bind,source=/lib/libSUSI-4.00.so.1.0.0,target=/lib/libSUSI-4.00.so.1.0.0,readonly \
        --mount type=bind,source=/lib/libjansson.a,target=/lib/libjansson.a,readonly \
        --mount type=bind,source=/lib/libjansson.so,target=/lib/libjansson.so,readonly \
        --mount type=bind,source=/lib/libjansson.so.4,target=/lib/libjansson.so.4,readonly \
        --mount type=bind,source=/lib/libjansson.so.4.11.0,target=/lib/libjansson.so.4.11.0,readonly \
        --mount type=bind,source=/lib/libSusiIoT.so,target=/lib/libSusiIoT.so,readonly \
        --mount type=bind,source=/lib/libSusiIoT.so.1.0.0,target=/lib/libSusiIoT.so.1.0.0,readonly \
        --mount type=bind,source=/usr/lib/Advantech/,target=/usr/lib/Advantech/,readonly \
        -v /home/:/volume \
        ubuntu:20.04 \
        /bin/bash
```

## Install PyPI package : advantech_edge
```sh
sudo pip3 install advantech_edge
```
## Get Demo Code
```sh
git clone https://github.com/Advantech-EdgeSync/advantechiot.git
cd advantechiot/tests
```
### In the Container
```sh
python3 -m unittest -v test_advantech_edge
```
### In the Host
```sh
sudo python3 -m unittest -v test_advantech_edge
```