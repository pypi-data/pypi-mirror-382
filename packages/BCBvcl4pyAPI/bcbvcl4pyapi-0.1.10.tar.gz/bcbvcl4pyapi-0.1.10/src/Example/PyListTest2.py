from BCBvcl4pyAPI import TStringList
from BCBvcl4pyAPI import DynamicArray

obj_MyList   : TStringList;
mda_MyValues : DynamicArray;
mi_c         : int = 0;

mda_MyValues = DynamicArray();

mda_MyValues.Add(0.319);
mda_MyValues.Add(4.123);
mda_MyValues.Add(3.621);

for mi_c in range(0, mda_MyValues.Length()):
    print(mda_MyValues[mi_c]);


obj_MyList = TStringList();
obj_MyList.Add("OKOK");