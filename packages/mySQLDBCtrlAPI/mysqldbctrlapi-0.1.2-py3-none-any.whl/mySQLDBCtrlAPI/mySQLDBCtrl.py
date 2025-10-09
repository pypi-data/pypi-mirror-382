#UTF-8 #-*- coding:
# ----------------------------------------------------------------------------
# MySQL 資料庫類別: CLASS_mySQLDBCtrl
# [使用範例]:
#           ms_SQL = "SELECT * FROM ztbxtalk_reglist";
#           self.CVobj_MyQuery = self.CVobj_mySQLDBCtrl.CUF_DB_OpenSQL(
#                                     self.CVobj_Conn, ms_SQL);
#           mi_RECCNT = self.CVobj_mySQLDBCtrl.CUF_DB_RecordCount(self.CVobj_MyQuery);
#           print("Record count = "+ str(mi_RECCNT));
#           while(not self.CVobj_mySQLDBCtrl.CUF_Eof(self.CVobj_MyQuery)):
#               obj_DataSet = self.CVobj_mySQLDBCtrl.CUF_DB_FETCH(self.CVobj_MyQuery)
#               print(obj_DataSet["SADDR"], "    ", obj_DataSet["LOGIN_TIME"],
#                     obj_DataSet["IP_ADDR"], "    ", obj_DataSet["APP_NAME"]);
# ----------------------------------------------------------------------------

import os
import pymysql as Gobj_pymysql

# --------------------------------------------------------------------------------
# 資料庫字元集
class ENUM_DB_CHARSET:
    def __init__(self):
        self.cE_DBCS_ascii    = 1,  # ascii     US ASCII                        
        self.cE_DBCS_big5     = 2,  # big5      Big5 Traditional Chinese        
        self.cE_DBCS_binary   = 3,  # binary    Binary pseudo charset           
        self.cE_DBCS_cp1250   = 4,  # cp1250    Windows Central European        
        self.cE_DBCS_gb2312   = 5,  # gb2312    GB2312 Simplified Chinese       
        self.cE_DBCS_gbk      = 6,  # gbk       GBK Simplified Chinese          
        self.cE_DBCS_latin1   = 7,  # latin1    cp1252 West European 
        self.cE_DBCS_latin2   = 8,  # latin2    ISO 8859-2 Central European     
        self.cE_DBCS_latin5   = 9,  # latin5    ISO 8859-9 Turkish              
        self.cE_DBCS_latin7   = 10, # latin7    ISO 8859-13 Baltic              
        self.cE_DBCS_utf16    = 11, # utf16     UTF-16 Unicode                  
        self.cE_DBCS_utf16le  = 12, # utf16le   UTF-16LE Unicode                
        # --------------------------------------------------------------------------------
        self.cE_DBCS_utf32    = 13, # utf32     UTF-32 Unicode 
        # --------------------------------------------------------------------------------
        self.cE_DBCS_utf8mb3  = 14, # utf8mb3   UTF-8 Unicode                   
        self.cE_DBCS_utf8mb4  = 15  # utf8mb4   UTF-8 Unicode                   


# ================================================================================
#                           define mySQLDBCtrl API structure
# ================================================================================
class STRU_mySQLDBInfo:
    def __init__(self):
        self.ms_DB_HostIP = "127.0.0.1";
        self.mi_DB_Port   = 3306;
        self.ms_DB_Name   = "";
        self.ms_User      = "";
        self.ms_Password  = "";


