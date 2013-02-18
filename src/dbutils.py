from collections import Iterable

def iterRec(dbcon, tab, sel_fields, cond_str=None, cond_values=None):
    """
    simple query to iterate a table. 
    sel_fields:  a tuple or a list of select fields;
    cond_str: the condition string(with '?') after 'WHERE'; 
    cond_values: a tuple or list that replace '?' in condition striong 
    """
    if isinstance(sel_fields, str):
        sel_fields = sel_fields.split()
    sel_fields = ','.join(sel_fields)
    sql = 'SELECT %s FROM %s' % (sel_fields, tab)

    if cond_str: 
        sql += ' WHERE ' + cond_str
        #print 'executing sql: '+sql
    if cond_values != None and not isinstance(cond_values, Iterable):
        cond_values = (cond_values,)
    cur = None
    if cond_values != None:
        cur = dbcon.execute(sql, cond_values)
    else:
        cur = dbcon.execute(sql)

    for r in cur:
        yield r


def queryOneRec(dbcon, tab, sel_fields, cond_str=None, cond_values=None):
    """
    return only one record if exists, otherwise return  None 
    """
    for r in iterRec(dbcon,tab, sel_fields, cond_str, cond_values):
        return r

def countOfRecs(dbcon,tab, cond_str=None, cond_values=None):
    return queryOneRec(dbcon, tab, 'count(*)', cond_str, cond_values)[0]

def insert(dbcon, tab, field_map):
    vals = ','.join([ '?' for i in range(0, len(field_map)) ])
    ins_sql = 'INSERT INTO %s (%s) VALUES (%s)' % (tab, ','.join(field_map.iterkeys()), vals)
    #print 'executeing sql: ' + ins_sql
    dbcon.execute(ins_sql, field_map.values())

def updateByPK(dbcon, tab, field_dict, pk_dict):
    field_str = ','.join([k+'=?' for k in field_dict])
    pk_str = ' AND '.join([k+'=?' for k in pk_dict])
    upd_sql = 'UPDATE %s SET %s WHERE %s' % (tab, field_str, pk_str)
    #print 'excuting sql: ' + upd_sql
    dbcon.execute(upd_sql, field_dict.values() + pk_dict.values())

def delete(dbcon, tab, cond_str, cond_values):
    del_sql = 'DELETE FROM %s WHERE %s' % (tab, cond_str)
    if cond_values !=None and not isinstance(cond_values,Iterable):
        cond_values = tuple(cond_values)
    dbcon.execute(del_sql, cond_values)

def updateOrInsert(dbcon, tab, field_dict, pk_dict):
    """

    """
    pk_cond = ' AND '.join([k+'=?' for k in pk_dict.iterkeys()])
    r = queryOneRec(dbcon, tab, ['count(*)',], pk_cond, pk_dict.values())
    
    if r[0] == 0:
        for k,v in pk_dict.iteritems(): field_dict[k]=v
        insert(dbcon, tab, field_dict)
    elif r[0] == 1:
        updateByPK(dbcon,tab, field_dict,pk_dict)
    else:
        raise Exception('multiply records for %s in table %s' % 
                        (str(pk_dict),tab))

def connect_db(con_str):
    import sqlite3
    return sqlite3.connect(con_str)

def close_db(dbcon):
    dbcon.commit()
    dbcon.close()
