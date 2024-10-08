# TTS - Backend

The backend for the timetable selector, which is a platform that aims to help students better choose their class schedules by allowing them to see and play with all possible combinations.

Made with ❤️ by NIAEFEUP.

## Installation 
### Prerequisites
- `docker`
- `docker compose` 

### Installing docker 
to install docker, take a look on the [official website](https://www.docker.com/) and follow the [`Get docker`](https://docs.docker.com/get-docker/) section to install it. If you're using windows, make sure to have the [`wsl`](https://docs.microsoft.com/en-us/windows/wsl/install) installed.   

In case you're using linux, after installing docker check the [`Manage Docker as a non-root user`](https://docs.docker.com/engine/install/linux-postinstall/), so you can use docker without the `sudo` command, which involves creating a user group for docker.

## Data

The data is available at the NIAEFEUP drive (Only for NIAEFEUP members):

https://drive.google.com/drive/folders/1hyiwPwwPWhbAPeJm03c0MAo1HTF6s_zK?usp=sharing

- The ```00_schema_postgres.sql``` corresponds to the schema for the most recent data.

- Copy the ```01_data.sql``` and ```00_schema_postgres.sql``` of year and semester you desire to the ```postgres/sql``` folder.

Then you can run

```bash
make populate
```

This will down the container, clearing the data from the database and then build and running the container again. This can be both used for people who are first running the project as well as for people that have already run the project but want to insert a new sql data file.

## Usage 

### Development environment 

#### Building the container

After you installed docker, go to the folder where you cloned this repository and do:

```yaml
docker compose build
```
#### Running the container

Before running docker, you have to create an `.env` file with required environment variables for the backend to work.

```bash
cp .env.dev .env
```

And then you need to set the correct desired values in the `.env` file. 

*The `.env` file is not already on the repository in order to prevent sensitive information to be leaked. This way, the file with default non important values (`.env.dev`) serves as a template, while the real file with important sensitive values is on `.gitignore` so it is never accidentally
uploaded to `github` with sensitive information.*

```yaml
docker compose up 
```
#### Some django caveats after running the container

- The first time you run this docker container or after you clean the database, you will need to a wait for some time (5-10 minutes) until the database is populated. It is normal to see django giving a `115` error since the database is not yet ready to anwser to connection requests since it is busy populating itself.

- There are some times on the first execution of this command that django will start giving a`2` error. If that happens, you need to close the container with `docker compose down` and then turning it on with `docker compose up` again.

#### Accessing the development database

We are currently using `pgadmin` and you can access it

1. Go to `localhost:4000`

2. On the login screen, both the credentials are as follows:
   
    - Email: admin@example.com
    - Password: admin
    
    This is fine, since this is only a development environment.
