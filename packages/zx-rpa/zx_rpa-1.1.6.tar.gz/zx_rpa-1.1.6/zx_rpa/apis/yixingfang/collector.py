"""
伊性坊平台数据采集模块

提供商品数据采集、图片包下载等功能。
遵循ZX_RPA规范，每个函数不超过50行，避免硬编码。
"""

import requests
from typing import Dict, List, Optional
from pathlib import Path
from loguru import logger

from .base import YixingfangBase
from .utils import extract_bn_id, filter_price, filter_spec_string, is_authorization_error

# 常量定义 - 避免硬编码
API_BASE_URL = "https://api.360zqf.com"
IMAGE_PACKAGE_API_PATH = "/yxf/api/file/queryList"
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
SUPPORTED_ZIP_EXTENSIONS = [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"]
DOWNLOAD_TIMEOUT = 30
MAX_RETRY_COUNT = 2

# 限制对外暴露的类
__all__ = ['YixingfangCollector']


class YixingfangCollector:
    """
    伊性坊平台数据采集类

    提供商品链接采集、商品数据采集、图片包下载等功能。
    支持参数化配置，避免硬编码问题。

    公开方法（对外API）：
    - collect_product_link(product_code: str, mode: str = "s") -> str: 根据商品编号采集商品链接
    - collect_product_data(url: str, mode: str = "s") -> Dict: 采集商品数据
    - download_image_package(image_package_url: str, save_folder: str, product_code: str = None) -> str: 下载图片包
    """

    # 默认过滤配置（可通过参数覆盖）
    DEFAULT_TITLE_FILTER_KEYWORDS = {"清仓", "负责人", "备案", "私人", "厂家"}
    DEFAULT_SKU_FILTER_KEYWORDS = {"箱", "清仓"}
    DEFAULT_SKU_FILTER_PRICES = {"987.00"}
    DEFAULT_REMARK_FILTER_KEYWORDS = {"备注", "通知", "备案"}

    def __init__(self, base: YixingfangBase,
                 title_filter_keywords: Optional[set] = None,
                 sku_filter_keywords: Optional[set] = None,
                 sku_filter_prices: Optional[set] = None,
                 remark_filter_keywords: Optional[set] = None,
                 api_base_url: str = API_BASE_URL,
                 user_agent: str = DEFAULT_USER_AGENT,
                 download_timeout: int = DOWNLOAD_TIMEOUT,
                 max_retry_count: int = MAX_RETRY_COUNT):
        """
        初始化数据采集器

        Args:
            base: 伊性坊基础操作实例
            title_filter_keywords: 标题过滤关键词
            sku_filter_keywords: SKU过滤关键词
            sku_filter_prices: SKU价格过滤
            remark_filter_keywords: 备注过滤关键词
            api_base_url: API基础URL，默认使用常量
            user_agent: 用户代理字符串，默认使用常量
            download_timeout: 下载超时时间，默认60秒
            max_retry_count: 最大重试次数，默认2次
        """
        logger.debug("初始化伊性坊数据采集器")

        if not base:
            logger.debug("基础操作实例不能为空")
            raise ValueError("基础操作实例不能为空")

        self.base = base

        # 过滤配置（支持参数化）
        self.title_filter_keywords = title_filter_keywords or self.DEFAULT_TITLE_FILTER_KEYWORDS
        self.sku_filter_keywords = sku_filter_keywords or self.DEFAULT_SKU_FILTER_KEYWORDS
        self.sku_filter_prices = sku_filter_prices or self.DEFAULT_SKU_FILTER_PRICES
        self.remark_filter_keywords = remark_filter_keywords or self.DEFAULT_REMARK_FILTER_KEYWORDS

        # API配置（避免硬编码）
        self.api_base_url = api_base_url
        self.user_agent = user_agent
        self.download_timeout = download_timeout
        self.max_retry_count = max_retry_count
        
        # 页面元素定位器
        self._init_selectors()
        
        logger.debug("数据采集器初始化完成")

    def _init_selectors(self):
        """初始化页面元素定位器"""
        self.selectors = {
            'goods_title': "t:h1@@class=goodsname",
            'goods_props': "t:ul@@class=goodsprops clearfix",
            'sku_table': "#listall_ll",
            'goods_intro': "t:div@@id=goods-intro",
            'product_listall': "t:div@@id=listall",
            'product_link': "t:a@@class=nolnk entry-title"
        }

    def collect_product_link(self, product_code: str, mode: str = "s") -> str:
        """
        根据商品编号采集商品链接

        Args:
            product_code (str): 商品编号，用于搜索商品的唯一标识符
            mode (str, optional): 采集模式，'d'表示浏览器模式（适合复杂页面），'s'表示requests模式（速度更快）. Defaults to "s".

        Returns:
            str: 商品详情页链接，完整的URL地址

        Raises:
            ValueError: 当商品编号为空时
            Exception: 当采集失败或未找到商品链接时

        Example:
            >>> collector = YixingfangCollector(base)
            >>> link = collector.collect_product_link("ABC123", mode="s")
            >>> print(link)
            'https://www.yxfshop.com/product/ABC123.html'
        """
        logger.debug("开始采集商品链接，商品编号: {}", product_code)
        
        if not product_code:
            logger.debug("商品编号不能为空")
            raise ValueError("商品编号不能为空")

        try:
            # 构造搜索URL
            search_url = f"{self.base.base_url}/?gallery--n,{product_code}-wholesale.html"
            
            # 切换模式并访问页面
            self.base.switch_mode(mode)
            self.base.tab.get(search_url)
            
            # 获取商品链接
            link_element = self.base.tab.ele(self.selectors['product_link'], timeout=5)
            if not link_element:
                logger.debug("未找到商品链接元素")
                raise Exception("未找到商品链接")
                
            product_link = link_element.link
            logger.debug("采集到商品链接: {}", product_link)
            return product_link
            
        except Exception as e:
            logger.debug("采集商品链接失败: {}", str(e))
            raise Exception(f"采集商品链接失败: {str(e)}")

    def collect_product_data(self, url: str, mode: str = "s") -> Dict:
        """
        采集商品详细数据

        Args:
            url (str): 商品详情页URL，完整的商品链接地址
            mode (str, optional): 采集模式，'d'表示浏览器模式（适合复杂页面），'s'表示requests模式（速度更快）. Defaults to "s".

        Returns:
            Dict: 商品数据字典，包含以下字段：
                - title (str): 商品标题
                - product_code (str): 商品编号
                - brand (str): 品牌信息
                - weight (str): 商品重量
                - skus (List[Dict]): SKU列表，每个SKU包含规格、价格、库存等信息
                - image_package_url (str): 图片包下载链接
                - remark (str): 备注信息
                - source_url (str): 原始商品链接

        Raises:
            ValueError: 当商品URL为空时
            Exception: 当采集失败或页面解析错误时

        Example:
            >>> collector = YixingfangCollector(base)
            >>> data = collector.collect_product_data("https://www.yxfshop.com/product/ABC123.html")
            >>> print(data['title'])
            '商品名称'
            >>> print(len(data['skus']))
            5
        """
        logger.debug("开始采集商品数据，URL: {}", url)
        
        if not url:
            logger.debug("商品URL不能为空")
            raise ValueError("商品URL不能为空")

        try:
            # 切换模式并访问页面
            self.base.switch_mode(mode)
            self.base.tab.get(url)

            # 分步采集数据
            basic_info = self._get_basic_info()
            skus = self._get_sku_data(basic_info.get('weight', ''))
            image_package = self._get_image_package()
            remark = self._get_remark()

            # 组装商品数据
            product_data = self._assemble_product_data(basic_info, skus, image_package, remark, url)
            
            logger.debug("商品数据采集完成，商品编号: {}，SKU数量: {}", 
                        basic_info.get('product_code'), len(skus))
            logger.debug("商品数据: {}", product_data)
            return product_data

        except Exception as e:
            logger.debug("商品数据采集失败: {}", str(e))
            raise Exception(f"商品数据采集失败: {str(e)}")

    def _assemble_product_data(self, basic_info: Dict, skus: List,
                              image_package: str, remark: str, url: str) -> Dict:
        """
        组装商品数据

        Args:
            basic_info: 基本信息
            skus: SKU列表
            image_package: 图片包链接
            remark: 备注信息
            url: 商品URL

        Returns:
            dict: 组装后的商品数据
        """
        return {
            "商品编号": basic_info.get('product_code', ''),
            "品牌": basic_info.get('brand', ''),
            "标题": basic_info.get('title', ''),
            "来源": "伊性坊",
            "来源链接": url,
            "图片包链接": image_package,
            "备注": remark,
            "skus": skus
        }

    def _get_basic_info(self) -> Dict:
        """
        获取商品基本信息

        Returns:
            dict: 包含标题、商品编号、品牌、重量的字典

        Raises:
            Exception: 获取失败时抛出异常
        """
        logger.debug("获取商品基本信息")

        try:
            # 获取商品标题
            title_element = self.base.tab.ele(self.selectors['goods_title'])
            if not title_element:
                logger.debug("未找到商品标题元素")
                raise Exception("未找到商品标题")

            goods_title = title_element.text.strip()
            logger.debug("商品标题: {}", goods_title)

            # 检查是否为特殊商品
            if any(word in goods_title for word in self.title_filter_keywords):
                logger.debug("商品标题包含过滤关键词，跳过: {}", goods_title)
                raise ValueError(f"商品标题包含过滤关键词: {goods_title}")

            # 获取商品属性
            basic_props = self._extract_product_props()

            result = {
                'title': goods_title,
                'product_code': basic_props['product_code'],
                'brand': basic_props['brand'],  # 直接使用原始品牌数据
                'weight': basic_props['weight']
            }

            logger.debug("基本信息获取完成: {}", result)
            return result

        except Exception as e:
            logger.debug("获取商品基本信息失败: {}", str(e))
            raise

    def _extract_product_props(self) -> Dict[str, str]:
        """
        提取商品属性信息

        Returns:
            dict: 包含商品编号、品牌、重量的字典
        """
        props_element = self.base.tab.ele(self.selectors['goods_props'])
        if not props_element:
            logger.debug("未找到商品属性元素")
            raise Exception("未找到商品属性")

        props_eles = props_element.eles("t:li")
        product_code = ""
        brand = ""
        weight = ""

        for ele in props_eles:
            text = ele.text
            if "商品编号：" in text:
                product_code = text.split("：")[-1].strip()
            elif "品牌：" in text:
                brand = text.split("：")[-1].strip()
            elif "重量：" in text:
                weight = text.split("：")[-1].strip()
                # 处理重量格式：34.000 克(g) -> 34
                try:
                    weight = weight.split(" ")[0]
                    weight = str(int(float(weight)))
                except:
                    weight = "0"  # 解析失败时设置为0

        # 如果没有找到重量字段，设置为0
        if not weight:
            weight = "0"

        logger.debug("提取属性 - 编号: {}，品牌: {}，重量: {}", product_code, brand, weight)
        return {
            'product_code': product_code,
            'brand': brand,
            'weight': weight
        }

    def _get_sku_data(self, weight: str) -> List[Dict[str, str]]:
        """
        获取SKU数据

        Args:
            weight: 商品重量

        Returns:
            list: SKU数据列表

        Raises:
            Exception: 获取失败时抛出异常
        """
        logger.debug("获取SKU数据")

        try:
            sku_table = self.base.tab.ele(self.selectors['sku_table'])
            if not sku_table:
                logger.debug("未找到SKU表格")
                raise Exception("未找到SKU表格")

            sku_trs = sku_table.s_eles("t:tr")
            logger.debug("找到{}行SKU数据", len(sku_trs))

            skus = []
            for sku_tr in sku_trs:
                sku_data = self._parse_single_sku(sku_tr, weight)
                if sku_data:
                    skus.append(sku_data)

            logger.debug("有效SKU数量: {}", len(skus))

            if len(skus) == 0:
                raise ValueError("没有有效的SKU数据")

            return skus

        except Exception as e:
            logger.debug("获取SKU数据失败: {}", str(e))
            raise Exception(f"获取SKU数据失败: {str(e)}")

    def _parse_single_sku(self, sku_tr, weight: str) -> Optional[Dict[str, str]]:
        """
        解析单个SKU数据

        Args:
            sku_tr: SKU行元素
            weight: 商品重量

        Returns:
            dict: SKU数据字典，如果应该跳过则返回None
        """
        sku_tds = sku_tr.s_eles("t:td")
        if len(sku_tds) < 6:
            return None

        # 提取SKU信息
        sku_code = sku_tds[0].text.replace("货号：", "").strip()
        spec_value = sku_tds[1].text.replace("规格：", "").strip()
        sale_price = sku_tds[2].text.replace("售价：", "").strip()
        cost_price = sku_tds[3].text.replace("会员价：", "").strip()
        stock_quantity = sku_tds[5].text.replace("库存：", "").strip()

        # 处理库存
        if stock_quantity == '无货':
            stock_quantity = 0

        # 应用过滤规则
        if self._should_skip_sku(spec_value, cost_price):
            logger.debug("跳过SKU: {}", sku_code)
            return None

        # 处理数据格式
        spec_value = filter_spec_string(spec_value)
        sale_price = filter_price(sale_price)
        cost_price = filter_price(cost_price)

        return {
            "规格编号": sku_code,
            "规格值": spec_value,
            "售价": sale_price,
            "会员价": cost_price,
            "重量": weight,
            "库存": stock_quantity,
        }

    def _should_skip_sku(self, spec_value: str, cost_price: str) -> bool:
        """
        判断是否应该跳过此SKU

        Args:
            spec_value: 规格值
            cost_price: 成本价

        Returns:
            bool: 应该跳过返回True
        """
        # 检查规格关键词
        if any(word in spec_value for word in self.sku_filter_keywords):
            return True

        # 检查价格过滤
        if any(price in cost_price for price in self.sku_filter_prices):
            return True

        return False

    def _get_image_package(self) -> str:
        """
        获取图片包链接

        Returns:
            str: 图片包链接，如果没有则返回"没有图片包"
        """
        logger.debug("获取图片包链接")

        try:
            goods_intro = self.base.tab.ele(self.selectors['goods_intro'])
            if not goods_intro:
                logger.debug("未找到商品介绍区域")
                return "没有图片包"

            a_eles = goods_intro.eles("t:a")
            valid_links = []

            for a_ele in a_eles:
                img_url = a_ele.attr("href")
                if img_url and "yxfshop.com/refund/transit" in img_url:
                    valid_links.append(img_url)

            # 根据链接数量返回结果
            if len(valid_links) == 0:
                img_url = "没有图片包"
            elif len(valid_links) == 1:
                img_url = valid_links[0]
            else:
                img_url = valid_links[1]  # 取第二个链接

            logger.debug("图片包链接: {}", img_url)
            return img_url

        except Exception as e:
            logger.debug("获取图片包链接异常: {}", str(e))
            return "获取图片包链接失败"

    def _get_remark(self) -> str:
        """
        获取备注信息

        Returns:
            str: 备注信息
        """
        logger.debug("获取备注信息")

        try:
            goods_intro = self.base.tab.ele(self.selectors['goods_intro'])
            if not goods_intro:
                logger.debug("未找到商品介绍区域")
                return "获取备注信息失败"

            remark_text = ""
            for div in goods_intro.eles("t:div"):
                if any(word in div.text for word in self.remark_filter_keywords):
                    remark_text += div.text

            logger.debug("备注信息长度: {}", len(remark_text))
            return remark_text

        except Exception as e:
            logger.debug("获取备注信息异常: {}", str(e))
            return "获取备注信息失败"

    def download_image_package(self, image_package_url: str, save_folder: str,
                              product_code: str = None) -> str:
        """
        下载商品图片包文件

        Args:
            image_package_url (str): 图片包下载链接，从商品数据中获取的完整URL
            save_folder (str): 保存目录路径，文件将下载到此目录下
            product_code (str, optional): 商品编号，用于重命名下载文件，如果不提供则使用原始文件名. Defaults to None.

        Returns:
            str: 下载成功时返回完整的文件路径

        Raises:
            ValueError: 当保存目录为空时
            Exception: 当图片包链接无效、下载失败或解析失败时

        Example:
            >>> collector = YixingfangCollector(base)
            >>> file_path = collector.download_image_package(
            ...     "https://api.360zqf.com/download/ABC123.zip",
            ...     "./downloads",
            ...     "ABC123"
            ... )
            >>> print(file_path)
            './downloads/ABC123.zip'
        """
        logger.debug("开始下载图片包: {}", image_package_url[:100])

        if not image_package_url or image_package_url == "没有图片包":
            logger.debug("没有有效的图片包链接")
            raise Exception("没有图片包链接")

        if not save_folder:
            logger.debug("保存目录不能为空")
            raise ValueError("保存目录不能为空")

        try:
            # 获取Authorization
            authorization = self._get_valid_authorization()

            # 获取图片包数据
            package_data = self._get_package_data_with_retry(image_package_url, authorization)

            # 解析下载链接
            download_url = self._parse_package_data(package_data)
            if not download_url:
                logger.debug("解析下载链接失败")
                raise Exception("解析下载链接失败")

            # 下载文件
            file_path = self._download_file(download_url, save_folder, product_code)
            logger.debug("图片包下载完成: {}", file_path)
            return file_path

        except Exception as e:
            logger.debug("下载图片包失败: {}", str(e))
            raise Exception(f"下载图片包失败: {str(e)}")

    def _get_valid_authorization(self) -> str:
        """
        获取有效的Authorization

        Returns:
            str: Authorization令牌

        Raises:
            Exception: 获取失败时抛出异常
        """
        authorization = self.base.get_authorization()
        if not authorization:
            logger.debug("获取Authorization失败")
            raise Exception("获取Authorization失败")
        return authorization

    def _get_package_data_with_retry(self, package_url: str, authorization: str) -> Dict:
        """
        带重试机制获取图片包数据

        Args:
            package_url: 图片包URL
            authorization: Authorization令牌

        Returns:
            dict: 图片包数据

        Raises:
            Exception: 获取失败时抛出异常
        """
        for retry in range(self.max_retry_count):
            try:
                package_data = self._get_image_package_data(package_url, authorization)
                if package_data:
                    return package_data
                else:
                    if retry < self.max_retry_count - 1:
                        logger.debug("第{}次获取图片包数据失败，重试", retry + 1)
                        continue
                    else:
                        raise Exception("获取图片包数据失败：所有重试都失败了")
            except Exception as e:
                if "Authorization错误" in str(e) and retry < self.max_retry_count - 1:
                    logger.debug("Authorization错误，重新获取")
                    # 重新获取Authorization
                    new_authorization = self.base.get_authorization(force_refresh=True)
                    if new_authorization:
                        authorization = new_authorization
                        continue
                    else:
                        raise Exception("重新获取Authorization失败")
                else:
                    raise

        raise Exception("获取图片包数据失败")

    def _get_image_package_data(self, package_url: str, authorization: str) -> Dict:
        """
        获取商品图片包信息

        Args:
            package_url: 图片包URL
            authorization: Authorization令牌

        Returns:
            dict: 图片包数据

        Raises:
            Exception: 获取失败时抛出异常
        """
        api_url = f"{self.api_base_url}{IMAGE_PACKAGE_API_PATH}"
        userid = self.base.username

        headers = {
            "User-Agent": self.user_agent,
            "Authorization": authorization,
            "Userid": userid
        }

        # 提取bn_id
        bn_id = extract_bn_id(package_url)
        if not bn_id:
            logger.debug("提取bn_id失败")
            raise Exception("提取bn_id失败")

        # 构造请求数据
        data = {"goodsCode": str(bn_id)}

        try:
            # 发送POST请求
            res = self.base.tab.post(api_url, json=data, headers=headers)
            res_json = res.json()

            # 检查是否为Authorization错误
            if is_authorization_error(res_json):
                self.base.auth_manager.clear()
                raise Exception(f"Authorization错误: {res_json.get('msg', '身份验证失败')}")

            if res_json.get("code") != 200:
                raise Exception(f"获取图片包信息失败: {res_json.get('code')} - {res_json.get('msg', '')}")

            return res_json.get("data")
        except Exception as e:
            if "Authorization错误" in str(e):
                raise  # 重新抛出Authorization错误
            raise Exception(f"获取图片包信息失败: {str(e)}")

    def _parse_package_data(self, package_data: Dict) -> Optional[str]:
        """
        解析图片包数据，返回最新的压缩包下载链接

        Args:
            package_data: 图片包数据

        Returns:
            str: 下载链接，解析失败返回None
        """
        logger.debug("解析图片包数据")

        try:
            if not package_data or not isinstance(package_data, dict):
                logger.debug("图片包数据为空或格式错误")
                return None

            # 获取文件列表
            file_list = package_data.get('list', [])
            if not file_list:
                logger.debug("文件列表为空")
                return None

            # 过滤压缩包文件
            zip_files = self._filter_zip_files(file_list)
            if not zip_files:
                logger.debug("未找到压缩包文件")
                return None

            # 选择最合适的压缩包
            selected_zip = self._select_best_zip_file(zip_files)
            if not selected_zip:
                logger.debug("未找到合适的压缩包")
                return None

            download_url = selected_zip.get('url')
            logger.debug("选择压缩包: {}", selected_zip.get('originalName', 'Unknown'))
            return download_url

        except Exception as e:
            logger.debug("解析图片包数据异常: {}", str(e))
            return None

    def _filter_zip_files(self, file_list: List[Dict]) -> List[Dict]:
        """
        过滤出压缩包文件

        Args:
            file_list: 文件列表

        Returns:
            list: 压缩包文件列表
        """
        zip_files = []

        for file_info in file_list:
            file_name = file_info.get('originalName', '')
            if any(file_name.lower().endswith(ext) for ext in SUPPORTED_ZIP_EXTENSIONS):
                zip_files.append(file_info)

        return zip_files

    def _select_best_zip_file(self, zip_files: List[Dict]) -> Optional[Dict]:
        """
        选择最合适的压缩包文件

        Args:
            zip_files: 压缩包文件列表

        Returns:
            dict: 选中的压缩包文件信息
        """
        # 按创建时间排序，获取最新的压缩包
        sorted_zip_files = sorted(
            zip_files,
            key=lambda x: x.get('createTime', 0),
            reverse=True
        )

        # 选择压缩包，跳过包含"视频"的文件
        for zip_file in sorted_zip_files:
            file_name = zip_file.get('originalName', '')
            if "视频" in file_name:
                logger.debug("跳过包含'视频'的压缩包: {}", file_name)
                continue
            else:
                return zip_file

        # 如果所有压缩包都包含"视频"，选择最新的
        if sorted_zip_files:
            logger.debug("所有压缩包都包含'视频'关键词，选择最新的")
            return sorted_zip_files[0]

        return None

    def _download_file(self, download_url: str, save_folder: str,
                      product_code: str = None) -> str:
        """
        下载文件

        Args:
            download_url: 下载链接
            save_folder: 保存目录
            product_code: 商品编号（用于重命名）

        Returns:
            str: 下载成功时返回文件路径

        Raises:
            Exception: 下载失败时抛出异常
        """
        logger.debug("开始下载文件: {}", download_url[:100])

        # 创建保存目录
        save_path = Path(save_folder)
        save_path.mkdir(parents=True, exist_ok=True)
        logger.debug("保存目录已创建: {}", save_path)

        try:
            logger.debug("开始文件下载，目标目录: {}", save_path)

            if product_code:
                # 使用商品编号作为文件名
                logger.debug("使用商品编号重命名文件: {}", product_code)
                result = self.base.tab.download(
                    download_url,
                    save_path,
                    rename=product_code,
                    timeout=self.download_timeout,
                    show_msg=False
                )
            else:
                # 使用原文件名
                logger.debug("使用原文件名下载")
                result = self.base.tab.download(
                    download_url,
                    save_path,
                    timeout=self.download_timeout,
                    show_msg=False
                )

            logger.debug("下载操作完成，结果: {}", result[0])

            if result[0] == "success":
                file_size = Path(result[1]).stat().st_size if Path(result[1]).exists() else 0
                logger.debug("文件下载成功: {}，文件大小: {} bytes", result[1], file_size)
                return result[1]
            else:
                logger.debug("下载失败，错误信息: {}", result[1])
                raise Exception(f"下载失败: {result[1]}")

        except Exception as e:
            logger.debug("文件下载异常: {}", str(e))
            raise Exception(f"文件下载失败: {str(e)}")
