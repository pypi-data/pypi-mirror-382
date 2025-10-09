from BCBvcl4pyAPI import HyperDynamicArray
from dataclasses import dataclass

@dataclass
class TPerson:
    name: str
    age: int

# 建立記憶體 table 模式
arr = HyperDynamicArray[TPerson](
    mysql_host="mis.gotech.biz",
    mysql_port= 3300,
    mysql_user="root",
    mysql_password="gotechdf8000sys",
    mysql_db="df8000",
    table_name="_mem_dataset",
    table_type="memory"
)

arr.Clear();

# 加入元素
for i in range(500):
    arr.Add(TPerson(f"Person{i}", 20+i))

print("元素總數:", arr.Count())

# 讀取
for i in range(arr.Count()):
    print(arr[i])

print(arr[106].name);

# 清空 table
#arr.Clear()
#print("清空後元素總數:", arr.Count())

arr.Close()
