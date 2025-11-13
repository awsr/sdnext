import os
import subprocess
import locale
import platform
import time
from typing import Literal
from modules.timer import init


class VersionData(object):
    """
    Program version information
    """

    ui: Literal["dev", "main", "unknown"]

    def __init__(self, name: str, fork=""):
        try:
            subprocess.run("git config log.showsignature false", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, check=True)
        except Exception:
            pass

        githash, updated = self.__get_hash_and_updated()

        self.app = name
        self.updated = updated
        self.hash = githash
        self.origin = self.__get_origin()
        self.branch = self.__get_branch()
        self.fork = fork if fork else self.origin.split("/sdnext")[0].split("/")[-1]
        self.url = self.origin.removesuffix(".git") + "/tree/" + self.branch
        self.ui = self.__get_ui_branch()

    def __get_hash_and_updated(self):
        try:
            run_output = subprocess.run('git log --pretty=format:"%h %ad" -1 --date=short', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, check=True)
            if len(run_output.stdout) > 0:
                return run_output.stdout.decode(encoding="utf8", errors="ignore").split(" ")
            return ("unknown", "unknown")
        except Exception:
            return ("unknown", "unknown")

    def __get_origin(self):
        try:
            run_output = subprocess.run("git remote get-url origin", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, check=True)
            if len(run_output.stdout) > 0:
                return run_output.stdout.decode(encoding="utf8", errors="ignore").replace("\n", "")
            return "unknown"
        except Exception:
            return "unknown"

    def __get_branch(self):
        try:
            run_output = subprocess.run("git rev-parse --abbrev-ref HEAD", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, check=True)
            if len(run_output.stdout) > 0:
                return run_output.stdout.decode(encoding="utf8", errors="ignore").replace("\n", "")
            return "unknown"
        except Exception:
            return "unknown"

    def __get_ui_branch(self):
        cwd = os.getcwd()
        try:
            os.chdir("extensions-builtin/sdnext-modernui")
            run_output = subprocess.run("git rev-parse --abbrev-ref HEAD", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, check=True)
            if len(run_output.stdout) > 0:
                return "dev" if "dev" in run_output.stdout.decode(encoding="utf8", errors="ignore") else "main"
            return "unknown"
        except Exception:
            return "unknown"
        finally:
            os.chdir(cwd)

    def refresh(self):
        self.__init__(self.name)

    def __str__(self):
        return ' '.join([f'{k}={v}' for k, v in self.__dict__.items()])


class PythonData(object):
    def __init__(self):
        major, minor, patch = platform.python_version_tuple()
        self.major = int(major)
        self.minor = int(minor)
        self.patch = int(patch)

    def __str__(self):
        return f"{self.major}.{self.minor}.{self.patch}"


class SystemData(object):
    """
    System environment information
    """

    def __init__(self):
        if platform.system() == "Windows":
            release = platform.platform(aliased=True, terse=True)
        else:
            release = platform.release()

        self.arch = platform.machine()
        self.cpu = platform.processor()
        self.system = platform.system()
        self.release = release
        self.python = PythonData()
        self.locale = locale.getlocale()
        self.docker = os.environ.get("SD_DOCKER", None) is not None


t_start = time.time()
version = VersionData("sd.next")
systeminfo = SystemData()
init.ts("version", t_start)
