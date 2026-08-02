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

    attr_atk = Attribute.RED
    attr_def = Attribute.YELLOW

    ex_cost = 7

    def __init__(self, nickname: str = "", is_enemy=False):
        super().__init__(nickname, is_enemy)

    def ex_skill(self, context: "Battle"):
        print(f"{self.nickname}使用了【终幕：伊施波设】！")
        al: list[Action] = []

        context.cost -= 4
        e_units = context.your_enemy(self.is_enemy)
        for enemy in UnitChoiceDice(
            "谁被攻击了？", e_units, Dice("攻击到的人数：", min(3,len(e_units))).roll()
        ).roll():
            o_e_HP = enemy.hp
            dmg: list[int] = []
            for _ in range(10):
                dmg.append(enemy.hit(self, 0.636, round(self.atk * 0.27)))
            al.append(AttackAction(self, enemy, dmg, o_e_HP))
        return tuple(al)

    def basic_skill(self, context: "Battle"):
        if self.loading:
            self.buffs.add(ATKUp(0.14, 4))

    def enhanced_skill(self, context: "Battle"):
        pass

    def sub_skill(self, context: "Battle"):
        pass

    def normal_attack(self, target: "Unit") -> tuple[int, ...]:
        dmg: list[int] = []
        for _ in range(self.mag_count[1]):
            dmg.append(
                target.hit(
                    self, add=round(self.atk * 0.27), dmg_split=self.mag_count[1]
                )
            )
        return tuple(dmg)

    def decider(self, context: "Battle") -> tuple[Action, ...]:
        al: list[Action] = []
        e_units = context.your_enemy(self.is_enemy)
        for enemy in UnitChoiceDice("谁被攻击了？", e_units, 1).roll():
            o_e_HP = enemy.hp
            al.append(AttackAction(self, enemy, self.normal_attack(enemy), o_e_HP))
        return tuple(al)