# ================================================================================
#                               CLASS_mySQLDBCtrl 
# ================================================================================
class CLASS_mySQLDBCtrl:
    def __init__(self):
        self.CUms_DB_HostIP = '127.0.0.1';
        self.CUmi_DB_Port   = 3306;
        self.CUms_DB_Name   = '';
        self.CUms_User      = '';
        self.CUms_Password  = '';
        # ------------------------------------------------------------
        self.CVmi_qryRECCNT = 0;
        # ------------------------------------------------------------
        self.CVmsa_DBCS   = ["ascii",  "big5",    "binary",  "cp1250", \
                             "gb2312", "gbk",     "latin1",  "latin2", \
                             "latin5", "latin7",  "utf16",   "utf16le",\
                             "utf32",  "utf8mb3", "utf8mb4"];


    # ----------------------------------------------------------------------
    # 功能: 設定資料庫 Charset
    # 傳入: PmE_DB_Charset --> ENUM_DB_CHARSET 
    # 傳回: obj_Query
    # ----------------------------------------------------------------------
    def CUF_SET_Charset(self, PmE_DB_Charset):
        if(self.CUobj_Conn != None and len(PmE_DB_Charset) > 0):
            ms_SQL = "SET NAMES " + self.CVmsa_DBCS[PmE_DB_Charset[0]];
            # ----------------------------------------
            self.CUF_DB_ExecSQL(self.CUobj_Conn, ms_SQL);


    # ----------------------------------------------------------------------
    # 功能: 開啟 MySQL 資料庫
    # 傳入:
    # 傳回: obj_Query
    # ----------------------------------------------------------------------
    def CUF_OpenConnection_DBCS(self, Pms_DB_HostIP, Pmi_DB_Port, Pms_DB_Name, \
                                      Pms_User,      Pms_Password,
                                      PmE_DB_CHARSET):
        self.CUms_DB_HostIP = Pms_DB_HostIP;
        self.CUmi_DB_Port   = Pmi_DB_Port;
        self.CUms_DB_Name   = Pms_DB_Name;
        self.CUms_User      = Pms_User;
        self.CUms_Password  = Pms_Password;
        # ----------------------------------------------------------------
        try:
            self.CUobj_Conn = Gobj_pymysql.connect(
                                           host       = self.CUms_DB_HostIP,
                                           port       = self.CUmi_DB_Port,
                                           user       = self.CUms_User,
                                           password   = self.CUms_Password,
                                           db         = self.CUms_DB_Name,
                                           cursorclass= Gobj_pymysql.cursors.DictCursor);
        except:
            self.CUobj_Conn = None;
        #------------------------------------------------------------
        # 設定資料庫字元集
        self.CUF_SET_Charset(PmE_DB_CHARSET)
        #------------------------------------------------------------
        return(self.CUobj_Conn);
    # ======================================================================
    def CUF_OpenConnection(self, Pms_DB_HostIP, Pmi_DB_Port, Pms_DB_Name, \
                                 Pms_User,      Pms_Password):
        mE_DB_Charset = ENUM_DB_CHARSET();
        # ------------------------------------------------------------
        return(self.CUF_OpenConnection_DBCS(Pms_DB_HostIP, Pmi_DB_Port,  \
                                            Pms_DB_Name,   Pms_User,     \
                                            Pms_Password,                \
                                            mE_DB_Charset.cE_DBCS_utf32));
    # ======================================================================
    def CUF_DB_OpenConn(self, Pstru_mySQLDBInfo):
        self.CUobj_Conn.commit();
        return(self.CUF_OpenConnection(Pstru_mySQLDBInfo.ms_DB_HostIP,
                                       Pstru_mySQLDBInfo.mi_DB_Port,                                
                                       Pstru_mySQLDBInfo.ms_DB_Name,
                                       Pstru_mySQLDBInfo.ms_User,
                                       Pstru_mySQLDBInfo.ms_Password));


    # ----------------------------------------------------------------------
    # 功能: 開啟 Pms_SQL 資料錄
    # 傳入:
    # 傳回: obj_Query
    # ----------------------------------------------------------------------
    def CUF_DB_OpenSQL(self, Pobj_Connection, Pms_SQL):
        Pobj_Connection.commit();
        # ------------------------------------------------------------
        obj_Query = Pobj_Connection.cursor();
        # ------------------------------------------------------------
        obj_Query.execute(Pms_SQL);
        # ------------------------------------------------------------
        Pobj_Connection.commit();
        # ------------------------------------------------------------
        self.CVmi_qryRECCNT = self.CUF_DB_RecordCount(obj_Query);
        # ------------------------------------------------------------
        return(obj_Query);


    # ----------------------------------------------------------------------
    # 功能: 擷取資料錄
    # 傳入:
    # 傳回: obj_Field
    # ----------------------------------------------------------------------
    def CUF_DB_FETCH(self, Pobj_Query):
        self.CVmi_qryRECCNT = self.CVmi_qryRECCNT - 1;
        # ------------------------------------------------------------
        return(Pobj_Query.fetchone());


    # ----------------------------------------------------------------------
    # 功能: 執行 Open SQL 命令
    # 傳入:
    # 傳回: obj_Field
    # ----------------------------------------------------------------------
    def CUF_DB_ExecSQL(self, Pobj_Connection, Pms_SQL):
        obj_Query = Pobj_Connection.cursor();
        # ------------------------------------------------------------
        obj_Query.execute(Pms_SQL);
        # ------------------------------------------------------------
        Pobj_Connection.commit();
        # ------------------------------------------------------------
        return(obj_Query);


    # ----------------------------------------------------------------------
    # 功能: 取得資料錄筆數
    # 傳入:
    # 傳回: obj_Field
    # ----------------------------------------------------------------------
    def CUF_DB_RecordCount(self, Pobj_Query):
        return(Pobj_Query.rowcount);
    # ----------------------------------------------------------------------
    def CUF_DB_RECCOUNT(self, Pobj_Query):
        return(self.CUF_DB_RecordCount(Pobj_Query));


    # ----------------------------------------------------------------------
    # 功能: 執行 Open SQL 命令
    # 傳入:
    # 傳回: true: Eof
    # ----------------------------------------------------------------------
    def CUF_DB_Eof(self, Pobj_Query):
        mB_RetVal = True;
        # ------------------------------------------------
        if(self.CVmi_qryRECCNT > 0):
            mB_RetVal = False;
        # ------------------------------------------------
        return(mB_RetVal);


    # ----------------------------------------------------------------------
    # 功能: 執行 Open SQL 命令
    # 傳入:
    # 傳回: true: Eof
    #       Robj_DataSet: 資料集
    # ----------------------------------------------------------------------
    def CUF_Eof(self, Pobj_Query):
        return(self.CUF_DB_Eof(Pobj_Query));


    # ----------------------------------------------------------------------
    # 功能: 轉換字串編碼 (big5 -> utf-8)
    # 傳入:
    # 傳回: true: Eof
    #       Robj_DataSet: 資料集
    # ----------------------------------------------------------------------
    def CUF_str_utf8(self, Pobj_DataSet):
        return(str(Pobj_DataSet).encode("latin1").decode("big5"));


    # ----------------------------------------------------------------------
    # 功能: 讀取 BLOB Field
    # 傳入:
    # 傳回: true: Eof
    #       Pobj_Query: 資料集
    # ----------------------------------------------------------------------
    def CUF_GetBlobField(self, Pobj_Query, Pms_BlobFieldName, Pms_FileName):
        if(Pobj_Query):
            obj_DataSet  = Pobj_Query.fetchone();
            if(obj_DataSet is None):
                return;
            # --------------------------------------------------            
            obj_FileData = obj_DataSet[Pms_BlobFieldName];            
            # --------------------------------------------------
            with open(Pms_FileName, "wb") as obj_FP:
                obj_FP.write(obj_FileData);


    # ----------------------------------------------------------------------
    # 功能: 寫入 BLOB Field
    # 傳入:
    # 傳回: true: Eof
    #       Pobj_Query: 資料集
    # ----------------------------------------------------------------------
    def CUF_SetBlobField(self, Pobj_Query, Pms_TableName, Pms_QUERY, Pms_BlobFieldName, Pms_FileName):
        ms_SQL     :str;
        mi_FileSize:int;

        mi_FileSize = os.path.getsize(Pms_FileName);
        if(mi_FileSize > 4200000000):
            print("File over size!!");
            return;
        # --------------------------------------------------
        with open(Pms_FileName, "rb") as obj_FP:
            obj_FileData = obj_FP.read();
        # --------------------------------------------------
        ms_SQL = f"UPDATE {Pms_TableName} SET {Pms_BlobFieldName}=%s WHERE {Pms_QUERY}";  
        Pobj_Query.execute(ms_SQL, (obj_FileData,));
        # --------------------------------------------------
        self.CUobj_Conn.commit();
        

    # --------------------------------------------------------------------------------        
    # FUNC: 取得伺服主機系統日期時間
    # PIN :
    # POUT:
    # --------------------------------------------------------------------------------        
    def CUF_GetServerDateTime(self, Pms_SEPCHAR_DATE, Pms_SEPCHAR_TIME, 
                                    Pms_SEPERATOR):
        ms_DateTime = "";
        # ------------------------------------------------------------
        ms_FMT_DATE = "%Y" + Pms_SEPCHAR_DATE + "%m" + Pms_SEPCHAR_DATE + "%d";
        ms_FMT_TIME = "%H" + Pms_SEPCHAR_TIME + "%i" + Pms_SEPCHAR_TIME + "%s";
        # ------------------------------------------------------------
        ms_SQL = "SELECT CONCAT(DATE_FORMAT(CURRENT_DATE(), '"+ \
                         ms_FMT_DATE + "'), '"+ Pms_SEPERATOR + \
                         "',TIME_FORMAT(CURRENT_TIME(), '"    + \
                         ms_FMT_TIME + "'))  AS _DATETIME";
        obj_MyQuery = self.CUF_DB_OpenSQL(self.CUobj_Conn, ms_SQL);
        obj_DataSet = self.CUF_DB_FETCH(obj_MyQuery);
        # ------------------------------------------------------------
        ms_DateTime = obj_DataSet["_DATETIME"];
        # ------------------------------------------------------------
        return(ms_DateTime);        
    # --------------------------------------------------------------------------------        
    def CUF_GetServerDateTime1(self, PmB_DELIMITER):
        if(PmB_DELIMITER == True):
            ms_RetVal = self.CUF_GetServerDateTime("/", ":", " ");
        else:
            ms_RetVal = self.CUF_GetServerDateTime("", "", "");
        # ------------------------------------------------------------    
        return(ms_RetVal);
    # --------------------------------------------------------------------------------        
    def CUF_GetServerDateTime2(self):
        return(self.CUF_GetServerDateTime("", "", ""));
    # --------------------------------------------------------------------------------            
    def CUF_GetServerDate(self, Pms_DELIMITER):
        ms_DateTime = "";
        # ------------------------------------------------------------
        ms_SQL = "SELECT DATE_FORMAT(CURRENT_DATE(), " \
                "'%Y" + Pms_DELIMITER + "%m" + Pms_DELIMITER + \
                "%d') AS _DATE";
        obj_MyQuery = self.CUF_DB_OpenSQL(self.CUobj_Conn , ms_SQL);
        obj_DataSet = self.CUF_DB_FETCH(obj_MyQuery);
        # ------------------------------------------------------------
        ms_DateTime = obj_DataSet["_DATE"];
        # ------------------------------------------------------------
        return(ms_DateTime);
    # --------------------------------------------------------------------------------            
    def CUF_GetServerTime(self, Pms_DELIMITER):
        ms_DateTime = "";
        # ------------------------------------------------------------
        ms_SQL = "SELECT TIME_FORMAT(CURRENT_TIME(), " \
                        "'%H" + Pms_DELIMITER + "%i" + Pms_DELIMITER + \
                        "%s') AS _TIME";
        obj_MyQuery = self.CUF_DB_OpenSQL(self.CUobj_Conn, ms_SQL);
        obj_DataSet = self.CUF_DB_FETCH(obj_MyQuery);
        # ------------------------------------------------------------
        ms_DateTime = obj_DataSet["_TIME"];
        # ------------------------------------------------------------
        return(ms_DateTime);
               

    # --------------------------------------------------------------------------------        
    # FUNC: 日期時間計算 (相加/減 Pmi_TimeSecond)
    # PIN : Pms_DateTime   可配合使用 CUF_GetServerDateTime(...) 取得系統日期時間
    #       Pmi_TImeSecond -59 ~ +59 秒
    # POUT:
    # --------------------------------------------------------------------------------        
    def CUF_AddTime(self, Pms_DateTime, Pmi_TimeSecond):
        ms_SQL = "SELECT ADDTIME('"+ Pms_DateTime + "', "+\
                         str(Pmi_TimeSecond)+ ") AS _TIMESTR ";
        obj_MyQuery = self.CUF_DB_OpenSQL(self.CUobj_Conn, ms_SQL);
        obj_DataSet = self.CUF_DB_FETCH(obj_MyQuery);
        ms_TimeSTR  = obj_DataSet["_TIMESTR"];
        # ------------------------------------------------------------
        return(ms_TimeSTR);
        

    # --------------------------------------------------------------------------------        
    # FUNC: 將目前時間 加/減 Pmi_TimeSecond 秒
    # PIN :
    # POUT:
    # --------------------------------------------------------------------------------        
    def CUF_AddTime_Current(self, Pmi_TimeSecond):
        ms_CurrTime = self.CUF_GetServerDateTime1(True);
        ms_CurrTime = self.CUF_AddTime(ms_CurrTime, Pmi_TimeSecond);
        # ------------------------------------------------------------
        return(ms_CurrTime);


