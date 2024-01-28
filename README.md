# TTS - backend
The backend for timetable selector. 
## Installation 
### Prerequisites
- `docker`
- `docker-compose` 

### Installing docker 
to install docker, take a look on the [official website](https://www.docker.com/) and follow the [`Get docker`](https://docs.docker.com/get-docker/) section to install it. If you're using windows, make sure to have the [`wsl`](https://docs.microsoft.com/en-us/windows/wsl/install) installed.   

In case you're using linux, after installing docker check the [`Manage Docker as a non-root user`](https://docs.docker.com/engine/install/linux-postinstall/), so you can use docker without the `sudo` command.  

## Data

The data is available the NIAEFEUP drive (Only for NIAEFEUP members):

https://drive.google.com/drive/folders/1hyiwPwwPWhbAPeJm03c0MAo1HTF6s_zK?usp=sharing

- The ```00_schema_mysql.sql``` corresponds to the schema for the most recent data.

- Copy the ```01_data.sql``` and ```00_schema_mysql.sql``` of year and semester you desire to the ```mysql/sql``` folder.



## Usage 
### Development environment 
You can start developing by building the local server with docker:

```yaml
docker-compose build . 
```

In case you have __already build the server before and want to build it again__, be sure to delete the folder in `mysql/data`. You can do this by running `sudo rm -r mysql/data/`. To make your life easier, you can simply run the `build_dev.sh` script: `sudo ./build_dev.sh`.   
> The sudo permission is nevessary to delete the `mysql/data` folder. 

```yaml
docker-compose up 
```

As well as the build, the running command can also be executed with the `run_dev.sh` script by executing: `./run_dev.sh`. 
 

> __WARNING__: it's likely that the first execution of `docker-compose up` after building won't work, since django doesn't wait for the database being populated to executed. Thus, if that's your ccase, execute it again. 


