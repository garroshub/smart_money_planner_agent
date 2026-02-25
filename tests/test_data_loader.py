from app.data.loader import load_users, load_accounts, load_goals


def test_data_loaders():
    assert load_users()
    assert load_accounts()
    assert load_goals()
