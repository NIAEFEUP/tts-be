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

You can paste the `database.db` file in `django/tts_be` folder.

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