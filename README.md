# Sign-Pro
对 签到啦 重构优化等

### 重构优化思路

<img src=https://github.com/Litre-WU/Sign-Pro/blob/main/demo.png width=300/>

1.将各种类型统一结构化存入数据库中  
2.脚本只需要路由函数和结构化数据解析函数即可  
3.平台函数和账户信息可以通过接口动态添加、修改和删除  
4.脚本只需从数据库读取结构化数据通过解析函数去请求  
5.消息通知起始也是平台函数的一种，也是从数据库解析请求  


## 优化总结  

通过结构化数据将签到函数存于数据库中，一可以降低代码量、二可以不需要更新脚本就可以实现函数的增删改查...
