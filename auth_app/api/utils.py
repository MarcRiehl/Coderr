
def get_fullname(user):
    """
    Return the user's full name or a fallback based on available user data.

    Args:
        user (User): The user whose name should be retrieved.

    Returns:
        str: The user's full name, username, email prefix, or 'Unknown User'
            if no suitable user information is available.
    """
    first_name = (user.first_name or '').strip()
    last_name = (user.last_name or '').strip()

    if first_name and last_name:
        return f'{first_name} {last_name}'

    if first_name:
        return f'{first_name} User'

    if last_name:
        return f'User {last_name}'

    username = (user.username or '').strip()

    if username:
        parts = username.split()

        if len(parts) >= 2:
            return username

        return f'{username} User'

    email_name = (user.email or '').split('@')[0].strip()

    if email_name:
        return f'{email_name} User'

    return 'Unknown User'