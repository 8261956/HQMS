# MSSQL 驱动安装

使用`web.py`操作`SQL Server`数据库时，需要`pymssql`驱动。

安装步骤如下：

## 1. 安装FreeTDS

CentOS: 
```bash
yum install freetds     #为避免出现问题，最好安装freetds 0.91版本
```

安装完成后，可以使用下面的命令进行测试：
```bash
tsql -H host -p 1433 -U user
```

## 2. 安装pymssql

可以使用`pip`安装`pymssql`：
```bash
pip install pymssql
```
安装完成后，就可以使用`web.py`操作`SQL Server`数据库。

## 3. FAQ

如果在安装的时候出现问题，可以参考：

- `yum install freetds`时出现`No matches found`错误：
    
    ```bash
    # 更新源
    yum search epel
  
    # 选择一个版本安装epel
    yum install epel-release.noarch
  
    # 之后再安装freetds
    ```
    
- 安装`pymssql`失败

    ```bash
    # 可能原因是freetds版本有问题，先卸载freetds
    yum remove freetds
  
    # 再搜索freetds的包
    yum search freetds
  
    # 再选择合适的包
    yum install freetds-devel.x86_64
  
    # 最后再安装pymssql
    pip install pymssql
    ```

## 4. 使用web.py建立数据库连接

使用`web.py`建立`SQL Server`数据库连接：
```python
import web

db = web.database(
    dbn='mssql',
    host='192.168.17.98',
    port=1433,
    user='sa',
    pw='123456',
    db='HisQueue'
)
```

## 5. 数据库及SQL连接信息

#### 数据库信息
```
数据库类型：mssql
数据库地址：192.168.17.98
端口：1433
用户名：sa
密码：123456
编码：utf8
数据库名：HisQueue
数据库表名：visitors
```

#### SQL连接信息

注：根据源表相应字段进行填写。

```
病人编号：log_id
病人姓名：name
挂号科室或队列：queue
挂号类型：yuyue
挂号日期：date
挂号时间：time
预约日期：
预约时间：
病人描述：
病人年纪：
是否为VIP用户：jizhen
病人状态：
病人在队列中的序号：snumber
医生编号：
医生姓名：
科室名称：
病人医保卡：
病人身份证：
病人手机号：
刷新时间：10
```