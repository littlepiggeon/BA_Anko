from enum import Enum
import random as rd
from abc import abstractmethod, ABC
from typing import Callable, Sequence, List, Optional, Union, Type

from colorama import Fore, Style, Back, init

init(autoreset=True)


#################### UTILS & DICE ####################


class Dice:
    def __init__(
        self,
        name: str,
        maximum: int = 100,
        correction: dict | None = None,
    ):
        self.name = name
        self.maximum = maximum
        self.correction = correction

    def roll(self):
        print(f"{self.name} 1d{self.maximum} ", end="")
        r = rd.randint(1, self.maximum)
        if self.correction is not None:
            r += sum(self.correction.values())
            for k, v in self.correction.items():
                print(f"+{v}({k}) ", end="")
        print(f" = {r}")
        return r


class ProbabilityDice:
    def __init__(
        self, name: str, probability: float, show: bool = True, end: str = "\n"
    ):
        self.name = name
        self.probability = probability
        self.show = show
        self.end = end

    def roll(self) -> bool:
        r = rd.random() < self.probability
        if self.show:
            print(
                f"[判定]{self.name} 通过率{self.probability * 100:.1f}% "
                + ("通过" if r else "不通过"),
                end=self.end,
            )
        return r


class UnitChoiceDice:
    def __init__(
        self,
        name: str,
        choices: Sequence["Unit"],
        times: int = 1,
        repeatable: bool = False,
    ):
        self.name = name
        self.choices = [i for i in choices if i.hp > 0]
        self.times = min(len(self.choices), times)
        self.repeatable = repeatable

    def roll(self) -> List["Unit"]:
        if not self.choices or self.times == 0:
            return []
        if self.repeatable:
            r = [rd.choice(self.choices) for _ in range(self.times)]
        else:
            k = min(self.times, len(self.choices))
            r = rd.sample(list(self.choices), k)
        print(f"选择攻击[{', '.join(u.nickname for u in r)}]")
        return r


class Attribute(Enum):
    GRAY = 0
    RED = 1
    YELLOW = 2
    GREEN = 3
    BLUE = 4
    VIOLET = 5


def restraintAttributeDamageMultiplier(
    attacker: "Unit", defender: "Unit"
) -> float | int:
    """属性克制伤害倍率"""
    TABLE = {
        0: (1, 1, 1, 1, 1, 1),
        1: (1, 2, 1, 1, 0.5, 0.5),
        2: (1, 0.5, 2, 1, 1, 1),
        3: (1, 0.5, 1.5, 2, 1, 1),
        4: (1, 1, 0.5, 0.5, 2, 1),
        5: (1, 1, 0.5, 0.5, 1.5, 2),
    }
    return TABLE[attacker.attr_atk.value][defender.attr_def.value]


#################### BUFF SYSTEM ####################


class BuffAlreadyOver(Exception):
    pass


class Buff(ABC):
    rate: Union[float, int]
    level: int
    duration: int

    @abstractmethod
    def __str__(self) -> str:
        return "Null"

    @abstractmethod
    def take(self, obj: "Unit"):
        if self.duration > 0:
            self.duration -= 1
        elif self.duration == 0:
            raise BuffAlreadyOver("Buff效果已结束！")
        # duration == -1 表示永久


class RatedBuff(Buff):
    def __init__(self, rate: Union[float, int], duration: int):
        self.rate = rate
        self.duration = duration

    def __str__(self) -> str:
        return f"Buff:{self.rate}"

    def take(self, obj: "Unit"):
        super().take(obj)


class LeveledBuff(Buff):
    def __init__(self, level: int, duration: int):
        self.level = level
        self.duration = duration

    def __str__(self) -> str:
        return f"Buff x{self.level}"

    @abstractmethod
    def take(self, obj: "Unit"):
        super().take(obj)


class Barrier(LeveledBuff):
    def __str__(self) -> str:
        return f"护盾 x{self.level}"

    def take(self, obj: "Unit"):
        super().take(obj)


