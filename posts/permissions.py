from django.db.models import Q

PERMISSION_VALUES = {'none': 0, 'read': 1, 'write': 2}

def validate_permission_hierarchy_values(author_access, team_access, authenticated_access, public_access):
    errors = {}

    author = PERMISSION_VALUES.get(author_access, 0)
    team = PERMISSION_VALUES.get(team_access, 0)
    auth = PERMISSION_VALUES.get(authenticated_access, 0)
    public = PERMISSION_VALUES.get(public_access, 0)

    if team > author:
        errors['team_access'] = (f"Team access ({team_access}) cannot exceed Author access ({author_access}).")

    if auth > team:
        errors['authenticated_access'] = (f"Authenticated access ({authenticated_access}) cannot exceed Team access ({team_access}).")

    if public > auth:
        errors['public_access'] = (f"Public access({public_access}) cannot exceed Authenticated access ({authenticated_access}).")

    return errors

def get_user_permission_level(user, post):
    """
    return the highest access level from user in a post
    return: 'none', 'read', 'write'
    """
    if user.is_authenticated and (user.is_superuser or getattr(user, 'role', None) == 'admin'):
        return 'write'
    
    if post.author == user:
        return post.author_access
    
    if not user.is_authenticated:
        return post.public_access
    
    permissions = [post.public_access, post.authenticated_access]

    if getattr(user, 'team', None) and getattr(post.author, 'team', None):
        if user.team == post.author.team:
            permissions.append(post.team_access)


    return max(permissions, key=lambda x: PERMISSION_VALUES[x])

def user_can_read_post(user, post):
    """
    check if user can read a post
    """
    return get_user_permission_level(user, post) in ['read', 'write']

def user_can_edit_post(user, post):
    """
    check if user can edit a post
    """
    return get_user_permission_level(user, post) == 'write'

def get_readable_posts_query(user):
    """
    Generate Q object for filtering readable posts based on user permissions.
    """

    # Site admin and admin user role can see all posts
    if user.is_authenticated and (user.is_superuser or getattr(user, 'role', None) == 'admin'):
        return Q()  # Empty Q()- all posts
    
    # Start with public posts (everyone can see these)
    query = Q(public_access__in = ['read', 'write'])
    
    # If user is authenticated, add more permissions
    if user.is_authenticated:
        query |= Q(authenticated_access__in=['read', 'write'])
        query |= Q(team_access__in=['read', 'write'], author__team=user.team)
        query |= Q(author_access__in=['read', 'write'], author=user)
    
    return query