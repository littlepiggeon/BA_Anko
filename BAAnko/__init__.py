import random as rd
import sys
from abc import abstractmethod, ABC
from enum import Enum, IntEnum, Flag, auto
from typing import Callable, Sequence, List, Union, Type, TextIO

from colorama import init, Fore, Back, Style

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
        print(f"选择攻击[{', '.join(str(u) for u in r)}]")
        return r


class Attribute(IntEnum):
    GRAY = 0
    RED = 1
    YELLOW = 2
    GREEN = 3
    BLUE = 4
    VIOLET = 5


class Weapon(IntEnum):
    SG = 0  # 霰弹枪
    SMG = 1  # 冲锋枪
    AR = 2  # 突击步枪
    GL = 3  # 榴弹发射器
    HG = 4  # 手枪
    SR = 5  # 狙击步枪
    RG = 6  # 轨道炮
    MG = 7  # 机枪
    RL = 8  # 导弹发射器
    MT = 9  # 迫击炮
    FT = 10  # 火焰喷射器
    SPECEIL = 99


W = Weapon


def restraint_attribute_damage_multiplier(
    attacker: "Unit", defender: "Unit"
) -> float | int:
    """属性克制伤害倍率"""
    table = (
        (1, 1, 1, 1, 1, 1),
        (1, 2, 1, 1, 0.5, 0.5),
        (1, 0.5, 2, 1, 1, 1),
        (1, 0.5, 1.5, 2, 1, 1),
        (1, 1, 0.5, 0.5, 2, 1),
        (1, 1, 0.5, 0.5, 1.5, 2),
    )
    return table[attacker.attr_atk.value][defender.attr_def.value]


RADM = restraint_attribute_damage_multiplier


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
            raise BuffAlreadyOver("Buff效果已结束")


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
        return f"暴击值上升:{self.rate * 100:.0f}%"

    def take(self, obj: "Unit"):
        super().take(obj)
        obj.crit = round(obj.crit * (1 + self.rate))


class CritRESUP(RatedBuff):
    def __str__(self) -> str:
        return f"暴击抵抗力上升:{self.rate * 100:.0f}%"

    def take(self, obj: "Unit"):
        super().take(obj)
        obj.crit_res = round(obj.crit_res * (1 + self.rate))


class CritDMGUP(RatedBuff):
    def __str__(self) -> str:
        return f"暴击伤害上升:{self.rate * 100:.0f}%"

    def take(self, obj: "Unit"):
        super().take(obj)
        obj.crit_dmg = obj.crit_dmg * (1 + self.rate)


class DEFUp(RatedBuff):
    def __str__(self) -> str:
        return f"防御力上升:{self.rate * 100:.0f}%"

    def take(self, obj: "Unit"):
        super().take(obj)
        obj.def_ = round(obj.def_ * (1 + self.rate))


class ATKUp(RatedBuff):
    def __str__(self) -> str:
        return f"攻击力上升:{self.rate * 100:.0f}%"

    def take(self, obj: "Unit"):
        super().take(obj)
        obj.atk = round(obj.atk * (1 + self.rate))


class HealingUP(RatedBuff):
    def __str__(self) -> str:
        return f"治疗力上升:{self.rate * 100:.0f}%"

    def take(self, obj: "Unit"):
        super().take(obj)
        obj.healing = round(obj.healing * (1 + self.rate))


class EvasionUP(RatedBuff):
    def __str__(self) -> str:
        return f"闪避值上升:{self.rate * 100:.0f}%"

    def take(self, obj: "Unit"):
        super().take(obj)
        obj.evasion = round(obj.evasion * (1 + self.rate))


class HPRegen(RatedBuff):
    def __str__(self) -> str:
        return f"持续回复:{self.rate * 100:.0f}%"

    def take(self, obj: "Unit"):
        super().take(obj)
        obj.recover(round(obj.healing * self.rate))