class CritUp(RatedBuff):
    def __str__(self) -> str:
        return f"暴击上升:{self.rate * 100:.0f}%"

    def take(self, obj: "Unit"):
        super().take(obj)
        obj.crit = round(obj.crit * (1 + self.rate))


class DEFUp(RatedBuff):
    def __str__(self) -> str:
        return f"防御上升:{self.rate * 100:.0f}%"

    def take(self, obj: "Unit"):
        super().take(obj)
        obj.def_ = round(obj.def_ * (1 + self.rate))


class ATKUp(RatedBuff):
    def __str__(self) -> str:
        return f"攻击上升:{self.rate * 100:.0f}%"

    def take(self, obj: "Unit"):
        super().take(obj)
        obj.atk = round(obj.atk * (1 + self.rate))


class HPRegen(RatedBuff):
    def __str__(self) -> str:
        return f"持续回复:{self.rate * 100:.0f}%"

    def take(self, obj: "Unit"):
        super().take(obj)
        obj.hp = min(obj.max_hp, obj.hp + round(obj.healing * self.rate))


class Buffs:
    def __init__(self, *buffs: Buff):
        self.buffs: List[Buff] = list(buffs)

    def __iter__(self):
        return self.buffs

    def add(self, other: Union[Buff, "Buffs"]):
        if isinstance(other, Buff):
            self.buffs.append(other)
        elif isinstance(other, Buffs):
            self.buffs.extend(other.buffs)

    def __str__(self) -> str:
        if not self.buffs:
            return ""
        return "[" + " ".join(str(buff) for buff in self.buffs) + "]"

    def take(self, obj: "Unit"):
        # 逆序遍历以便安全删除
        for i in range(len(self.buffs) - 1, -1, -1):
            buff = self.buffs[i]
            try:
                buff.take(obj)
            except BuffAlreadyOver:
                self.buffs.pop(i)

    def has_buff(self, buff_type: Type[Buff]):
        for buff in self.buffs:
            if isinstance(buff, buff_type):
                return True
        else:
            return False


#################### ACTION SYSTEM ####################


class Action:
    def __init__(self, subject: "Unit", object_: "Unit"):
        self.subject = subject
        self.object = object_

    def __str__(self) -> str:
        return f"{self.subject.nickname} 对 {self.object.nickname} 行动"


class AttackAction(Action):
    def __init__(
        self,
        subject: "Unit",
        object_: "Unit",
        damages: Sequence[int],
        originEnemyHP: int,
    ):
        super().__init__(subject, object_)
        self.damages = damages
        self._enemyHP = originEnemyHP
        print(str(self))

    def __str__(self) -> str:
        match restraintAttributeDamageMultiplier(self.subject, self.object):
            case 0:
                resistance = "免疫"
            case 0.5:
                resistance = f"{Fore.BLUE}抵抗{Fore.RESET}"
            case 1:
                resistance = ""
            case 1.5:
                resistance = f"{Fore.LIGHTYELLOW_EX}强效{Fore.RESET}"
            case 2:
                resistance = f"{Fore.YELLOW}克制{Fore.RESET}"
            case _:
                resistance = ""

        dmg_str = " ".join(
            (str(dmg) if dmg else f"{Back.BLACK}MISS{Back.RESET}")
            for dmg in self.damages
        )
        return f"{self.subject.nickname} 攻击 {self.object.nickname} : {resistance}[{dmg_str}]total={(sum_dmg:=sum(self.damages))}\n{self.object.nickname} HP: {self._enemyHP}-{sum_dmg}={self.object.hp}"


#################### UNIT SYSTEM ####################


class Timer:
    def __init__(self, r: int, action: Callable[["Battle"], Action]):
        self.round = r
        self.action = action
        self.r_remaining = self.round

    def act(self, context: "Battle") -> Optional[Action]:
        self.r_remaining -= 1
        if self.r_remaining <= 0:
            self.r_remaining = self.round
            return self.action(context)
        return None


