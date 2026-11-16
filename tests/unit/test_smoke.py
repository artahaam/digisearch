from digisearch import config


def test_config_defaults():
    assert isinstance(config.VECTOR_SIZE, int)
    assert config.VECTOR_SIZE == 1024
    assert config.QDRANT_COLLECTION