class Buffs:
    def __init__(self, master: "Unit", *buffs: Buff):
        self.master = master
        self.buffs: List[Buff] = list(buffs)

    def __iter__(self):
        return self.buffs

    def _buff_add(self, buff):
        ReportBuff(self.master, buff).report()
        repeat=False
        for i in self.buffs:
            repeat=True
            if isinstance(i, buff.__class__):
                if isinstance(i, LeveledBuff):
                    i.level += buff.level
                elif isinstance(i, RatedBuff):
                    i.rate += buff.rate
                if i.duration > -1:
                    i.duration = (i.duration + buff.duration) // 2
        if not repeat:
            self.buffs.append(buff)

    def add(self, buff: "Buff|Buffs"):
        if isinstance(buff, Buff):
            self._buff_add(buff)
        elif isinstance(buff, Buffs):
            # pyrefly: ignore [not-iterable]
            for i in buff:
                self._buff_add(i)

    def __str__(self) -> str:
        if len(self.buffs) == 0:
            return ""
        else:
            return "(" + " ".join(str(buff) for buff in self.buffs) + ")"

    def take(self, obj: "Unit"):
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


#################### EVENT SYSTEM ####################
class Event:
    def __init__(
        self,
        name: str,
        action: Callable[["Battle"], None],
        condition: Callable[["Battle"], bool],
    ):
        self.name = name
        self.action = action
        self.condition = condition
        self.available = True

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}("{self.name}")>'

    def trigger(self, context: "Battle"):
        if self.available:
            if self.condition(context):
                self.action(context)
        else:
            raise Exception(repr(self), "is not available, should not be triggered")


class EventManager:
    def __init__(self):
        self._events: List[Event] = []

    def __iter__(self):
        for i in self._events:
            yield i

    def add(self, event: Event):
        self._events.append(event)

    def trigger(self, context: "Battle"):
        for i in range(len(self._events) - 1, -1, -1):
            event = self._events[i]
            if event.available:
                event.trigger(context)
            else:
                self._events.pop(i)

    def clear(self):
        self._events.clear()


#################### UNIT SYSTEM ####################
class DMGFlag(Flag):
    CRIT = 0b1
    SKILL = 0b10


class BuffRemainer:
    """上下文管理器，用于在回合结束时恢复被Buff修改的属性"""

    def __init__(self, unit: "Unit"):
        self.subject = unit

    def __enter__(self):
        # 备份关键属性
        self.bak_atk = self.subject.atk
        self.bak_def = self.subject.def_
        self.bak_healing = self.subject.healing
        self.bak_accuracy = self.subject.accuracy
        self.bak_evasion = self.subject.evasion
        self.bak_crit = self.subject.crit
        self.bak_crit_res = self.subject.crit_res
        self.bak_crit_dmg = self.subject.crit_dmg
        self.bak_crit_dmg_res = self.subject.crit_dmg_res
        # 可以扩展其他属性

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 恢复属性
        self.subject.atk = self.bak_atk
        self.subject.def_ = self.bak_def
        self.subject.healing = self.bak_healing
        self.subject.accuracy = self.bak_accuracy
        self.subject.evasion = self.bak_evasion
        self.subject.crit = self.bak_crit
        self.subject.crit_res = self.bak_crit_res
        self.subject.crit_dmg = self.bak_crit_dmg
        self.subject.crit_dmg_res = self.bak_crit_dmg_res


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

    weapon: int
    attr_atk: Attribute
    attr_def: Attribute

    name: str = "Unknown"
    affiliation: str = "Neutral"
    is_enemy: bool = False

    def __init__(self, nickname: str = ""):
        self.nickname = nickname if nickname else self.name
        self.hp = self.max_hp
        self.mag = self.mag_count[0]
        self.loading = False
        self.buffs = Buffs(self)
        self.event_manager = EventManager()

    def __str__(self) -> str:
        return f"{self.nickname}:{self.hp}{self.buffs}"

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}(name="{self.name}", affiliation="{self.affiliation}")>'

    def on_start(self, context):
        pass

    def normal_attack(self, context: "Battle", flag=DMGFlag(0)):
        enemies = context.your_enemy(self.is_enemy)
        match self.weapon:
            case W.SG | W.GL | W.RL | W.MT | W.FT:
                hit_num = rd.sample((1, 2, 3), 1, counts=(10, 3, 1))[0]
            case W.SMG | W.AR | W.HG | W.SR | W.RG | W.MG:
                hit_num = 1
            case _:
                raise ValueError(f"Unknown weapon type")
        self._attack(
            UnitChoiceDice("谁被攻击了？", enemies, hit_num).roll(),
            self.mag_count[1],
            1,
            0,
            self.mag_count[1],
            flag,
        )

    def _attack(
        self,
        targets: Sequence["Unit"],
        attaking_num: int,
        rate: float | int,
        add: float | int = 0,
        dmg_split: int = 1,
        flag=DMGFlag(0),
    ):
        for target in targets:
            reporter = ReportDamage(self, target)
            reporter.start()
            for _ in range(attaking_num):
                dmg, flag = target.hit(self, rate, add, dmg_split, flag)
                reporter.record(dmg, flag)
            reporter.report()

    def hit(
        self,
        attacker: "Unit",
        rate: float | int = 1,
        add: float | int = 0,
        dmg_split: int = 1,
        flag=DMGFlag(0),
    ) -> tuple[int, DMGFlag]:
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

            def_factor = 1 + self.def_ / 1666.66
            if 1 / def_factor < 0.2:
                def_factor = 5

            damage = (
                attacker.atk * rate * RADM(attacker, self) * stability_factor
            ) / def_factor

            crit_chance = (attacker.crit - self.crit_res) / (
                attacker.crit - self.crit_res + 666.66
            )
            crit_chance = max(0, min(1, crit_chance))

            if ProbabilityDice("", crit_chance, show=False).roll():
                damage = damage * attacker.crit_dmg * (1 - self.crit_dmg_res)
                flag |= DMGFlag.CRIT

            damage /= dmg_split

            damage += add

            if damage < 0:
                damage = 0

            damage = round(damage)

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
        return damage, flag

    def recover(self, hp: int):
        self.hp = min(self.max_hp, self.hp + hp)
        ReportRecover(self, hp).report()

    def decider(self, context: "Battle"):
        if isinstance(self, Student):
            if self.type == StudentType.SPECIEL:
                return
        self.normal_attack(context)

    def act(self, context: "Battle"):
        with BuffRemainer(self):
            self.buffs.take(self)
            self.event_manager.trigger(context)
            self.decider(context)


