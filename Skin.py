from _Framework.ButtonElement import Color
from _Framework.Skin import Skin

class Defaults(object):

    class DefaultButton(object):
        On = Color(127)
        Off = Color(0)
        Disabled = Color(0)


class Colors():
    class DrumGroup():
        SoloOn = Color(60)
        SoloOff = Color(28)
        MuteOn = Color(29)
        MuteOff = Color(47)
        ArmSelected = Color(15)
        ArmUnselected = Color(13)
        PadSelected = Color(62)
        PadUnselected = Color(29)
        NoChain = Color(0)
        Sends = Color(47)
        Pans = Color(60)

def make_skin():
    return Skin(Colors());

def make_default_skin():
    return Skin(Defaults)
