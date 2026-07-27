# BA Anko
## Example案例
```python
from BAAnko import Battle
from BAAnko.students.hina import SorasakiHina
from BAAnko.students.hoshino import TakanashiHoshino

Battle([SorasakiHina('1'), SorasakiHina('2'), SorasakiHina('3'), SorasakiHina('4')],
       [TakanashiHoshino('a', True), TakanashiHoshino('b', True)]).start()
```
