# # -*- coding:utf8 -*-
# from base import *
# # a=cli.render('''
# #    my name is {{name}}.
# #    {%- for i in [1,2,3,4,5,6,7] %}
# #     {{i}}
# #    {%- endfor %}
# # ''',{'name':"jqzhang"})
# #
# # # print(a)
# #
# #
# # dsn='mysql://root:root@localhost:3306/ferry'
# #
# # conn=cli.get_mysql_connection(dsn)
# # print(cli.mysql_query(conn,'show tables'))
# # print(cli.mysql_query(conn,'select * from test'))


# # conn=cli.get_sqlite_connection(":memory:")
# #
# # cli.sqlite_query(conn,'''
# # CREATE TABLE COMPANY(
# #    ID INT PRIMARY KEY     NOT NULL,
# #    NAME           TEXT    NOT NULL,
# #    AGE            INT     NOT NULL,
# #    ADDRESS        CHAR(50),
# #    SALARY         REAL
# # );
# # ''')

# # i="insert into COMPANY(NAME,ID,AGE) values('jqzhang','1',30)"
# # cli.sqlite_query(conn,i)
# # i="insert into COMPANY(NAME,ID,AGE) values('hello','2',35)"
# # cli.sqlite_query(conn,i)

# # sql='''
# # INSERT INTO COMPANY (`ID`,`NAME`,`AGE`,`ADDRESS`,`SALARY`)
# # VALUES
# # (1,'jqzhang',30,NULL,NULL),
# # (2,'hello',35,NULL,NULL);'''
# # cli.sqlite_query(conn,sql)
# #
# # rows=cli.sqlite_query(conn,'select * from COMPANY')
# #
# # print(cli.dict2sql('COMPANY',rows))
# #
# #
# # dsn = os.environ.get("DSN", "mysql://root:root@127.0.0.1:3306/pjm_db")
# #
# # dsn='mysql://root:root@localhost:3306/ferry'
# # conn=cli.get_mysql_connection(dsn)
# # cli.dump_mysql_data(conn,"/tmp/ferry")
# # cli.dump_mysql_ddl(conn,"/tmp/ferry")
# #
# # print(cli.get_dependencies())


# # tpl='''
# # <dl>
# #     {% for key, value in d.items() %}
# #     <dt>{{ key }}</dt>
# #     <dd>{{ value }}</dd>
# #     {% endfor %}
# # </dl>
# # '''
# #
# # d={'key1':'value1','key2':'value2'}
# # print(cli.render(tpl,globals()))


# # cli.example()
# #
# # req=cli.requests.get('https://www.baidu.com')
# # print(req.content)

# # print(cli.get_dependencies(True))

# # html=cli.requests.get("https://www.baidu.com").content
# # for i in cli.pq(html,'a','items'):
# #     print(cli.pq(i,'a','text'))


# # xml='''
# # <note>
# # <to>Tove</to>
# # <from name="xxx">Jani</from>
# # <heading>Reminder</heading>
# # <body>Don't forget me this weekend!</body>
# # </note>
# # '''
# #
# # for i in cli.pq(xml,'from','items'):
# #     print(i.attr('name'))


# # cli.example()


# # cli.get_redis()
# #
# # import dsnparse
# #
# # print(cli.parse_dsn(dsn))

# # dsn='redis://localhost:63790/0'
# # r=cli.get_redis(dsn)
# # r.set('a','b')
# # print(r.get('a'))

# # import kafka

# #

# #
# # def cc():
# #     dsn="kafka://127.0.0.1:9092/test?group_id=2&bootstrap_servers=127.0.0.1:9092"
# #     consumer=cli.get_kafka_consumer(dsn)
# #     for m in consumer:
# #         print(m)
# # import threading
# #
# # c=threading.Thread(target=cc)
# # c.setDaemon(True)
# # c.start()
# # #
# # dsn="kafka://127.0.0.1:9092/?bootstrap_servers=127.0.0.1:9092"
# #
# # p=cli.get_kafka_producer(dsn)
# # k=cli.kafka
# #
# # import time
# # for i in range(1,1000):
# #     p.send('test','xxx')
# #     time.sleep(1)


# # yaml='''
# # Section:
# #     heading: Heading 1
# #     font:
# #         name: Times New Roman
# #         size: 22
# #         color_theme: ACCENT_2
# # '''
# #
# # a=cli.yaml2json(yaml)
# # b=cli.json2yaml(a)
# # print(a)
# # print(b)

# # def server():
# #
# #     import zmq
# #
# #     context = zmq.Context()
# #     socket = context.socket(zmq.REP)
# #     socket.bind("tcp://*:5555")
# #
# #     while True:
# #         message = socket.recv()
# #         print("Received: %s" % message)
# #         socket.send("I am OK!".encode('utf-8'))
# #
# # import threading
# # svc=threading.Thread(target=server)
# # svc.setDaemon(True)
# # svc.start()
# #
# # from concurrent.futures import ThreadPoolExecutor
# #
# # import zmq
# # context = zmq.Context()
# # socket = context.socket(zmq.REQ)
# # socket.connect("tcp://localhost:5555")
# #
# # time.sleep(3)
# #
# # socket.send('Are you OK?'.encode('utf-8'))
# # response = socket.recv()
# # print("response: %s" % response)


# # cli.gen_requirements()

# # app=cli.get_flask_app()
# # from flask import request
# # app.config['SECRET_KEY']=os.urandom(24)
# # @app.route("/")
# # def hello():
# #
# #     respose= cli.get_flask_response()
# #     respose.data='xxx'
# #     respose.status=404
# #     return respose
# #
# # app.run('0.0.0.0',port=8000,debug=True)

