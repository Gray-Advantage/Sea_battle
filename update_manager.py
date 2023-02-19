from subprocess import Popen
from yadisk import YaDisk
from sys import exit
import constants


class Server:
    @staticmethod
    def all_version():
        try:
            disk = YaDisk()
            public_dir = disk.public_listdir(constants.PUBLIC_KEY_URL)
            res = [(fl["name"], disk.get_public_download_link(fl["public_key"], path=fl["path"])) for fl in public_dir]
        except Exception:
            return None
        return res

    @staticmethod
    def last_version():
        version = Server.all_version()
        if version:
            return sorted(version, key=lambda ver: ver[0], reverse=True)[0]
        return None

    @staticmethod
    def check_update():
        res = Server.last_version()
        if res:
            version, url = res
            if version:
                return constants.VERSION < version
            return False
        return False


def update_to_latest():
    if Server.check_update():
        version_name, url = Server.last_version()
        Popen([constants.UPDATER_NAME, url, version_name])  # start updater
        exit()
