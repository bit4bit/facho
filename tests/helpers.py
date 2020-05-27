
def mock_urlopen(m):
    import urllib.request
    def mock(url):
        class FakeIO:
            def read(*args):
                return "X".encode('utf-8')
        return FakeIO()
    m.setattr(urllib.request, "urlopen", mock)
