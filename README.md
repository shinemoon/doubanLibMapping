# doubanLibMapping
扫描豆瓣书单并在杭州图书馆扫描是否有在库书籍

### 依赖：
- beautifulsoup4==4.9.1 (pip install bs4)
- requests==2.24.0
- progressbar2==3.51.3 (**Important: pip install progressbar2**)

### 使用：

`python3 run.py`

使用前自行修改想读用户的用户id，以及相应的图书馆分馆地址

### 文件:

- run.py: 主文件
- piplibs.list:  依赖
- doubanSpider.py: 不需要，当时只是拿来做参考的....
