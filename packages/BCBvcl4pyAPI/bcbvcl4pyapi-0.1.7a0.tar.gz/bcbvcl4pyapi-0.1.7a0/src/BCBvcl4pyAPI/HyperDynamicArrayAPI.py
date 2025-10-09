import os
import pickle
from typing import Generic, TypeVar, Optional
import pymysql
from dataclasses import is_dataclass

T = TypeVar("T")

class HyperDynamicArray(Generic[T]):
    def __init__(
        self,
        mysql_host: str,
        mysql_port: int,
        mysql_user: str,
        mysql_password: str,
        mysql_db: str,
        table_name: str = "dynamic_array_table",
        pickle_file: Optional[str] = None,
        table_type: str = "standard",  # "standard" = InnoDB, "memory" = MEMORY
        sample_element: Optional[T] = None  # 用來檢測元素型別
    ):
        self.mysql_host = mysql_host
        self.mysql_port = mysql_port
        self.mysql_user = mysql_user
        self.mysql_password = mysql_password
        self.mysql_db = mysql_db
        self.table_name = table_name
        self._count = 0

        # 初始化 table_type
        self.table_type = table_type.lower()
        if self.table_type not in ("standard", "memory"):
            raise ValueError("table_type must be 'standard' or 'memory'")

        # 自動切換 MEMORY / InnoDB
        if self.table_type == "memory":
            if sample_element is None:
                # 無法判斷元素型別，安全起見改標準 table
                print("⚠ Cannot determine element type, using standard table (InnoDB)")
                self.table_type = "standard"
            else:
                if is_dataclass(sample_element) or not isinstance(sample_element, (int, float, str)):
                    # dataclass 或任意 Python 物件 → 改 InnoDB
                    print("⚠ Dataclass / Python object not supported in MEMORY Table, switching to standard table (InnoDB)")
                    self.table_type = "standard"
                elif isinstance(sample_element, str):
                    # 字串超長也改 InnoDB
                    if len(sample_element.encode("utf-8")) > 65532:
                        print("⚠ String exceeds MEMORY Table maximum length, switching to standard table (InnoDB)")
                        self.table_type = "standard"

        # 建立 pymysql 連線
        self._conn = pymysql.connect(
            host=mysql_host,
            port=mysql_port,
            user=mysql_user,
            password=mysql_password,
            database=mysql_db,
            autocommit=True,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.Cursor
        )
        self._cursor = self._conn.cursor()

        # 建立 table
        self._create_table()

        # 如果有 pickle_file，轉入 MySQL
        if pickle_file and os.path.exists(pickle_file):
            self._load_pickle_to_mysql(pickle_file)

        # 計算元素總數
        self._cursor.execute(f"SELECT COUNT(*) FROM {self.table_name}")
        self._count = self._cursor.fetchone()[0]

    def _create_table(self):
        engine = "InnoDB" if self.table_type == "standard" else "MEMORY"
        # MEMORY Table 只能用 VARBINARY(65532)
        column_def = "LONGBLOB" if engine == "InnoDB" else "VARBINARY(65532)"
        create_sql = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            id BIGINT PRIMARY KEY AUTO_INCREMENT,
            data {column_def}
        ) ENGINE={engine};
        """
        self._cursor.execute(create_sql)

    def _load_pickle_to_mysql(self, pickle_file: str):
        with open(pickle_file, "rb") as f:
            try:
                while True:
                    item = pickle.load(f)
                    self.Add(item)
            except EOFError:
                pass

    def Add(self, value: T) -> int:
        data_blob = pickle.dumps(value)
        sql = f"INSERT INTO {self.table_name} (data) VALUES (%s)"
        self._cursor.execute(sql, (data_blob,))
        self._count += 1
        return self._count - 1

    def Count(self) -> int:
        return self._count

    def __getitem__(self, index: int) -> T:
        if index < 0 or index >= self._count:
            raise IndexError("HyperDynamicArray index out of range")
        sql = f"SELECT data FROM {self.table_name} WHERE id = %s"
        self._cursor.execute(sql, (index + 1,))
        row = self._cursor.fetchone()
        if row:
            return pickle.loads(row[0])
        else:
            raise IndexError("HyperDynamicArray index not found")

    def __setitem__(self, index: int, value: T):
        if index < 0 or index >= self._count:
            raise IndexError("HyperDynamicArray index out of range")
        data_blob = pickle.dumps(value)
        sql = f"UPDATE {self.table_name} SET data = %s WHERE id = %s"
        self._cursor.execute(sql, (data_blob, index + 1))

    def __iter__(self):
        for i in range(self._count):
            yield self[i]

    def Clear(self):
        """清空 table"""
        sql = f"TRUNCATE TABLE {self.table_name}"
        self._cursor.execute(sql)
        self._count = 0

    def Close(self):
        self._cursor.close()
        self._conn.close()
