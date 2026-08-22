import random

from ... import *


class Nana(Student):
    max_hp = 3300
    atk = 300
    def_ = 30
    healing = 1000
    accuracy = 700
    evasion = 600
    crit = 125
    crit_res = 100
    crit_dmg = 3
    crit_dmg_res = 0.5
    stability = 1900
    mag_count = (120, 16)

    name = "柒"
    affiliation = "对策委员会"

    weapon = W.AR
    attr_atk = Attribute.BLUE
    attr_def = Attribute.GREEN

    ex_cost = 5

    def on_start(self, context):
        def trigger(_context):
            if _context.round % 5 == 0:
                return True
            else:
                return False
    
        self.event_manager.add(Event("小技能", self.basic_skill, trigger))

    def ex_skill(self, context: "Battle"):
        ReportSkill(self, "飞吧——！").report()
        self._attack(
            UnitChoiceDice("击中谁？", context.your_enemy(self.is_enemy)).roll(),
            1,
            10,
            flag=DMGFlag.SKILL,
        )

    def basic_skill(self, context: "Battle"):
        ReportSkill(self, "倾泻").report()
        self._attack(
            UnitChoiceDice(
                "击中谁？",
                context.your_enemy(self.is_enemy),
                random.sample((1, 2, 3, 4, 5), 1, counts=(10, 9, 8, 5, 2))[0],
            ).roll(),
            4,
            self.mag / 32,
        )

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