class StudentType(Enum):
    STRIKER = auto()
    SPECIEL = auto()


class Student(Unit):
    type: StudentType = StudentType.STRIKER
    ex_cost: int

    def __init__(self, nickname: str = ""):
        super().__init__(nickname)

    @abstractmethod
    def ex_skill(self, context: "Battle"):
        pass

    @abstractmethod
    def basic_skill(self, context: "Battle"):
        pass

    @abstractmethod
    def enhanced_skill(self, context: "Battle"):
        pass

    @abstractmethod
    def sub_skill(self, context: "Battle"):
        pass

    def decider(self, context: "Battle"):
        if self.type == StudentType.STRIKER:
            super().decider(context)


#################### BATTLE SYSTEM ####################
class Report(ABC):
    def __init__(
        self,
        subject: "Unit|None",
        object_: "Sequence[Unit]|Unit|None",
        file: TextIO = sys.stdout,
    ):
        self.subject = subject
        self.object = object_
        self.file = file

    @abstractmethod
    def report(self):
        pass

    def _print(self, *args, **kwargs):
        if "file" in kwargs.keys():
            raise Exception("你要造反？！")
        print(*args, **kwargs, file=self.file)


class ReportDamage(Report):
    def __init__(self, subject: "Unit", object_: "Unit", file: TextIO = sys.stdout):
        if (subject is None) or (object_ is None):
            raise Exception("你要造反？！")

        super().__init__(subject, object_, file)
        self.oringinal_hp = object_.hp
        self.active = False
        self.delt_damage = 0
        self.resistance = ""
        match RADM(subject, object_):
            case 0:
                self.resistance = f"{Back.RED}Immune{Back.RESET}"
            case 0.5:
                self.resistance = f"{Fore.BLUE}Resist{Fore.RESET}"
            case 1.5:
                self.resistance = f"{Fore.LIGHTYELLOW_EX}Effective{Fore.RESET}"
            case 2:
                self.resistance = f"{Fore.YELLOW}Weak{Fore.RESET}"

    def start(self):
        self.active = True
        self._print(f"{self.subject} 攻击 {self.object}  {self.resistance}[ ", end="")

    def record(self, damage: int, flag=DMGFlag(0)):
        if not self.active:
            raise Exception(f"{self.__class__.__name__}.start() first")
        self.delt_damage += damage
        self._print(f"{Back.LIGHTWHITE_EX if damage == 0 else ''}\
{Fore.RED if DMGFlag.CRIT in flag else ''}\
{Style.BRIGHT if DMGFlag.SKILL in flag else ''}\
{"MISS" if damage == 0 else damage}{Style.RESET_ALL}", end=" ")

    def stop(self):
        self.active = False

    def report(self):
        self.stop()
        self._print(f"]total={self.delt_damage}")


