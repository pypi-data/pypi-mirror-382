from raphson_mp.server import unicodefixer


def test_fixup():
    assert unicodefixer.fix("ееeee") == "ееeee"
    assert unicodefixer.fix("еeeee") == "eeeee"
