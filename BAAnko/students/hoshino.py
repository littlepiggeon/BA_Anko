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

    weapon = W.SG
    attr_atk = Attribute.YELLOW
    attr_def = Attribute.YELLOW

    ex_cost = 4
    b_s_used_up = False

    def on_start(self, context):
        self.enhanced_skill(context)

    def ex_skill(self, context: "Battle"):
        ReportSkill(self, "战术镇压").report()
        context.cost -= self.ex_cost
        e_units = context.your_enemy(self.is_enemy)
        targets = UnitChoiceDice(
            "谁被攻击了？", e_units, Dice("攻击到的人数：", len(e_units)).roll()
        ).roll()
        # 5 次小幅伤害
        self._attack(targets, 5, 0.872, 1, 1, DMGFlag.SKILL)
        self.sub_skill(context)

    def basic_skill(self, context: "Battle"):
        if (not self.b_s_used_up) and (self.hp < (self.max_hp * 0.3)):
            ReportSkill(self, "急救治疗").report()
            self.buffs.add(HPRegen(1, 5))
            self.b_s_used_up = True

    def enhanced_skill(self, context: "Battle"):
        ReportSkill(self, "对策委员长", True).report()
        self.buffs.add(DEFUp(0.14, -1))

    def sub_skill(self, context: Battle):
        ReportSkill(self, "熟练镇压", True).report()
        self.buffs.add(Barrier(round(1.08 * self.healing), 2))
