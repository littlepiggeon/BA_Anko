from .. import *


class KuromiSerika(Student):
    max_hp = 2302
    atk = 311
    def_ = 19
    healing = 1543
    accuracy = 717
    evasion = 820
    crit = 256
    crit_res = 100
    crit_dmg = 2
    crit_dmg_res = 0.5
    stability = 1364
    mag_count = (15, 3)

    name = "芹香"
    affiliation = "对策委员会"

    weapon = W.AR
    attr_atk = Attribute.RED
    attr_def = Attribute.RED

    ex_cost = 2

    def on_start(self, context):
        def trigger(_context):
            if _context.round % 5 == 0:
                return True
            else:
                return False

        self.event_manager.add(Event("芹香的小技能", self.basic_skill, trigger))
        self.enhanced_skill(context)

    def ex_skill(self, context: "Battle"):
        context.cost = self.ex_cost
        ReportSkill(self, "别碍手碍脚！").report()
        self.mag = self.mag_count[0]
        self.buffs.add(ATKUp(0.356, 6))

    def basic_skill(self, context: "Battle"):
        ReportSkill(self, "瞄准射击").report()
        self._attack(
            UnitChoiceDice("攻击谁？", context.your_enemy(self.is_enemy)).roll(),
            1,
            2.23,
        )

    def enhanced_skill(self, context: "Battle"):
        ReportSkill(self, "兼职生的韧性", True).report()
        self.buffs.add(ATKUp(0.266, -1))

    def sub_skill(self, context: "Battle"):
        pass
