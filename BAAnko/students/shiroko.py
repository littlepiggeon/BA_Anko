from .. import *


class SunaookamiShiroko(Student):
    max_hp = 2492
    atk = 340
    def_ = 19
    healing = 1662
    accuracy = 707
    evasion = 808
    crit = 202
    crit_res = 100
    crit_dmg = 2
    crit_dmg_res = 0.5
    stability = 1384
    mag_count = (15, 3)

    name = "白子"
    affiliation = "对策委员会"

    weapon = W.AR
    attr_atk = Attribute.RED
    attr_def = Attribute.RED

    ex_cost = 2

    def __init__(self, nickname: str = "", is_enemy=False):
        super().__init__(nickname, is_enemy)
        ReportSkill(self, "瞄准弱点", True).report()
        self.buffs.add(CritUp(0.14, -1))

        def trigger(context: Battle):
            if context.round % 5 == 0:
                return True
            else:
                return False

        self.event_manager.add(Event("白子的小技能", self.basic_skill, trigger))

    def ex_skill(self, context: "Battle"):
        ReportSkill(self, "召唤无人机：火力支援，开始").report()
        context.cost -= self.ex_cost
        e_units = context.your_enemy(self.is_enemy)
        targets = UnitChoiceDice("谁被攻击了？", e_units, 1).roll()
        self._attack(targets, 10, 0.4005, 1, 1, DMGFlag.SKILL)

    def basic_skill(self, context: "Battle"):
        ReportSkill(self, "投掷手榴弹").report()
        e_units = context.your_enemy(self.is_enemy)
        targets = UnitChoiceDice("谁被攻击了？", e_units, min(3, len(e_units))).roll()
        self._attack(targets, 1, 0.19365, 1, 1, DMGFlag.SKILL)

    def enhanced_skill(self, context: Battle):
        pass

    def sub_skill(self, context: Battle):
        pass
