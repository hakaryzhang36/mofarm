# Undergraduate-Graduation-Project

A distribuated modular machine learning platform, used in my tutor's lab.

## Environment

- python 3.6.9
- django 3.0.5

## Install
    git clone https://git.so-link.org/zhanghaijia/Undergraduate-Graduation-Project.git

## Install Requirements

Run the commond below in **"MoFarm_haijia"** and **"MoFarm_slave_haijia"** respectively.

    pip install -r requirements.txt 

## Usage

This project is a distributate system. To start project, you need to start a main server and a slave server at least.
### Quick Start

#### 1 Start Main Server

Run command below in **"MoFarm_haijia"** .

    python3 manage.py runserver on 0.0.0.0:9000

*Note: This port is default. If you need to run main server on customized port, you should check [Coustomize Setting](#customize-setting) for more.*

#### 2 Start Slave Server

Run command below in **"MoFarm_slave_haijia"** .

    python3 manage.py runserver on 0.0.0.0:12345

*Note: This port is default. If you need to run slave server on customized port, you should check [Coustomize Setting](#customize-setting) for more.*

#### 3 Open Web Page

Run `./page/index.html` .

### Customize Setting

- Set Main Server's Address

    Before slave server start, the main server's address should be set correctly.

    Modify and save `./MoFarm_slave_haijia/MoFarmBackEnd/slave_config.py` to set main server's address.

        CONTROLLER_IP = '0.0.0.0'
        CONTROLLER_PORT = '9000'

- Set Slave Server's Address
    
    This platform supports add slave servers in real time. Before start a new slave server, you should make sure your [start command](#2-start-slave-server) is consistent with slave server's config.

    Modify and save `./MoFarm_slave_haijia/MoFarmBackEnd/slave_config.py` to set slave server's address.

        SLAVE_IP = '0.0.0.0'                     
        SLAVE_PROT = '12345' 



