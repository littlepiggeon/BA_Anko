# BA Anko

## Example案例

```python
from BAAnko import Battle
from BAAnko.students.ayane import OkusoraAyane
from BAAnko.students.hina import SorasakiHina
from BAAnko.students.hoshino import TakanashiHoshino
from BAAnko.students.shiroko import SunaookamiShiroko

b = Battle(
    [SorasakiHina(""), OkusoraAyane("")],
    [TakanashiHoshino(""), SunaookamiShiroko("")],
    sensei=False,
)
b.start()
```

or...或者...

```python
from BAAnko import Battle
from BAAnko.students.ayane import OkusoraAyane
from BAAnko.students.hina import SorasakiHina
from BAAnko.students.hoshino import TakanashiHoshino
from BAAnko.students.shiroko import SunaookamiShiroko

b = Battle(
    [SorasakiHina(""), OkusoraAyane("")],
    [TakanashiHoshino(""), SunaookamiShiroko("")],
    sensei=True,
)
b.start()
```

But you need to decide if it's time to EX.但你需要自己决定是否EX。