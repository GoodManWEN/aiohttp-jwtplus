def test_behav():   
    '''
    五类测试页面
    
    1、@routes.get('/index.html')
    spa主页面
    
    2、@routes.get('/login.html')
    spa登录页面，独立

    3、@routes.get('/login')
    登录请求api，处于白名单中，会执行jwt验证，但不会影响路由行为
    
    4、@routes.get('/setattr')
    受保护的api

    5、@routes.get('/404')
    未定义的页面

    其应表现出的路由结果：
        logined         unauthorized
    1   index.html      login.html
    2   index.html      login.html
    3   /login正常逻辑   /login正常逻辑
    4   api正常逻辑      401
    5   index.html      login.html   
    '''
    pass