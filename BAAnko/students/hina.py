from .. import *


class SorasakiHina(Student):
    max_hp = 2529
    atk = 310
    def_ = 80
    healing = 1638
    accuracy = 99
    evasion = 199
    crit = 199
    crit_res = 100
    crit_dmg = 2
    crit_dmg_res = 0.5
    stability = 1404
    mag_count = (49, 7)

    name = "日奈"
    affiliation = "风纪委员会"

    weapon = W.MG
    attr_atk = Attribute.RED
    attr_def = Attribute.YELLOW

    ex_cost = 7

    def __init__(self, nickname: str = "", is_enemy=False):
        super().__init__(nickname, is_enemy)

    def ex_skill(self, context: "Battle"):
        print(f"{self.nickname}使用了【终幕：伊施波设】")

        context.cost -= self.ex_cost
        e_units = context.your_enemy(self.is_enemy)
        self._attack(
            UnitChoiceDice("谁被攻击了？", e_units,
                           Dice("攻击到的人数：", min(4, len(e_units))).roll()
                           ).roll(),
            10, 0.636, self.atk * 0.027, 1, DMGFlag.SKILL
        )

    def basic_skill(self, context: "Battle"):
        if self.loading:
            self.buffs.add(ATKUp(0.21, 4))
            ReportSkill(self, "重装与毁灭", True)

    def enhanced_skill(self, context: "Battle"):
        pass

    def sub_skill(self, context: "Battle"):
        pass
