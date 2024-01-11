import json
import keys2 


def user_credintials_selector(response_massage = False,counter = 0,user = 1):
    if  not response_massage or counter<5000:
        app = f'app_id_{user}'
        client_se= f'client_secre_{user}'
        app_id = getattr(keys2, app,None)
        client_secre = getattr(keys2,client_se,None)
        return app_id, client_secre, user
        
    else:
        new_user = user+1
        app = f'app_id_{new_user}'
        client_se= f'client_secre_{new_user}'
        app_id = getattr(keys2, app,None)
        client_secre = getattr(keys2,client_se,None)
        return app_id, client_secre, new_user
