# 问题文档

记录一些比较重要的问题

## Python模块

## 服务器

### Supervisor

- 务必使用绝对路径
    - 如果使用相对路径，只有在相对路径下的文件夹下启动supervisor的时候有效，而更新、重载是无效的
    - 而且多个配置文件如果使用相同的相对路径，会全部定向到一个日志文件，这是错误的
- BACKOFF Exited too quickly (process log may have details)
    - 根目录出错
    - 日志文件目录不存在
- 无法使用source等终端命令：使用bash -c "command"
- 不断exit status 0; not expected
    - supervisor无法处理不在前台的程序，如nohup、gunicorn设置了守护进程等
    - 多次出现是因为没有监测到前台程序不断重启

### NGINX

- **巨坑**：配置文件不能使用`;`作为注释，一定要是`#`
- host 的问题
    - 经常收到`Invalid HTTP_HOST header: '${ip}:${port}'`的错误，总的来说似乎是发过来的请求中的host不正确，但是配置NGINX并没有成功拦截下来
    - 目前仍未解决

## 数据库

### MySQL

- <span id="mysql-tzinfo">时区问题</span>
    - `Database returned an invalid datetime value. Are time zone definitions for your database installed`
        - 解决方法参考：https://blog.csdn.net/kq1983/article/details/109767343
        - 这个问题基本只有MySQL会有
        - 使用`mysql_tzinfo_to_sql`命令
            - `mysql_tzinfo_to_sql tz_dir`
                - 常用：`mysql_tzinfo_to_sql /usr/share/zoneinfo | mysql -u root -p密码 mysql`
            - `mysql_tzinfo_to_sql tz_file tz_name`
                - 常用：`mysql_tzinfo_to_sql tz_file tz_name | mysql -u root -p密码 mysql`
            - `mysql_tzinfo_to_sql --leap tz_file`
                - 常用：`mysql_tzinfo_to_sql --leap tz_file | mysql -u root -p密码 mysql`
        - 没有`mysql_tzinfo_to_sql`命令，如轻量级应用服务器安装等，直接使用sql文件
            - 下载地址：<https://dev.mysql.com/downloads/timezones.html>
                - 请注意下载与数据库对应的版本
            - 导入：`mysql -u root -p密码 mysql < 文件名称`
            - 或者使用Navicat等工具导入，非常简单
        - 最后可能需要刷新一下:`mysql -u root -p -e "flush tables;" mysql`
        - 或者重启一下：`sudo service mysql restart`
    - 时区渲染
        - 非常重要：**
          直接调用Python模型中的DateTimeField对象得到的永远是UTC时间，时区也是UTC时区，并非开启了时区就显示本地时区的**
        - 因为数据库中只存储UTC时间，所以在Python代码渲染的时候需要转换为本地时区
            - 使用`django.utils.timezone.localtime`方法
            - 表单和HTML中提供了方法进行时区转换
        - 但是非常奇怪的是，timestamp()却是本地时区的时间戳，根据调试发现，这个timestamp()
          已经不是datetime对象中的timestamp()了
            - 但是到底是如何作用的，机制是什么样还不清楚
    - 常见用法：<https://docs.djangoproject.com/zh-hans/4.0/topics/i18n/timezones/#usage>
        - 最重要的是如何将字符串转为需要的时区
            - 一定要理解`replace`和`astimezone`两者的区别，这是最大的坑
        - 如何查看所有可用时区：`zoneinfo.available_timezones()`为你的系统提供 IANA 时区的所有有效键集