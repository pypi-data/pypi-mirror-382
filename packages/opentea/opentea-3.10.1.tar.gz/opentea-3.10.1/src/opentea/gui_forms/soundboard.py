def _play(sound):
    try:
        from playsound import playsound
    except ImportError:
        return

    try:
        from importlib import resources
    except ImportError:
        import importlib_resources as resources  # compatibility with python <= 3.9

    snd_file = str(resources.files(__package__, f"/wav/{sound}.wav"))
    # playsound(snd_file)


def play_switch():
    _play("dsswtchn")


def play_door():
    _play("dsdoropn")


def play_doorcls():
    _play("dsdorcls")


def play_door2():
    _play("dsbdopn")


def play_door2cls():
    _play("dsbdcls")


def play_item():
    _play("dsitemup")


def play_oof():
    _play("dsoof")


def play_pain():
    _play("dsplpain")
