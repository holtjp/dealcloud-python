import zeep
from zeep.wsse import username


def create_client(
    email: str, password: str, hostname: str
) -> zeep.client.Client:
    """
    Create a DealCloud Data Service client with the provided credentials.
    hostname will be the component of your site's domain before dealcloud.com.
    For example, if your site is "https://equityfirm.dealcloud.com", then your
    hostname is "equityfirm".
    """
    url = f'https://{hostname}.dealcloud.com/Services/v2/' \
        'DCDataService.svc?singleWsdl'
    token = username.UsernameToken(email, password)
    c = zeep.Client(url, token)
    return c


def bind_service(
    client: zeep.client.Client, service_name: str = 'DCDataService',
    port_name: str = 'CustomBinding_IDCDataService1'
) -> zeep.proxy.ServiceProxy:
    """
    Create a proxy to the service described by service_name and port_name from
    the client.
    """
    s = client.bind(service_name, port_name)
    return s
