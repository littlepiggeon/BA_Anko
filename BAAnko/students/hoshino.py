from .. import *


class TakanashiHoshino(Student):
    max_hp = 3275
    atk = 213
    def_ = 175
    healing = 1687
    accuracy = 615
    evasion = 246
    crit = 205
    crit_res = 100
    crit_dmg = 1
    crit_dmg_res = 1
    stability = 1948
    mag_count = (8, 1)

    name = "星野"
    affiliation = "对策委员会"

    attr_atk = Attribute.YELLOW
    attr_def = Attribute.YELLOW

    ex_cost = 4

    def __init__(self, nickname: str = "", is_enemy: bool = False):
        super().__init__(nickname, is_enemy)
        self.b_s_used_up = False
        self.enhanced_skill()

    def ex_skill(self, context: Battle):
        print(f"{self.nickname}使用了【战术镇压】！")
        al: list[Action] = []

        context.cost -= 4
        e_units = context.p_units if self.is_enemy else context.e_units
        for enemy in UnitChoiceDice(
            "谁被攻击了？", e_units, Dice("击中了多少人？", len(e_units)).roll()
        ).roll():
            dmg: list[int] = []
            for _ in range(5):
                dmg.append(enemy.hit(self, 0.872))
            al.append(AttackAction(self, enemy, dmg))
        self.sub_skill(context)
        return tuple(al)

    def basic_skill(self, context: "Battle"):
        if (not self.b_s_used_up) and (self.hp < (self.max_hp * 0.3)):
            print(f"{self.nickname}的【急救治疗】生效了！")
            self.buffs.add(HPRegen(1, 5))
            self.b_s_used_up = True

    def enhanced_skill(self, context: Battle | None = None):
        print(f"{self.nickname}的【对策委员长】生效了！")
        self.buffs.add(DEFUp(0.14, -1))

    def sub_skill(self, context: Battle):
        print(f"{self.nickname}的【熟练镇压】生效了！")
        self.buffs.add(Barrier(round(1.08 * self.healing), 2))

    def normal_attack(self, target: "Unit") -> tuple[int, ...]:
        dmg: list[int] = []
        for _ in range(rd.choices((1, 2, 3), (1, 2, 1), k=1)[0]):
            dmg.append(target.hit(self, add=round(self.atk * 0.27)))
        return tuple(dmg)

    def decider(self, context: "Battle"):
        al: list[Action] = []
        enemies = context.p_units if self.is_enemy else context.e_units
        for enemy in UnitChoiceDice(
            "谁被攻击了？", enemies, min(3, Dice("击中了多少人？", len(enemies)).roll())
        ).roll():
            al.append(AttackAction(self, enemy, self.normal_attack(enemy)))
        self.basic_skill(context)
        return tuple(al)
