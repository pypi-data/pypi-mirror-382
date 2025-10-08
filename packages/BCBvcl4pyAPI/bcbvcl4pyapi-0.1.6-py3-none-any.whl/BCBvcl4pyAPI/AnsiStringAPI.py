class AnsiString:
    def __init__(self, Pms_str: str = '', encoding: str = 'byte'):
        """
        encoding:
            'byte' -> BCB5 byte模式（中文佔兩個byte）
            'unicode' -> Unicode 字元模式
        """
        self.encoding = encoding
        self.set(Pms_str)

    # ---------------------------------------------
    # 改變內容
    # ---------------------------------------------
    def set(self, Pms_str: str):
        if self.encoding == 'byte':
            self._data = Pms_str.encode('big5', errors='replace')
        else:
            self._data = Pms_str.encode('utf-8')
        return self  # 支援連鎖呼叫

    # ---------------------------------------------
    # 轉成 Python str
    # ---------------------------------------------
    def str(self):
        if self.encoding == 'byte':
            return self._data.decode('big5', errors='replace')
        else:
            return self._data.decode('utf-8')

    def __str__(self):
        return self.str()

    # ---------------------------------------------
    # 取 C 字串 bytes
    # ---------------------------------------------
    def c_str(self):
        return self._data

    # ---------------------------------------------
    # 支援索引取單 byte
    # ---------------------------------------------
    def __getitem__(self, index):
        return self._data[index]

    # ---------------------------------------------
    # SubString
    # mode='byte' / 'unicode'
    # ---------------------------------------------
    def SubString(self, start: int, length: int = None, mode: str = None):
        mode = mode or self.encoding
        if mode == 'unicode':
            s = self.str()
            start -= 1
            if length is None:
                return AnsiString(s[start:], encoding=self.encoding)
            else:
                return AnsiString(s[start:start+length], encoding=self.encoding)
        elif mode == 'byte':
            start -= 1
            if length is None:
                return AnsiString(self._data[start:].decode('big5', errors='replace'), encoding=self.encoding)
            else:
                return AnsiString(self._data[start:start+length].decode('big5', errors='replace'), encoding=self.encoding)
        else:
            raise ValueError("mode must be 'byte' or 'unicode'")

    # ---------------------------------------------
    # 長度
    # ---------------------------------------------
    def Length(self, mode: str = None):
        mode = mode or self.encoding
        if mode == 'unicode':
            return len(self.str())
        elif mode == 'byte':
            return len(self._data)
        else:
            raise ValueError("mode must be 'byte' or 'unicode'")

    @staticmethod
    def strlen(Pms_str: str, encoding: str = 'byte'):
        if encoding == 'unicode':
            return len(Pms_str)
        elif encoding == 'byte':
            return len(Pms_str.encode('big5', errors='replace'))
        else:
            raise ValueError("encoding must be 'byte' or 'unicode'")

    # ---------------------------------------------
    # 常用方法
    # ---------------------------------------------
    def Trim(self):
        return AnsiString(self.str().strip(), encoding=self.encoding)

    def UpperCase(self):
        return AnsiString(self.str().upper(), encoding=self.encoding)

    def LowerCase(self):
        return AnsiString(self.str().lower(), encoding=self.encoding)

    def Pos(self, sub: str):
        idx = self.str().find(sub)
        return idx + 1 if idx >= 0 else 0

    @staticmethod
    def StringOfChar(char: str, count: int, encoding='byte'):
        return AnsiString(char * count, encoding=encoding)

    @staticmethod
    def sprintf(fmt: str, *args, encoding='byte'):
        return AnsiString(fmt % args, encoding=encoding)

    # ---------------------------------------------
    # + 運算子
    # ---------------------------------------------
    def __add__(self, other):
        if isinstance(other, AnsiString):
            combined_str = self.str() + other.str()
        elif isinstance(other, str):
            combined_str = self.str() + other
        else:
            raise TypeError("Can only add AnsiString or str")
        return AnsiString(combined_str, encoding=self.encoding)

    # ---------------------------------------------
    # += 原地累加
    # ---------------------------------------------
    def __iadd__(self, other):
        if isinstance(other, AnsiString):
            new_str = self.str() + other.str()
        elif isinstance(other, str):
            new_str = self.str() + other
        else:
            raise TypeError("Can only add AnsiString or str")
        if self.encoding == 'byte':
            self._data = new_str.encode('big5', errors='replace')
        else:
            self._data = new_str.encode('utf-8')
        return self

# ================================================================================
if(__name__=="__main__"):
    s = AnsiString("  test--測試1234  ")

    # 連鎖呼叫
    result = s.Trim().UpperCase().SubString(3,5)
    print(str(result))  # 結果: "ST--測試1"

    # 改變內容也可以連鎖
    s.set("abc 中文").UpperCase().Trim()
    print(str(s))       # "ABC 中文"

    # 取長度
    print(s.Length())           # byte 長度
    print(s.Length(mode='unicode'))  # 字元長度

    # 靜態 strlen
    ms_MyStr = "test--測試1234"
    mi_Len = AnsiString.strlen(ms_MyStr, encoding="unicode")
    print("mi_Len unicode:", mi_Len)
    mi_Len_byte = AnsiString.strlen(ms_MyStr, encoding="byte")
    print("mi_Len byte:", mi_Len_byte)

    # SubString byte/unicode
    print(str(s.SubString(2,3)))                 # byte模式
    print(str(s.SubString(2,3, mode='unicode'))) # unicode模式


    s.set(str(ms_MyStr))
    print(s.str())       # "新的字串" -> 大寫 "新的字串"
    print(s.Pos("測"))
    
    print(f"[{s}] ----> len1={s.Length()}");
    s+="-->增加字";
    print(f"[{s}] ----> len2={s.Length()}");