# # states = ['New' , 'Ready', 'Waiting', 'Running','Terminated']
# # transitions = [
# #     {'trigger': 'Admitted', 'source': 'New', 'dest': 'Ready'},
# #     {'trigger': 'Dispatch', 'source': 'Ready', 'dest': 'Running'},
# #     {'trigger': 'Interrupt', 'source': 'Running', 'dest': 'Ready'},
# #     {'trigger': 'InputOutputoreventwait', 'source': 'Running', 'dest': 'Waiting'},
# #     {'trigger': 'InputOutputoreventcompletion', 'source': 'Waiting', 'dest': 'Ready'},
# #     {'trigger': 'Exit', 'source': 'Running', 'dest': 'Terminated'}]
# # flow = '''
# #   1=New
# # 2 = Ready
# #   3=        Waiting
# # 4=Running
# # 5=Terminated
# # Admitted:1->2
# # Dispatch:2 -> 4
# # Interrupt:4->2
# # InputOutputoreventwait:4->3
# # InputOutputoreventcompletion:3->2
# # Exit:4->5
# # '''
# #
# # flow = '''
# #
# # //格式如下：
# # 动作1:状态1 -> 状态2
# # 动作2:状态2 -> 状态3
# # 动作3:状态3 -> 状态4
# #
# # //举例
# # //通知member填写校招培训自评
# # NotifyMemberToFillCampusAssignment:init->WaitForMemberFillCampusAssignment
# # //member填写校招自评
# # MemberFillCampusAssignment:WaitingFillCampusAssignment->FinishFillCampusAssignment
# # //通知mentor提交校招生评价
# # NotifyMentorToFillCampusAssignment:FinishFillCampusAssignment->WaitForMentorFillCampusAssignment
# #
# # '''
# #
# # print(cli.parse_fsm_flow(flow))



# import ollama


# import pandas as pd
# import sqlite3
# import re

# def remove_special_characters(table_name):
#     # 定义需要去除的特殊字符的正则表达式模式
#     pattern = r'[^a-zA-Z_\u4e00-\u9fa5]'

#     # 使用正则表达式替换特殊字符为空字符串
#     cleaned_table_name = re.sub(pattern, '', table_name)

#     return cleaned_table_name

# conn = sqlite3.connect(':memory:')

# xls=pd.ExcelFile('/Users/junqiang.zhang/Downloads/B0BMPDRG46-US-Reviews-20240514.xlsx')


# sheet_names={}

# for sheet_name_origin in xls.sheet_names:
#   sheet_name=remove_special_characters(sheet_name_origin)
#   sheet_names[sheet_name_origin]=sheet_name
#   df = xls.parse(sheet_name_origin)

#   if df.shape[0]>1:
#     df.to_sql(sheet_name, conn, if_exists='replace', index=False)

# ddl=cli.dump_sqlite_ddl(conn,dir='')


# print(ddl)







# chat = ollama.chat(
#     # model='llama3:8b',
#     model='gemma2:9b',
#     # model='r3m8/llama3-simpo:8b',
#     # model='duckdb-nsql:7b',
#     options={'max_tokens': 4096,'top_k': 1,'top_p': 0.5,'temperature': 0.1},
#     # messages=[{'role': 'user', 'content': 'Why is the sky blue?'}],
#     messages=[
#               {'role': 'user', 'content': '你是一个sqlite3数据库专家,现在需要你帮忙写查询SQL语句'},
#               {'role': 'user', 'content': '你是一个sqlite3数据库专家,现在需要你帮忙写查询SQL语句，实现功能描述所需要执行的sql语句'},
#               {'role': 'user', 'content': '下面我给出数据库的表结构如下：'},
#               {'role': 'user', 'content': "\n".join(ddl)},
#               {'role': 'user', 'content': '请理解表结构及字段的含义,回答时保留正确表名和列名'},
#               {'role': 'user', 'content': '查询一共有多少条评论,每个星级的评论数量及占比'},
#               {'role': 'user', 'content': '你只需要输出SQL语句，无需输出解析及结果，多个SQL用$$$$进行分隔'},
#               #  {'role': 'user', 'content': '输出5星的中文评论'},
#               # {'role': 'user', 'content': '对于复杂的问题可以分解为多个sql语句'},
#               # {'role': 'user', 'content': '注意要将输出内容转化为json数组格式，不需格式化，保证可以反序列化，示例格式模板如下：'},
#               # {'role': 'user', 'content': '```[{"title":"功能描述","sql":"select column from xxx_reviews"}]```'},


#               # {'role': 'system', 'content':"\n".join(ddl)},
#               # {'role': 'user', 'content': '查询一下有多少条评论,每个星级的评论数量及占比'},
#               # {'role': 'user', 'content': '你只需要输出SQL语句，无需输出解析及结果'},
#             ],


#     stream=False,
# )


# # for chunk in chat:
# #   print(chunk['message']['content'], end='', flush=True)


# sqls=cli.jq(chat,'message,content')


# print(sqls)



# for sql in sqls.split('$$$$'):
#   # 使用正则表达式替换特殊字符为空字符串,$.*?$
#   sql=sql.strip('$.*?$')
#   if sql=='':
#     continue
#   print(sql)
#   try:
#     print( json.dumps(cli.sqlite_query(conn,sql),indent=2))
#   except Exception as e:
#     print(e)



# # print(msg)

# # import re


# # # 获取 ```这是要获取的内容``` 之间的内容

# # msg = re.findall(r"```[\s\S]+?```", msg, re.MULTILINE | re.IGNORECASE)


# # sqls = json.loads(msg[0].strip('```'))


# # ctx={}

# # for info in sqls:
# #   rows=cli.sqlite_query(conn,info.get('sql'))
# #   ctx[info['title']]=rows

# # print( json.dumps(ctx,indent=2))



