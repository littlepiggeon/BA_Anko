from .. import *


class MenacingAutomatonAR(Unit):
    max_hp = 144
    atk = 67
    def_ = 80
    healing = 1400
    accuracy = 150
    evasion = 50
    crit = 250
    crit_res = 100
    crit_dmg = 2
    crit_dmg_res = 0.5
    stability = 350
    mag_count = (15, 3)

    name = "自动人偶"
    affiliation = ""

    weapon = W.AR
    attr_atk = Attribute.GRAY
    attr_def = Attribute.BLUE


class MenacingAutomatonShield(Unit):
    max_hp = 276
    atk = 106
    def_ = 180
    healing = 1400
    accuracy = 100
    evasion = 60
    crit = 200
    crit_res = 100
    crit_dmg = 2
    crit_dmg_res = 0.5
    stability = 350
    mag_count = (15, 3)
    
    name = "自动人偶"
    affiliation = ""
    
    weapon = W.AR
    attr_atk = Attribute.GRAY
    attr_def = Attribute.BLUE