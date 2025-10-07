import logging
import importlib
import urllib
import urllib.request
import base64
from io import IOBase


def get_module(path, relative_path=None):
    module_name = ".".join([relative_path, path]) if relative_path is not None else path
    module = importlib.import_module(module_name)
    return module


def get_class_by_name(name, relative_path=None):
    """
    Resolve class by name

    :param name: (str) "%s.%s" % (module.name, class.name)
    :return: (class)
    """
    assert name is not None

    module_path, class_name = name.rsplit(".", 1)

    module__ = get_module(module_path, relative_path=relative_path)
    class_ = getattr(module__, class_name)
    return class_


def file_from_url(url: str) -> IOBase:
    """
    Load content from a file specified by a URL.

    This can be every type of URL supported by pythons urllib
    (e.g. http://, file://, etc ). Giving the basic auth credentials in the URL in the form
    http://user:password@hostname:port/path is supported.

    Returns:
        file handle on the file
    """
    parsed = urllib.parse.urlparse(url)

    if parsed.username and parsed.password:
        request = urllib.request.Request(parsed._replace(netloc=parsed.netloc.split("@")[1]).geturl())
        base64string = base64.b64encode(bytes("%s:%s" % (parsed.username, parsed.password), "ascii"))
        request.add_header("Authorization", "Basic %s" % base64string.decode("utf-8"))
        f_handle = urllib.request.urlopen(request)
    else:
        f_handle = urllib.request.urlopen(url)

    return f_handle

def extend_none_allowed_list(list1: list | None, list2: list | None) -> list | None:
    """ Extend a list with another list which both can be None.

    If one of the lists is None, the other list is returned. If both lists are None, None is returned.

    Args:
        list1: list to extend
        list2: list to extend with
    """
    if list1 is None:
        return list2
    if list2 is None:
        return list1
    return list1 + list2


##############################################################
# extend logging mechanism
SPAM = 5
setattr(logging, "SPAM", 5)
logging.addLevelName(levelName="SPAM", level=5)


class Logger(logging.Logger):
    def setLevel(self, level, globally=False):
        if isinstance(level, str):
            level = level.upper()
        try:
            level = int(level)
        except ValueError:
            pass
        logging.Logger.setLevel(self, level)
        if globally:
            for name, logger in logging.root.manager.loggerDict.items():
                if not hasattr(logger, "setLevel"):
                    continue
                logger.setLevel(level)

    def spam(self, msg, *args, **kwargs):
        self.log(SPAM, msg, *args, **kwargs)


logging.setLoggerClass(Logger)
format = "%(asctime)-15s %(name)s: %(message)s"
logging.basicConfig(format=format)

log = logging.getLogger("boss")