class BuffRemainer:
    """上下文管理器，用于在回合结束时恢复被Buff修改的属性"""

    def __init__(self, unit: "Unit"):
        self.subject = unit

    def __enter__(self):
        # 备份关键属性
        self.backup_atk = self.subject.atk
        self.backup_def = self.subject.def_
        self.backup_crit = self.subject.crit
        # 可以扩展其他属性

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 恢复属性
        self.subject.atk = self.backup_atk
        self.subject.def_ = self.backup_def
        self.subject.crit = self.backup_crit


class Unit(ABC):
    max_hp: int
    atk: int
    def_: int
    healing: int
    accuracy: int
    evasion: int
    crit: int
    crit_res: int
    crit_dmg: float
    crit_dmg_res: float
    stability: int
    mag_count: tuple[int, int]  # (弹匣容量, 单次消耗)

    name: str = "Unknown"
    affiliation: str = "Neutral"

    attr_atk: Attribute
    attr_def: Attribute

    def __init__(self, nickname: str = "", is_enemy=False):
        self.nickname = nickname if nickname else self.name
        self.hp = self.max_hp
        self.mag = self.mag_count[0]
        self.loading = False
        self.buffs = Buffs()
        self.is_enemy = is_enemy
        self.calendar: List[Timer] = []

    @abstractmethod
    def normal_attack(self, target: "Unit") -> tuple[int, ...]:
        dmg = []
        shots = self.mag_count[1]
        for _ in range(shots):
            if self.mag <= 0:
                self.loading = True
                break
            d = target.hit(self, 1)
            dmg.append(d)
            self.mag -= 1
            if target.hp <= 0:
                break
        return tuple(dmg)

    def hit(
        self, attacker: "Unit", rate: float | int = 1, add: int = 0, dmg_split: int = 1
    ) -> int:
        if (not dmg_split.is_integer()) or dmg_split < 1:
            raise ValueError("你这伤害分摊数怎么回事？")

        damage = 0
        # 命中判定
        if attacker.accuracy >= self.evasion:
            success_rate = 1.0
        else:
            success_rate = 700 / (700 + self.evasion - attacker.accuracy)

        if ProbabilityDice("", success_rate, show=False).roll():
            # 伤害计算
            stability_factor = rd.uniform(
                attacker.stability / (attacker.stability + 1000) + 0.2, 1.0
            )

            def_factor = (self.def_ + 1666.66) / 1666.66
            if def_factor < 1.25:
                def_factor = 1.25

            base_dmg = (
                attacker.atk
                * rate
                * restraintAttributeDamageMultiplier(attacker, self)
                * stability_factor
            ) / def_factor
            damage = (base_dmg) / max(1, attacker.mag_count[1])

            # 暴击判定
            crit_chance = (attacker.crit - self.crit_res) / (
                attacker.crit - self.crit_res + 666.66
            )
            crit_chance = max(0, min(1, crit_chance))  # 限制在0-1

            if ProbabilityDice("", crit_chance, show=False).roll():
                damage = damage * attacker.crit_dmg

            damage /= dmg_split

            damage += add

            damage = round(damage)

            # 护盾扣除
            if self.buffs.has_buff(Barrier):
                for i in range(len(self.buffs.buffs) - 1, -1, -1):
                    if isinstance((buff := self.buffs.buffs[i]), Barrier):
                        buff.level -= damage
                        if buff.level > 0:
                            break
                        else:
                            if buff.level < 0:
                                damage += buff.level
                            self.buffs.buffs.pop(i)
            else:
                self.hp -= damage
        return damage

    @abstractmethod
    def decider(self, context: "Battle") -> tuple[Action, ...]:
        pass

    def act(self, context: "Battle") -> tuple[Action, ...]:
        al: List[Action] = []
        self.decider(context)
        with BuffRemainer(self):
            self.buffs.take(self)
            for timer in self.calendar:
                if (a := timer.act(context)) is not None:
                    al.append(a)
        return tuple(al)


