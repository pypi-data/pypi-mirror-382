# ops_channel


API 说明：

```
        # from ops_channel import cli #导入包


        ##### 内置工具函数　#####
        # cli.id() #获取机器标识（uuid） 与  cli.get_machine_id() 相同
        # cli.get_machine_id() #获取机器标识（uuid）
        # cli.ip() #获取本机ip
        # cli.check_port(80,'127.0.0.1') #检查端口是否开启
        # cli.get_hostname() #获取本机主机名
        # cli.get_all_ip_list() #返回本机所有ip
        # cli.json_encode(data) #json编码
        # cli.json_decode(data) #json解码


        ##### 日期　#####
        # cli.date() #当时日期
        # cli.time() #当前时间
        # cli.now() #当前日期时间


        ##### 网络　#####
        # cli.get_server_uri('help') # 返回cli服务器url
        # cli.get('http://www.bb.com',timeout=2) #get获取网页，返回网页内容，注意错误处理
        # cli.post('http://test.web.com',{'name':'jqzhang'},timeout=2) #post获取网页 返回网页内容，注意错误处理

        #####  日志　#####
        # cli.log.info('message')  #打印提示日志
        # cli.log.error('message')  #打印错误日志

        #####  字符串与shell 　#####
        # cli.execute('hostname',timeout=2) #执行命令
        # cli.join(['a','b','c'],sep=',') #数组并接，返回字符串
        # cli.jq({'data':{'rows':[{'id':1,'name':'hello'},{'id':2,'name':'world'}]}},'data,rows') #json 获取
        # cli.match('hello123world456','\d+') #正则匹配，返回数组
        # cli.split('hello123world456','\d+') #正则分割，返回数组
        # cli.getopt("cli api -u root --sudo 1 --token abc -c 'hostname' -t 5 ") #命令行参数获取，返回字典
        # cli.rand() #随机数，返回浮点数
        # cli.randint(1,100) #随机数，两者之间
        # cli.randstr(20) #随机字符串
        # cli.format('sadf {name} xxx',{'name':'jqzhang'}) #格式化，入参数为(str,dict) 返回字符串
        # print( cli.execute( cli.format('echo "{json}"|cli jq -k count',{'json':data},is_shell_str=True))) #python 与 shell交互

        #####  cli数据接口　#####
        # cli.report({'data':{'name':'jqzhang','group':'devops'},'queue':'redis','topic':'test'}) #上报信息到redis
        # cli.get_report({'topic':'test'}) #获取上报信息
        # cli.addobjs({'o':'test','d':{'name':'jqzhang'},'w':{'name':'hello'}}) #增加对象到mongo  o:表名 d:数据 w:条件
        # cli.getobjs({'o':'test','q':{'name':'jqzhang'},'c':'name,address','limit':'10'}) #增加对象到mongo  o:表名 q:查询条件 c:返回列名  limit:返回行数

        #####  cli通用命令行　#####
        #　说明：凡是能在shell中运行的cli用命令行的都可以通过 cli.xxx({}) 的方式进行调用
        #  举例：　shell：cli check -i 10.1.14.32    python: cli.check({'i':'10.1.14.32'})
```