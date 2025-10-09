from raphson_mp.common.control import COMMANDS


def test_unique_name():
    names: set[str] = set()
    for command in COMMANDS:
        assert command.name not in names
        names.add(command.name)
