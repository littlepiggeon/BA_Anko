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

# 新功能
可以使用`./BAAnko/text2mmt.py`与Momotalk进行联动  
需要选择一个已有的聊天进行追加  
所有文本均以透明旁白的形式输出  
旧的聊天文件会被备份\(.bak\)