class ReportRecover(Report):
    def __init__(
        self,
        subject: "Unit",
        hp: int,
        file: TextIO = sys.stdout,
    ):
        super().__init__(subject, None, file)
        self.hp = hp

    def report(self):
        self._print(f"{self.subject} 回复了 {self.hp} HP")


class ReportBuff(Report):
    def __init__(self, object_: "Unit", buff: Buff, file: TextIO = sys.stdout):
        super().__init__(None, object_, file)
        self.buff = buff

    def report(self):
        self._print(f"{self.object} 获得 {self.buff}")


class ReportSkill(Report):
    def __init__(
        self, subject: "Unit", name: str, enhanced=False, file: TextIO = sys.stdout
    ):
        super().__init__(subject, None, file)
        self.name = name
        self.enhanced = enhanced

    def report(self):
        if self.enhanced:
            self._print(f"{self.subject} 技能【{self.name}】生效了")
        else:
            self._print(f"{self.subject} 施放了技能【{self.name}】")


class Battle:
    alive_p_units: List[Unit]
    alive_e_units: List[Unit]

    def __init__(self, p_units: List[Unit], e_units: List[Unit], sensei: bool = True):
        self.p_units = p_units
        self.e_units = e_units
        self.sensei = sensei
        self.cost = 0
        self.round = 1

        print(f"\n{'=' * 30}")
        print("战斗开始".center(30))
        print(f"{'=' * 30}")
        print(" ".join(str(u) for u in p_units))
        print("VS")
        print(" ".join(str(u) for u in e_units))
        print(f"{'-' * 30}\n")

        for e_unit in self.e_units:
            e_unit.is_enemy = True

        for unit in self.p_units + self.e_units:
            unit.on_start(self)

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
                return [
                    p_unit
                    for p_unit in self.p_units
                    if p_unit.hp > 0
                    and (
                        (False if p_unit.type == StudentType.SPECIEL else True)
                        if isinstance(p_unit, Student)
                        else True
                    )
                ]
            case "alive_e_units":
                return [
                    e_unit
                    for e_unit in self.e_units
                    if e_unit.hp > 0
                    and (
                        (False if e_unit.type == StudentType.SPECIEL else True)
                        if isinstance(e_unit, Student)
                        else True
                    )
                ]
            case _:
                raise AttributeError(f'"{name}"')

    def your_enemy(self, is_enemy: bool):
        return self.alive_p_units if is_enemy else self.alive_e_units

    def your_pal(self, is_enemy: bool):
        return self.alive_e_units if is_enemy else self.alive_p_units

    def start(self, max_turns=100):
        while self.round <= max_turns:
            print(f"\n--- 第 {self.round} 回合 ---")

            print(f"【友方回合】")
            for p_unit in self.p_units:
                if p_unit.hp > 0:
                    print(f"{p_unit} 开始行动")
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
                    print(f"  {p_unit} 正在装弹")
                    p_unit.loading = False
                    p_unit.mag = p_unit.mag_count[0]
                else:
                    p_unit.act(self)
                print()
                self.cost = min(10, self.cost + 1)

                if self.check_victory():
                    return

            if self.sensei:
                input()

            print(f"\n【敌方回合】")
            for e_unit in self.e_units:
                if e_unit.hp > 0:
                    print(f"{e_unit} 开始行动")
                else:
                    continue

                if e_unit.loading:
                    print(f"  {e_unit} 正在装弹")
                    e_unit.loading = False
                    e_unit.mag = e_unit.mag_count[0]
                else:
                    e_unit.act(self)
                print()

                if self.check_victory():
                    return

            if self.sensei:
                input()

            self.round += 1

            print("状态".center(10, "*"))
            print(f"COST: {self.cost}")
            print("【友方】")
            for p_unit in self.p_units:
                if p_unit.hp > 0:
                    print(p_unit)
            print("【敌方】")
            for e_unit in self.e_units:
                if e_unit.hp > 0:
                    print(e_unit)
            if self.sensei:
                input()
