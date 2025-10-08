
from .api_client_main import CrmebApiClient
from .web_client_main import CrmebWebClient

api_client = CrmebApiClient(
    main_url="https://shop.shikejk.com",
    appid="shikebot", 
    appsecret="KGJ3ShfnZmzmBRPHGxPRRspD87WzhnG5"
)
web_client = CrmebWebClient(
    main_url="https://shop.shikejk.com",
    username="as123456",
    password="admin_password"
)

products = api_client.get_product_list()

