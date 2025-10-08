from typing import Generic, TypeVar, List, Any, Iterator, Optional

T = TypeVar("T")

# --------------------------------------------------------
# TStringList (含簡單 Objects 支援)
# --------------------------------------------------------
class TStringList:
    def __init__(self):
        self.items: List[str] = []
        self._objects: List[Any] = []

    def Add(self, value: str, obj: Any = None) -> int:
        """回傳新加入項目的索引 (像 BCB 的 Add 回傳 index)"""
        self.items.append(value)
        self._objects.append(obj)
        return len(self.items) - 1

    def Insert(self, index: int, value: str, obj: Any = None):
        self.items.insert(index, value)
        self._objects.insert(index, obj)

    def Delete(self, index: int):
        self.items.pop(index)
        self._objects.pop(index)

    def Clear(self):
        self.items.clear()
        self._objects.clear()

    def Sort(self):
        # 排序時一併保留 objects 對應關係
        zipped = list(zip(self.items, self._objects))
        zipped.sort(key=lambda pair: pair[0])
        if zipped:
            self.items, self._objects = map(list, zip(*zipped))
        else:
            self.items, self._objects = [], []

    def IndexOf(self, value: str) -> int:
        try:
            return self.items.index(value)
        except ValueError:
            return -1

    def Count(self) -> int:
        """與 BCB 的 Count() 類似"""
        return len(self.items)

    # Objects 存取（模擬 TStringList.Objects[index]）
    def Objects(self, index: int) -> Any:
        return self._objects[index]

    def SetObject(self, index: int, obj: Any):
        self._objects[index] = obj

    def __getitem__(self, index: int) -> str:
        return self.items[index]

    def __setitem__(self, index: int, value: str):
        self.items[index] = value

    def __len__(self) -> int:
        return len(self.items)

    def __iter__(self) -> Iterator[str]:
        return iter(self.items)

    def __repr__(self):
        return f"TStringList({self.items})"


# --------------------------------------------------------
# TList<T>
# --------------------------------------------------------
class TList(Generic[T]):
    def __init__(self):
        self.items: List[T] = []

    def Add(self, value: T) -> int:
        self.items.append(value)
        return len(self.items) - 1

    def Delete(self, index: int):
        self.items.pop(index)

    def Clear(self):
        self.items.clear()

    def Count(self) -> int:
        return len(self.items)

    def __getitem__(self, index: int) -> T:
        return self.items[index]

    def __setitem__(self, index: int, value: T):
        self.items[index] = value

    def __len__(self) -> int:
        return len(self.items)

    def __iter__(self) -> Iterator[T]:
        return iter(self.items)

    def __repr__(self):
        return f"TList({self.items})"


# --------------------------------------------------------
# DynamicArray<T>
# --------------------------------------------------------
class DynamicArray(Generic[T]):
    def __init__(self, initial: Optional[List[T]] = None):
        self.items: List[T] = list(initial) if initial is not None else []

    def Add(self, value: T) -> int:
        self.items.append(value)
        return len(self.items) - 1

    def Resize(self, new_size: int, default: Optional[T] = None):
        if new_size < len(self.items):
            # truncate
            self.items = self.items[:new_size]
        else:
            # extend with default
            self.items.extend([default] * (new_size - len(self.items)))

    def Length(self) -> int:
        return len(self.items)

    def __getitem__(self, index: int) -> T:
        return self.items[index]

    def __setitem__(self, index: int, value: T):
        self.items[index] = value

    def __len__(self) -> int:
        return len(self.items)

    def __iter__(self) -> Iterator[T]:
        return iter(self.items)

    def __repr__(self):
        return f"DynamicArray({self.items})"
