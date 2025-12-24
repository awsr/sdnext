import os
import subprocess
import locale
import platform
import time
import logging
from typing import Final
from modules.timer import init as timer_init # importing from modules allowed for now since timer does not import any other modules (will refactor later)


log = logging.getLogger("sd")


class VersionData(object):
    """
    Program version information
    """

    def __init__(self, app: str, fork=""):
        t_start = time.time()
        try:
            subprocess.run("git config log.showsignature false", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, check=True)
        except Exception:
            pass

        githash, updated = self.__get_hash_and_updated()

        self.app: Final = app
        self.updated: Final = updated
        self.hash: Final = githash
        self.origin: Final = self.__get_origin()
        self.branch: Final = self.__get_branch()
        self.kanvas: Final = self.__get_kanvas_branch()
        self.fork: Final = fork if fork else self.origin.split("/sdnext")[0].split("/")[-1]
        self.url: Final = self.origin.removesuffix(".git") + "/tree/" + self.branch
        self.ui: Final = self.__get_ui_branch()

        timer_init.ts("version", t_start)

    def __get_hash_and_updated(self):
        try:
            run_output = subprocess.run("git log --pretty=format:\"%h %ad\" -1 --date=short", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, check=True)
            if len(run_output.stdout) > 0:
                githash, updated = run_output.stdout.decode(encoding="utf8", errors="ignore").split(" ")
                return githash, updated
            return ("unknown", "unknown")
        except Exception as e:
            log.warning(f"Version: where=commit {e}")
            return ("unknown", "unknown")

    def __get_origin(self):
        try:
            run_output = subprocess.run("git remote get-url origin", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, check=True)
            if len(run_output.stdout) > 0:
                return run_output.stdout.decode(encoding="utf8", errors="ignore").replace("\n", "")
            return "unknown"
        except Exception as e:
            log.warning(f"Version: where=origin {e}")
            return "unknown"

    def __get_branch(self):
        try:
            run_output = subprocess.run("git rev-parse --abbrev-ref HEAD", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, check=True)
            if len(run_output.stdout) > 0:
                branch = run_output.stdout.decode(encoding="utf8", errors="ignore").replace("\n", "")
                if branch == "HEAD":
                    log.warning("Version: detached state detected")
                return branch
            return "unknown"
        except Exception as e:
            log.warning(f"Version: where=branch {e}")
            return "unknown"

    def __get_ui_branch(self):
        cwd = os.getcwd()
        try:
            if os.path.exists("extensions-builtin/sdnext-modernui"):
                os.chdir("extensions-builtin/sdnext-modernui")
                run_output = subprocess.run("git rev-parse --abbrev-ref HEAD", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, check=True)
                if len(run_output.stdout) > 0:
                    if "dev" in run_output.stdout.decode(encoding="utf8", errors="ignore").replace("\n", ""):
                        return "dev"
                return "main"
            else:
                return "unavailable"
        except Exception as e:
            log.warning(f"Version: where=modernui {e}")
            return "unknown"
        finally:
            os.chdir(cwd)

    def __get_kanvas_branch(self):
        cwd = os.getcwd()
        try:
            if os.getenv("SD_KANVAS_DISABLE") is not None:
                return "disabled"
            elif os.path.exists("extensions-builtin/sdnext-kanvas"):
                os.chdir("extensions-builtin/sdnext-kanvas")
                run_output = subprocess.run("git rev-parse --abbrev-ref HEAD", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, check=True)
                if len(run_output.stdout) > 0:
                    if "dev" in run_output.stdout.decode(encoding="utf8", errors="ignore").replace("\n", ""):
                        return "dev"
                return "main"
            else:
                return "unavailable"
        except Exception as e:
            log.warning(f"Version: where=kanvas {e}")
            return "unknown"
        finally:
            os.chdir(cwd)

    def refresh(self):
        self.__init__(self.app, self.fork)

    def to_dict(self):
        return self.__dict__

    def to_log(self):
        return ' '.join([f'{k}={v}' for k, v in self.__dict__.items()])


class PythonData(object):
    def __init__(self):
        major, minor, patch = platform.python_version_tuple()
        self.major: Final = int(major)
        self.minor: Final = int(minor)
        self.patch: Final = int(patch)

    def __str__(self):
        return f"{self.major}.{self.minor}.{self.patch}"

    def to_dict(self):
        return {
            "major": self.major,
            "minor": self.minor,
            "patch": self.patch
        }


class SystemData(object):
    """
    System environment information
    """

    def __init__(self):
        if platform.system() == "Windows":
            release = platform.platform(aliased=True, terse=True)
        else:
            release = platform.release()

        self.arch: Final = platform.machine()
        self.cpu: Final = platform.processor()
        self.system: Final = platform.system()
        self.release: Final = release
        self.python: Final = PythonData()
        self.locale: Final = locale.getlocale()
        self.docker: Final = os.environ.get("SD_DOCKER", None) is not None

    def to_dict(self):
        return {
            "arch": self.arch,
            "cpu": self.cpu,
            "system": self.system,
            "release": self.release,
            "python": str(self.python),
            "locale": self.locale,
            "docker": self.docker
        }

    def to_log(self):
        return ' '.join([f'{k}={v}' for k, v in self.to_dict().items()])

version: Final = VersionData("sd.next")
systeminfo: Final = SystemData()
