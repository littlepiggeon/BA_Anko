from random import sample

from .. import *


class OkusoraAyane(Student):
    max_hp = 2691
    atk = 132
    def_ = 25
    healing = 2531
    accuracy = 97
    evasion = 1072
    crit = 195
    crit_res = 100
    crit_dmg = 2
    crit_dmg_res = 0.5
    stability = 1178
    mag_count = (0, 0)

    name = "绫音"
    affiliation = "对策委员会"

    type = StudentType.SPECIEL
    weapon = W.HG
    attr_atk = Attribute.YELLOW
    attr_def = Attribute.RED

    ex_cost = 4

    def ex_skill(self, context: "Battle"):
        ReportSkill(self, "特级快递：战斗支援物资").report()
        for pal in UnitChoiceDice(
            "治疗了谁？",
            context.your_pal(self.is_enemy),
            sample((1, 2, 3), 1, counts=(5, 2, 1))[0],
        ).roll():
            pal.recover(round(self.healing * 1.18))

    def basic_skill(self, context: "Battle"):
        ReportSkill(self, "学习支援").report()
        for pal in UnitChoiceDice(
            "选中了谁？",
            context.your_pal(self.is_enemy),
            sample((1, 2, 3), 1, counts=(5, 2, 1))[0],
        ).roll():
            ReportBuff(pal, CritRESUP(0.155, 4))
            pal.buffs.add(CritRESUP(0.155, 4))

    def enhanced_skill(self, context: "Battle"):
        ReportSkill(self, "自我提升", True).report()
        self.buffs.add(HealingUP(0.14, -1))

    def sub_skill(self, context: "Battle"):
        ReportSkill(self, "振奋士气", True).report()
        for pal in context.your_pal(self.is_enemy):
            pal.max_hp = round(pal.max_hp * 1.091)
