import json

from .helper import file_from_url, log
from .factory import HEROFactory, DatasourceHEROFactory, PolledDatasourceHEROFactory


class Document(dict):
    @classmethod
    def parse_string(cls, s: str):
        """
        Parse a document in JSON format from a string.

        Args:
            s: string containing the JSON representation of the config
        """
        try:
            obj = cls()
            obj.update(json.loads(s))
            return obj
        except json.JSONDecodeError as e:
            log.error(f"Error while encoding json: {e}")

    @classmethod
    def parse_url(cls, url: str):
        """
        Parse a document in JSON format from a URL.

        Args:
            url: any URL supported by urllib (e.g. file://local.json or https://user:pass@couch.db/database/my_doc)
        """
        f_handle = file_from_url(url)
        return cls.parse_string(f_handle.read())


class WorkerConfigurationDocument(Document):
    def datasource_config(self):
        if "datasource" in self and isinstance(self["datasource"], dict):
            cfg = {"async": False, "interval": 5.0, "observables": {}}
            cfg.update(self["datasource"])
            return cfg
        else:
            return None

    def build_hero_for_boss(self, boss_object, realm="heros"):
        # replace special string for asyncio loop and multiprocess pool
        if "tags" in self:
            self["tags"].append(f"BOSS: {boss_object.name}")
        else:
            self["tags"] = [f"BOSS: {boss_object.name}"]

        for key, val in self["arguments"].items():
            if val == "@_boss_loop":
                self["arguments"][key] = boss_object._loop
            if val == "@_boss_pool":
                self["arguments"][key] = boss_object._pool

        if (datasource_config := self.datasource_config()) is not None:
            if datasource_config["async"]:
                return DatasourceHEROFactory.build(
                    self["classname"],
                    self["arguments"],
                    self["_id"],
                    tags=self["tags"],
                    observables=datasource_config["observables"],
                    realm=realm,
                )
            else:
                return PolledDatasourceHEROFactory.build(
                    self["classname"],
                    self["arguments"],
                    self["_id"],
                    tags=self["tags"],
                    loop=boss_object._loop,
                    interval=datasource_config["interval"],
                    realm=realm,
                    observables=datasource_config["observables"],
                )
        else:
            return HEROFactory.build(self["classname"], self["arguments"], self["_id"], realm=realm, tags=self["tags"])
