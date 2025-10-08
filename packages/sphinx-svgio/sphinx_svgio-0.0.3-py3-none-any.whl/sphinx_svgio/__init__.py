
def setup(app) -> dict:
    from .svgio import setup_extension

    setup_extension(app)

    return {
        "version": "0.0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
