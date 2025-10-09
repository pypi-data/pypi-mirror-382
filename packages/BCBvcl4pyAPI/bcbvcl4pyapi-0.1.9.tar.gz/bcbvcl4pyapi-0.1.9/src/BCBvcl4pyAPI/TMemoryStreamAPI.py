import io
import os
import pickle

class TStream:
    def __init__(self):
        self._stream = io.BytesIO()

    # ---- 屬性 ----
    @property
    def Position(self) -> int:
        return self._stream.tell()

    @Position.setter
    def Position(self, value: int):
        self._stream.seek(value, io.SEEK_SET)

    @property
    def Size(self) -> int:
        current = self._stream.tell()
        self._stream.seek(0, io.SEEK_END)
        size = self._stream.tell()
        self._stream.seek(current, io.SEEK_SET)
        return size

    # ---- 基本方法 ----
    def Seek(self, Offset: int, Origin: int = io.SEEK_SET) -> int:
        """移動資料指標"""
        return self._stream.seek(Offset, Origin)

    def Read(self, Buffer, Count: int) -> int:
        """讀取 Count 個位元組到 Buffer"""
        data = self._stream.read(Count)
        if isinstance(Buffer, bytearray):
            Buffer[:len(data)] = data
        return len(data)

    def Write(self, Buffer, Count: int) -> int:
        """寫入 Count 個位元組"""
        if isinstance(Buffer, (bytes, bytearray)):
            self._stream.write(Buffer[:Count])
            return Count
        raise TypeError("Buffer must be bytes or bytearray")

    def ReadBuffer(self, Count: int) -> bytes:
        """讀取指定長度的 bytes"""
        return self._stream.read(Count)

    def WriteBuffer(self, Data: bytes):
        """直接寫入 bytes"""
        self._stream.write(Data)

    def Clear(self):
        """清空資料"""
        self._stream = io.BytesIO()

    def SetSize(self, NewSize: int):
        """設定串流大小"""
        current = self._stream.tell()
        data = self._stream.getvalue()
        if NewSize < len(data):
            data = data[:NewSize]
        else:
            data += b'\x00' * (NewSize - len(data))
        self._stream = io.BytesIO(data)
        self._stream.seek(min(current, NewSize))

    def LoadFromFile(self, FileName: str):
        """從檔案載入"""
        if not os.path.exists(FileName):
            raise FileNotFoundError(FileName)
        with open(FileName, "rb") as f:
            self._stream = io.BytesIO(f.read())
        self._stream.seek(0)

    def SaveToFile(self, FileName: str):
        """儲存至檔案"""
        with open(FileName, "wb") as f:
            current = self._stream.tell()
            self._stream.seek(0)
            f.write(self._stream.read())
            self._stream.seek(current)

    # ---- 擴充：物件序列化 ----
    def WriteObject(self, obj):
        """序列化並寫入任意 Python 物件（包含 dataclass）"""
        data = pickle.dumps(obj)
        self.Clear()
        self._stream.write(data)
        self._stream.seek(0)

    def ReadObject(self):
        """讀取並還原先前 WriteObject() 寫入的 Python 物件"""
        self._stream.seek(0)
        return pickle.loads(self._stream.read())


class TMemoryStream(TStream):
    """模擬 BCB5 的 TMemoryStream"""
    def __init__(self):
        super().__init__()

# ================================================================================
# [使用範例]
if(__name__=="__main__"):
    from dataclasses import dataclass

    @dataclass
    class STRU_Employee:
        mi_EMPID:    int;
        ms_EMPNAME:  str;
        ms_BIRTHDAY: str;
        ms_Weight:   float;

    obj_MemStream: TMemoryStream;
    stru_EMP1    : STRU_Employee;
    stru_EMP2    : STRU_Employee;
    stru_EMP3    : STRU_Employee;
    stru_READ    : STRU_Employee;
    
    obj_MemStream = TMemoryStream();
    stru_EMP1     = STRU_Employee(0, "劉備", "1998/01/02", 54.23);
    stru_EMP2     = STRU_Employee(1, "關羽", "2026/03/26", 74.74);
    stru_EMP3     = STRU_Employee(2, "張飛", "2028/11/18", 94.39);
    stru_READ     = STRU_Employee(-1, "", "", 0.0);
    
    obj_MemStream.Clear();
    obj_MemStream.WriteObject(stru_EMP1);
    obj_MemStream.Position = 0;
    obj_MemStream.SaveToFile("emp1.bin");

    obj_MemStream.Clear();
    obj_MemStream.WriteObject(stru_EMP2);
    obj_MemStream.Position = 0;
    obj_MemStream.SaveToFile("emp2.bin");

    obj_MemStream.Clear();
    obj_MemStream.WriteObject(stru_EMP3);
    obj_MemStream.Position = 0;
    obj_MemStream.SaveToFile("emp3.bin");


    obj_MemStream.LoadFromFile("emp2.bin");
    stru_READ = obj_MemStream.ReadObject();

    print(stru_READ.mi_EMPID);
    print(stru_READ.ms_EMPNAME);
    print(stru_READ.ms_BIRTHDAY);
    print(stru_READ.ms_Weight);
