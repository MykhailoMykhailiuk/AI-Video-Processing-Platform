def is_premium(user):
    if not user.is_authenticated:
        return False
    
    if hasattr(user, 'subscription'):
        return user.subscription.is_active()

    return False