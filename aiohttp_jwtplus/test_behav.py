def test_behav():   
    '''
    # markdown
    ## Behaviors of routing under different authorization
    path | remarks | authorized destination |  unauthorized destination
    -|-|-|-
    /index.html | Entry of main functional SPA | /index.html | /login.html
    /login.html | Entry of login page. Independent SPA | /index.html | /login.html
    /login_api  | Login api , one in jwt whitelist. | /login_api | /login_api
    /setattr_api | One of protected apis. | /setattr_api | 403 or 401
    /404        | Undefined page | /index.html | /login.html

    */\* Status code 404 handled in SPA \*/*
    '''
    pass
