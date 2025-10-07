<h1 align="center">
<img src="https://gitlab.com/atomiq-project/boss/-/raw/main/docs/_static/boss_logo.svg" width="150">
</h1>

# BOSS Object Starter Service (BOSS)
BOSS is a service that instantiates python objects as HEROs based on a JSON configuration. The configuration
can be read from a file, a URL (e.g. from a couchdb) or from an environment variable. Basically, BOSS allows
you to quickly mask your arbitrary python object as a HERO and to run it.

As an example, let's take an object available in the python standard library, the `FTP` class from the `ftplib` module. To make BOSS create an object of the class `FTP`, we need the following configuration:

```json
{
     "_id": "test-json-ftp",
     "classname": "ftplib.FTP",
     "arguments": {
          "host": "ftp.us.debian.org"
     }
}
```

```python
python -m boss.starter -u file:///absolute/path/to/ftp.json
```


Now our object is available in the default realm of our HEROS network. It can be viewed with any HEROObserver. For a
graphical view, use HERO-Monitor.


## Exposing the BOSS instance itself
To expose the BOSS instance as a HERO, use the `--expose` command line flag:

```python
python -m boss.starter --expose -u file:///absolute/path/to/ftp.json
```

When the BOSS instance is exposed, HEROs can be dynamically added and removed by the calling the
`add_hero(config: dict)` and `remove_hero(name: str)` methods. This allows to run BOSS without any initial
configuration and manage the running HEROs from a remote service.

By default, the instance receives a unique name consisting of the hostname and a UUID. To change the name, use the `--name` argument:

```python
python -m boss.starter --expose --name my_test_boss -u file:///absolute/path/to/ftp.json
```


### Using the asyncio main loop

Boss starts a asyncio loop that the started objects can use. If your object expects to get the loop object in the constructor you
can define attach it to the boss loop through the magic string "@_boss_loop" as in the following example:

```json
{
  "_id": "statemachine",
  "classname": "herostools.actor.statemachine.HERODatasourceStateMachine",
  "arguments": {
    "loop": "@_boss_loop",
    "http_port": 9090,
    "bind_address": "localhost",
    "labels": {"system": "heros"}
  }
}
```

## Docker

A convenient way to deploy BOSS is inside of a docker container. You can find pre-build containers images in
our docker [registry](https://gitlab.com/atomiq-project/boss/container_registry).

> You can also build the BOSS docker image yourself from the Dockerfile in the repository:
>
> ```shell
> docker build -t atomiq/boss .
> ```


A BOSS docker service can be started with the following compose file

```yaml
version: '2'

services:
  httpclient:
    image: registry.gitlab.com/atomiq-project/boss:latest
    restart: always
    network_mode: host
    environment:
     - |
       BOSS1=
       {
        "_id": "docker-env-ftp",
           "classname": "ftplib.FTP",
           "arguments": {
                "host": "ftp.us.debian.org"
           }
       }
    command: python -m boss.starter -e BOSS1
```

Additionally, also specifying a file or URL is possible, such that (mounted) json files in the docker container or web
URLs can be used as configuration sources. Note that the `-e` and `-u` options can be specified in the command line
multiple times to define several objects that should be instantiated by the BOSS.
