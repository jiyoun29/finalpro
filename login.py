# login.py
def login_user(account_id, user_df):
    user = user_df[user_df['ACCOUNT_ID'] == account_id]
    if not user.empty:
        return user.iloc[0]
    return None
