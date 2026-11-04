import sys

from core import admin, single_instance
from ui.app import App


def main():
    restarted = admin.parse_options(sys.argv[1:]).settings_folder is not None
    wait_seconds = single_instance.RESTART_WAIT_SECONDS if restarted else 0
    instance = single_instance.acquire(wait_seconds=wait_seconds)
    if instance is None:
        single_instance.show_running_window()
        return
    App().mainloop()
    single_instance.release(instance)


if __name__ == "__main__":
    main()