# ---------------------------------------------------------------------------
#                               使用範例
# ---------------------------------------------------------------------------
if(__name__ == '__main__'):
    Gobj_mySQLDBCtrl = CLASS_mySQLDBCtrl();
    # ------------------------------------------------------------
    Gobj_Conn = Gobj_mySQLDBCtrl.CUF_OpenConnection(Pms_DB_HostIP= "mis.XXX.biz",
                                                    Pmi_DB_Port  = 1234,
                                                    Pms_DB_Name  = "goxxxh_mis",
                                                    Pms_User     = "xxxx",
                                                    Pms_Password = "****");
# ------------------------------------------------------------
# [範例1]
#    ms_SQL = 'SELECT * From tbemployee';
#    obj_Query = Gobj_mySQLDBCtrl.CUF_DB_OpenSQL(Gobj_Conn, ms_SQL);
#    print(Gobj_mySQLDBCtrl.CUF_DB_FETCH(obj_Query));    # NEXT
#    print(Gobj_mySQLDBCtrl.CUF_DB_FETCH(obj_Query));    # NEXT
# [範例2]
#    ms_SQL = "SELECT * From tbdepartment order by DEPNO";
#    obj_Query = self.CVobj_mySQLDBCtrl.CUF_DB_OpenSQL(self.CVobj_Conn, ms_SQL);
#
    ms_SQL = """
             SELECT   tbdepartment.*, tbemployee.*
             From     tbemployee
                      INNER JOIN tbdepartment ON (
                      tbemployee.ZONE_ID = tbdepartment.ZONE_ID AND
                      tbemployee.DEPNO   = tbdepartment.DEPNO)
             WHERE    EMPID >= 10 AND EMPID <= 30
             ORDER BY EMPID
             """;
    obj_Query = Gobj_mySQLDBCtrl.CUF_DB_OpenSQL(Gobj_Conn, ms_SQL);
    mi_RECCNT = Gobj_mySQLDBCtrl.CUF_DB_RecordCount(obj_Query);
    print("Record count = "+ str(mi_RECCNT));

    for mi_c in range(1, 10):
        obj_DataSet = Gobj_mySQLDBCtrl.CUF_DB_FETCH(obj_Query);
        print(obj_DataSet["DEPNO"], "    ", obj_DataSet["DEPNAME"],
              obj_DataSet["EMPID"], "    ", obj_DataSet["EMPNAME"]);


    ms_SQL = "SELECT * FROM _def_fileservicemedia_d "\
             " WHERE FolderType=1 AND MEDIAID=1 AND BlockID=1 ";
    obj_Query = Gobj_mySQLDBCtrl.CUF_DB_OpenSQL(Gobj_Conn, ms_SQL);
    Gobj_mySQLDBCtrl.CUF_SetBlobField(obj_Query, "_def_fileservicemedia_d",
                                      "FolderType=1 AND MEDIAID=1 AND BlockID=1 ",
                                      "Media_Block", 
                                      "C:\\TEMP\\baselib.zip")


    ms_SQL = "SELECT * FROM _def_fileservicemedia_d "\
             " WHERE FolderType=1 AND MEDIAID=1 AND BlockID=1 ";
    obj_Query = Gobj_mySQLDBCtrl.CUF_DB_OpenSQL(Gobj_Conn, ms_SQL);
    Gobj_mySQLDBCtrl.CUF_GetBlobField(obj_Query, "Media_Block", "C:\\temp\\PPPKKK.zip");