import os
import configparser

class TIniFile:
    def __init__(self, FileName: str, Encoding: str = "byte"):
        """
        Encoding:
            "byte"    -> Big5 編碼
            "unicode" -> UTF-8 編碼
        """
        self.FileName = FileName
        self.Encoding = Encoding.lower()
        self.config = configparser.ConfigParser()
        self.config.optionxform = str  # 保留大小寫

        self._encoding_name = "big5" if self.Encoding == "byte" else "utf-8"

        if os.path.exists(self.FileName):
            self.config.read(self.FileName, encoding=self._encoding_name)

    # -----------------------
    # 讀取方法
    # -----------------------
    def ReadString(self, Section: str, Ident: str, Default: str = "") -> str:
        if self.config.has_section(Section) and self.config.has_option(Section, Ident):
            return self.config.get(Section, Ident)
        return Default

    def ReadInteger(self, Section: str, Ident: str, Default: int = 0) -> int:
        try:
            return int(self.ReadString(Section, Ident, str(Default)))
        except ValueError:
            return Default

    def ReadFloat(self, Section: str, Ident: str, Default: float = 0.0) -> float:
        try:
            return float(self.ReadString(Section, Ident, str(Default)))
        except ValueError:
            return Default

    def ReadBool(self, Section: str, Ident: str, Default: bool = False) -> bool:
        val = self.ReadString(Section, Ident, str(Default))
        return val.lower() in ['1', 'true', 'yes']

    # -----------------------
    # 寫入方法
    # -----------------------
    def WriteString(self, Section: str, Ident: str, Value: str):
        if not self.config.has_section(Section):
            self.config.add_section(Section)
        self.config.set(Section, Ident, Value)
        self._save()

    def WriteInteger(self, Section: str, Ident: str, Value: int):
        self.WriteString(Section, Ident, str(Value))

    def WriteFloat(self, Section: str, Ident: str, Value: float):
        self.WriteString(Section, Ident, str(Value))

    def WriteBool(self, Section: str, Ident: str, Value: bool):
        self.WriteString(Section, Ident, str(int(Value)))

    # -----------------------
    # 刪除 / 檢查
    # -----------------------
    def DeleteKey(self, Section: str, Ident: str):
        if self.config.has_section(Section):
            self.config.remove_option(Section, Ident)
            self._save()

    def EraseSection(self, Section: str):
        if self.config.has_section(Section):
            self.config.remove_section(Section)
            self._save()

    def ValueExists(self, Section: str, Ident: str) -> bool:
        return self.config.has_section(Section) and self.config.has_option(Section, Ident)

    # -----------------------
    # 內部保存
    # -----------------------
    def _save(self):
        with open(self.FileName, 'w', encoding=self._encoding_name) as f:
            self.config.write(f)

    # -----------------------
    # 關閉 (可選)
    # -----------------------
    def Close(self):
        self.config = None


# ================================================================================
if(__name__=="__main__"):
    # 預設 Big5
    ini = TIniFile("test.ini")
    # 或者使用 Unicode (UTF-8)
    # ini = TIniFile("test.ini", Encoding="unicode")

    ini.WriteString("User", "Name", "林大明")
    ini.WriteInteger("User", "Age", 36)

    name = ini.ReadString("User", "Name", "DefaultName")
    age = ini.ReadInteger("User", "Age", 0)

    print(name, age)
    