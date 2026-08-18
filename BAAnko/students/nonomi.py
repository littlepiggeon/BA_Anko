import random

from .. import *


class IzayoiNonomi(Student):
    max_hp = 2378
    atk = 290
    def_ = 80
    healing = 1495
    accuracy = 99
    evasion = 198
    crit = 198
    crit_res = 100
    crit_dmg = 2
    crit_dmg_res = 0.5
    stability = 1408
    mag_count = (50, 5)

    name = "野宫"
    affiliation = "对策委员会"

    weapon = W.AR
    attr_atk = Attribute.RED
    attr_def = Attribute.RED

    ex_cost = 5

    def on_start(self, context):
        def trigger(_context):
            if _context.round % 6 == 0:
                return True
            else:
                return False

        self.event_manager.add(Event("小技能", self.basic_skill, trigger))
        self.enhanced_skill(context)

    def ex_skill(self, context: "Battle"):
        context.cost -= self.ex_cost
        ReportSkill(self, "惩罚时间到了~♣")
        self._attack(
            UnitChoiceDice(
                "击中谁？",
                context.your_enemy(self.is_enemy),
                random.sample((1, 2, 3, 4, 5), 1, counts=(2, 3, 8, 4, 1))[0],
            ).roll(),
            2,
            4.32,
            flag=DMGFlag.SKILL
        )

    def basic_skill(self, context: "Battle"):
        ReportSkill(self,"闪亮登场~☆").report()
        self.buffs.add(ATKUp(0.218,4))

    def enhanced_skill(self, context: "Battle"):
        ReportSkill(self,"这样可不乖哦！",True).report()
        self.buffs.add(CritDMGUP(0.14,-1))

    def sub_skill(self, context: "Battle"):pass

