import pytest


def test_login_success(client, users):
    response = client.post(
        "/auth/login",
        data={"login_id": "user1", "password": "password123"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "ログインしました。" in response.get_data(as_text=True)
    assert response.request.path == "/dashboard/"


def test_login_failure(client, users):
    response = client.post(
        "/auth/login",
        data={"login_id": "user1", "password": "wrong-password"},
    )

    assert response.status_code == 200
    assert "ログインIDまたはパスワードが正しくありません。" in response.get_data(
        as_text=True
    )


@pytest.mark.parametrize(
    "url",
    ["/dashboard/", "/tasks/", "/projects/", "/questions/"],
)
def test_protected_page_redirects_to_login(client, url):
    response = client.get(url)

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]