class Student(Unit):
    ex_cost: int

    @abstractmethod
    def ex_skill(self, context: "Battle") -> tuple[Action, ...] | None:
        pass

    @abstractmethod
    def basic_skill(self, context: "Battle") -> tuple[Action, ...] | None:
        pass

    @abstractmethod
    def enhanced_skill(self, context: "Battle") -> tuple[Action, ...] | None:
        pass

    @abstractmethod
    def sub_skill(self, context: "Battle") -> tuple[Action, ...] | None:
        pass


#################### BATTLE SYSTEM ####################


class Battle:
    alive_p_units: List[Unit]
    alive_e_units: List[Unit]

    def __init__(self, p_units: List[Unit], e_units: List[Unit], sensei: bool = True):
        self.p_units = p_units
        self.e_units = e_units
        self.sensei = sensei
        self.cost = 0
        self.turn = 1

        print(f"\n{'=' * 30}")
        print("战斗开始".center(30))
        print(f"{'=' * 30}")
        print(" ".join(u.nickname for u in p_units))
        print("VS")
        print(" ".join(u.nickname for u in e_units))
        print(f"{'-' * 30}\n")

    def check_victory(self) -> bool:
        p_alive = any(self.alive_p_units)
        e_alive = any(self.alive_e_units)
        if not p_alive:
            print("\n>>> 失败<<<")
            return True
        if not e_alive:
            print("\n>>> 胜利<<<")
            return True
        return False

    def __getattr__(self, name):
        match name:
            case "alive_p_units":
                return [p_unit for p_unit in self.p_units if p_unit.hp > 0]
            case "alive_e_units":
                return [e_unit for e_unit in self.e_units if e_unit.hp > 0]
            case _:
                raise AttributeError(f'"{name}"')

    def your_enemy(self, is_enemy: bool):
        return self.alive_p_units if is_enemy else self.alive_e_units

    def start(self, max_turns=100):
        while self.turn <= max_turns:
            print(f"\n--- 第 {self.turn} 回合 ---")

            print(f"【友方回合】")
            for p_unit in self.p_units:
                if p_unit.hp > 0:
                    print(f"{p_unit.nickname}开始行动")
                else:
                    continue

                if isinstance(p_unit, Student):
                    if p_unit.ex_cost <= self.cost:
                        if self.sensei:
                            if (
                                input(
                                    f"是否使用EX技能({p_unit.ex_cost}/{self.cost})[Y/N(默认)]"
                                ).upper()
                                == "Y"
                            ):
                                p_unit.ex_skill(self)
                        else:
                            if ProbabilityDice("是否使用EX技能", 0.75).roll():
                                p_unit.ex_skill(self)

                if p_unit.loading:
                    print(f"  {p_unit.nickname} 正在装弹")
                    p_unit.loading = False
                    p_unit.mag = p_unit.mag_count[0]
                else:
                    actions = p_unit.act(self)
                    for act in actions:
                        print(f"  > {act}")
                print()
                self.cost = min(10, self.cost + 1)

            if self.sensei:
                input()
            if self.check_victory():
                break

            print(f"\n【敌方回合】")
            for e_unit in self.e_units:
                if e_unit.hp > 0:
                    print(f"{e_unit.nickname}开始行动")
                else:
                    continue

                if e_unit.loading:
                    print(f"  {e_unit.nickname} 正在装弹")
                    e_unit.loading = False
                    e_unit.mag = e_unit.mag_count[0]
                else:
                    actions = e_unit.act(self)
                    for act in actions:
                        print(f"  > {act}")
                print()

            if self.sensei:
                input()
            if self.check_victory():
                break

            self.turn += 1

            print("状态".center(10, "*"))
            print(f"COST: {self.cost}")
            print("【友方】")
            for p_unit in self.p_units:
                if p_unit.hp > 0:
                    print(f"{p_unit.nickname}:{p_unit.hp} {p_unit.buffs}")
            print("【敌方】")
            for e_unit in self.e_units:
                if e_unit.hp > 0:
                    print(f"{e_unit.nickname}:{e_unit.hp} {e_unit.buffs}")
            if self.sensei:
                input()
