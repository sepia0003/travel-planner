from flask import Blueprint, request, render_template, flash, redirect, url_for
from flask import current_app as current_app

from app.module import dbModule

test = Blueprint('test', __name__, url_prefix='/test')

@test.route('/', methods=['GET'])
def index():
    return render_template('/test/index.html', result=None, resultdata=None, resultupdate=None)

@test.route('/insert', methods=['GET'])
def insert():
    db_class = dbModule.Database()

    sql = '''
        INSERT INTO testtable(name, address)
        VALUES('insertname1', 'insertaddress1');
    '''

    db_class.execute(sql)
    db_class.commit()

    return render_template('/test/index.html', result='insert is done.', resultdata=None, resultupdate=None)

@test.route('/select', methods=['GET'])
def select():
    db_class = dbModule.Database()

    sql = '''
        SELECT id, name, address
        FROM testtable;
    '''

    listofrecords = db_class.execute_fetchall(sql)

    return render_template('/test/index.html', result='select is done.', resultdata=listofrecords[0], resultupdate=None)

@test.route('/update', methods=['GET'])
def update():
    db_class = dbModule.Database()

    sql = '''
        UPDATE testtable
        SET name = 'updatename3', address = 'updateaddress3'
        WHERE id = 1;
    '''

    db_class.execute(sql)
    db_class.commit()

    sql = '''
        SELECT id, name, address
        FROM testtable;
    '''

    listofrecords = db_class.execute_fetchall(sql)

    return render_template('/test/index.html', result='update is done.', resultdata=None, resultupdate=listofrecords[0])
