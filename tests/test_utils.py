from yaenv import utils


class TestUtils:
    """Utilities"""

    def test_is_truthy(self):
        """it can detect truthy values"""
        for val in utils._truthy:
            assert utils.is_truthy(val)
        assert not utils.is_truthy('maybe')
        assert not utils.is_truthy(None)

    def test_is_falsy(self):
        """it can detect falsy values"""
        for val in utils._falsy:
            assert utils.is_falsy(val)
        assert not utils.is_falsy('maybe')
        assert not utils.is_falsy(None)
