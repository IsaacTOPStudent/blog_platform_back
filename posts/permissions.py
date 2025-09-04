

def user_can_read_post(user, post):
    if user.is_superuser or (user.is_authenticated and user.role == 'admin'):
        return True
    
    if post.read_permission == 'public':
        return True 
    
    elif post.read_permission == 'authenticated' and user.is_authenticated:
        return True
    elif post.read_permission == 'team' and user.is_authenticated and user.team == post.author.team:
        return True
    elif post.read_permission == 'author' and user == post.author:
        return True
    
    return False


def user_can_edit_post(user, post):
    if user.is_superuser or (user.is_authenticated and user.role == 'admin'):
        return True
    
    if post.edit_permission == 'public':
        return True 
    
    elif post.edit_permission == 'authenticated' and user.is_authenticated:
        return True
    elif post.edit_permission == 'team' and user.is_authenticated and user.team == post.author.team:
        return True
    elif post.edit_permission == 'author' and user == post.author:
        return True
    
    return False