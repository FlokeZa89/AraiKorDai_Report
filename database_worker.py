import pymysql.cursors
from dotenv import load_dotenv
import asyncio
import os

load_dotenv()

HOST = os.getenv("HOST")
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
DATABASE = os.getenv("DATABASE")

db = pymysql.connect(host=HOST, user=USER, password=PASSWORD, database=DATABASE)
xd = db.cursor()

def getdata(disid):
    try:
        xd.execute("SELECT * FROM akd WHERE uid = '{}'".format(disid))
        geta = xd.fetchall()
        return geta
    except:
        return "false"

def gettransactioninfo(trans_id):
    xd.execute("SELECT * FROM transactions WHERE id = '{}'".format(trans_id))
    geta = xd.fetchall()
    return geta

def register(disid,disname):
    defaultpoint = 5000
    defaultrank = "m"
    defaultvertify = "n"
    defaultinven = []
    xd.execute("SELECT * FROM akd WHERE uid = '{}'".format(disid))
    geta = xd.fetchall()
    if (geta == ()):
        regissql = "INSERT INTO akd (username, uid, point, rank, verified, inventory) VALUES ('{}', '{}', '{}', '{}', '{}', '{}')".format(disname, disid, defaultpoint, defaultrank, defaultvertify, defaultinven)
        xd.execute(regissql)
        db.commit()
        rt = "true"
        return rt
    else:
        rt = "false"
        return rt

def update_point(updated_point,uid):
    updatedb = "UPDATE akd SET point = '{}' WHERE uid = '{}'".format(updated_point, uid)
    xd.execute(updatedb)
    db.commit()

def reverse_transaction(trans_id):
    transectioninfo = gettransactioninfo(trans_id)
    trans = transectioninfo[0]

    fdata = getdata(trans[2])
    cfdata = fdata[0]

    tdata = getdata(trans[3])
    ctdata = tdata[0]

    if(trans[5] == "d"):
        from_point = cfdata[3] - trans[4]
        to_point = ctdata[3] + trans[4]
        update_point(to_point,trans[3])
        update_point(from_point,trans[2])
        updatedb = "UPDATE transactions SET status = '{}' WHERE id = '{}'".format("r",trans_id)
        xd.execute(updatedb)
        db.commit()
        return "true"
    else:
        return "false"

def add_transaction(from_id, to_id, value):
    updatedb = "INSERT INTO transactions (from_id, to_id, value, status) VALUES ('{}', '{}', '{}', '{}')".format(from_id, to_id, value, "d")
    xd.execute(updatedb)
    db.commit()

def transaction(from_id,to_id,fdata,tdata,value):
    cfdata = fdata[0]
    ctdata = tdata[0]
    value = int(value)
    if (cfdata[4] == "a"):
        t_udpoint = ctdata[4] + value
        update_point(t_udpoint,to_id)
        add_transaction(from_id, to_id, value)
        return "true"
    else:
        if(value < 0 or value == 0):
            return "numerror"
        else:
            if (cfdata[3] < value):
                return "monerr"
            else:
                if(cfdata[5]=="y"):
                    f_udpoint = int(cfdata[3]) - value
                    t_udpoint = int(ctdata[3]) + value
                    update_point(f_udpoint, from_id)
                    update_point(t_udpoint,to_id)
                    add_transaction(from_id, to_id, value)
                    return "true"
                else:
                    if cfdata[5]=="d":
                        return "restricted"
                    else:
                        return "notverify"