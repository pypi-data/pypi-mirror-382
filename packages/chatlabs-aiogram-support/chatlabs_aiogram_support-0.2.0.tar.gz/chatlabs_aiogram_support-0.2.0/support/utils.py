def get_url(
    *,
    schema: str | None,
    host: str,
    port: int | None = None,
    username: str | None = None,
    password: str | None = None,
    path: str | None = None,
) -> str:
    if password is not None:
        password = f':{password}'
    auth = (
        ''
        if username is None and password is None
        else f'{username}{password}@'
    )
    schema = '' if schema is None else f'{schema}://'
    port = '' if port is None else f':{port}'
    path = '' if path is None else f'/{path}'
    return f'{schema}{auth}{host}{port}{path}'
