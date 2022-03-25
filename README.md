# CookEverything

一个用 Python 编写的简易菜谱转 JSON 转换器。菜谱基于 [HowToCook](https://github.com/Anduin2017/HowToCook) 。

## Usage

使用 `CookEverything` 类即可完成转换，详情请参见源码：

```python
from cook_everything import CookEverything

cook = CookEverything()
cook.generate_json("./data/dishes/xxx")
```

## Licensing

本项目基于 MIT 版权协议。