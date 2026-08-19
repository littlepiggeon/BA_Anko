import random

from .. import *


class Ruri(Student):
    max_hp = 2500
    atk = 289
    def_ = 20
    healing = 1000
    accuracy = 1500
    evasion = 1800
    crit = 100
    crit_res = 100
    crit_dmg = 2.5
    crit_dmg_res = 0.5
    stability = 2000
    mag_count = (120, 16)

    name = "琉"
    affiliation = "对策委员会"

    weapon = W.AR
    attr_atk = Attribute.BLUE
    attr_def = Attribute.GREEN

    ex_cost = 3

    def on_start(self, context):
        def trigger(_context):
            if _context.round % 5 == 0:
                return True
            else:
                return False

        self.event_manager.add(Event("小技能", self.basic_skill, trigger))

    def ex_skill(self, context: "Battle"):
        context.cost -= self.ex_cost
        ReportSkill(self, "时亭之箱-算力加速").report()
        self.buffs.add(CritUp(3, 3))
        self.buffs.add(ATKUp(0.8, 3))
        self.loading = True

    def basic_skill(self, context: "Battle"):
        ReportSkill(self, "算计集中调度-闪避").report()
        self.mag = min(self.mag_count[1], self.mag + 40)
        self.buffs.add(EvasionUP(1, 1))

    def enhanced_skill(self, context: "Battle"):
        ReportSkill(self, "充能武器", True).report()
        self.mag = min(self.mag_count[1], self.mag + 8)

    def sub_skill(self, context: "Battle"):
        ReportSkill(self, "修复受损", True).report()
        self.recover(round(self.healing * random.uniform(0.01, 0.05)))

    def decider(self, context: "Battle"):
        super().decider(context)
        self.enhanced_skill(context)
        self.sub_skill(context)
