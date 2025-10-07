from myproxy.client import MyProxyClient


def test_members():
    """Test public method members of MyProxyClient."""
    expected_members = [
        'caCertDir', 'changePassphrase', 'destroy', 'getDelegation',
        'getTrustRoots', 'hostname', 'info', 'locateClientCredentials',
        'logon', 'openSSLConfFilePath', 'openSSLConfig', 'parseConfig',
        'port', 'proxyCertLifetime', 'proxyCertMaxLifetime', 'put',
        'readProxyFile', 'serverDN', 'setDefaultCACertDir',
        'ssl_verification', 'store', 'writeProxyFile'
    ]
    actual_members = dir(MyProxyClient)
    for member in expected_members:
        assert member in actual_members


def test_simple():
    """Test a simple instance of MyProxyClient."""
    hostname = "example.com"
    c = MyProxyClient(hostname=hostname, caCertDir="")
    assert c.hostname == "example.com"
    assert not c.caCertDir
    assert c.proxyCertLifetime == 43200
    assert not c.serverDN
