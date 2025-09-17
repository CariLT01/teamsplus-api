def cert_route() -> tuple[str, int]:
    d = None
    with open("server.crt", "r") as f:
        d = f.read()
    f.close()
    return d, 200