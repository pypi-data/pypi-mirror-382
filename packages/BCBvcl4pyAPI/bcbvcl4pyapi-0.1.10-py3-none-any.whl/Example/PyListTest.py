from BCBvcl4pyAPI import TStringList
from BCBvcl4pyAPI import DynamicArray

mi_c : int = 0;

obj_StrList = TStringList();

obj_StrList.Add("Str--1");
obj_StrList.Add("Str--2");

print();
for mi_c in range(0, obj_StrList.Count()):
    print(f"data {mi_c}: {obj_StrList[mi_c]}");


mda_Values = DynamicArray[float]();

mda_Values.Add(1.2);
mda_Values.Add(2.2);
mda_Values.Add(3.2);
mda_Values.Add(4.2);
mda_Values.Add(5.2);

for mi_c in range(0, mda_Values.Length()):
    print(f"data_float = {mda_Values[mi_c]}");
