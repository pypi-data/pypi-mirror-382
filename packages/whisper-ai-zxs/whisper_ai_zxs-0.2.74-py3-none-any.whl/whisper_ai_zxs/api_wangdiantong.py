import time
import hashlib
import json
import requests
from urllib.parse import urlencode
import pandas as pd

class APIWangDianTong:
    def __init__(self):
        """
        :param sid: 卖家账号
        :param appkey: 接口账号
        :param appsecret: 接口密钥
        :param env: 'prod' 正式环境, 'sandbox' 测试环境
        """
        self.sid = "szzxs2"
        self.appkey = "szzxs2-gwa"
        self.appsecret = "2e1191428410c12ea69ad068268ffe8f"
        self.env = 'prod'
        self.base_url = {
            'prod': 'https://api.wangdian.cn/openapi2/',
            'sandbox': 'https://sandbox.wangdian.cn/openapi2/'
        }[self.env]

    def _get_timestamp(self):
        # 旺店通要求北京时间1970-01-01 08:00:00起的总秒数
        return int(time.time())

    def _sign(self, params):
        """
        旺店通标准API签名算法
        """
        items = sorted(params.items())
        sign_str = ""
        for idx, (k, v) in enumerate(items):
            k_utf8_len = len(k.encode('utf-8'))
            v_utf8_len = len(str(v).encode('utf-8'))
            k_len_str = f"{k_utf8_len:02d}"
            v_len_str = f"{v_utf8_len:0>4d}" if v_utf8_len < 10000 else str(v_utf8_len)
            part = f"{k_len_str}-{k}:{v_len_str}-{v}"
            if idx != len(items) - 1:
                part += ";"
            sign_str += part
        sign_str += self.appsecret
        return hashlib.md5(sign_str.encode('utf-8')).hexdigest()

    def _post(self, service_name, biz_params):
        """
        :param service_name: 接口服务名
        :param biz_params: 业务参数(dict)
        :return: 响应json
        """
        url = self.base_url + service_name
        timestamp = self._get_timestamp()
        params = {
            'sid': self.sid,
            'appkey': self.appkey,
            'timestamp': timestamp,
        }
        # 业务参数需json序列化
        for k, v in biz_params.items():
            if isinstance(v, (dict, list)):
                # 使用ensure_ascii=True确保所有字符为ASCII，避免签名错误
                params[k] = json.dumps(v, ensure_ascii=True)
            else:
                # 对字符串类型参数进行utf-8编码处理
                if isinstance(v, str):
                    params[k] = v.encode('utf-8').decode('utf-8')
                else:
                    params[k] = v
        # 生成签名
        params['sign'] = self._sign(params)
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = urlencode(params)
        resp = requests.post(url, data=data, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.json()

    # 创建订单接口
    def create_trade(self, file_path):
        """
        创建订单（sales_trade_push.php）。
        :param file_path: 订单数据文件路径，格式参考接口文档
        :return: 接口响应json
        """
        # 读取Excel文件
        df = pd.read_excel(file_path, engine="openpyxl")

        # 假设Excel包含如下字段：店铺名称	原始单号	收件人	省	市	区	手机	固话	邮编	地址	发货方式	应收合计	邮费	优惠金额	COD买家费用	下单时间	付款时间	买家备注	客服备注	发票抬头	发票内容	支付方式	商家编码	货品数量	货品价格	货品总价	货品优惠	源子订单号	备注	分销商, 等
        # 需根据实际Excel字段进行映射
        # 按原始单号（tid）分组，将同一订单的货品合并到 order_list
        trades = {}
        #重复的tid列表
        duplicate_tids = []
        for i, row in df.iterrows():
            tid = str(row['原始单号'])
            order_item = {
                'oid': "AIOID" + str(int(time.time())) + str(i),
                'num': int(row['货品数量']),
                'price': float(row['货品价格'])+float(row['货品优惠']),
                'status': 30,  # 10-待付款
                'refund_status': 0,
                'goods_id': row['商家编码'],
                'spec_no': row['商家编码'],
                'goods_name': row['商家编码'],
                'adjust_amount': 0,
                'discount': row['货品优惠'] if pd.notna(row['货品优惠']) else 0,
                'share_discount': 0
            }
            if tid not in trades:
                # 这里需要查询tid订单是否已经存在。
                if any(d['tid'] == tid for d in duplicate_tids):
                    print(f"订单 {tid} 在历史订单中已经出现，跳过创建。")
                    continue
                if self._check_order_tid(tid):
                    print(f"订单 {tid} 已存在，跳过创建。")
                    duplicate_tids.append({'tid': tid, 'shop_name': row['店铺名称']})
                    continue

                trades[tid] = {
                    'tid': tid,
                    'shop_name': row['店铺名称'],
                    'trade_status': 30,
                    'delivery_term': 4, # 1:款到发货,2:货到付款(包含部分货到付款),3:分期付款,4:挂账
                    'trade_time': row['下单时间'] if pd.notna(row['下单时间']) else time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
                    'pay_time': row['付款时间'] if pd.notna(row['付款时间']) else time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
                    'fenxiao_nick': row['分销商'] if pd.notna(row['分销商']) else '',
                    'buyer_nick': row['网名'] if pd.notna(row['网名']) else '',
                    'receiver_name': row['收件人'],
                    'receiver_province': row['省'] if pd.notna(row['省']) else '',
                    'receiver_city': row['市'] if pd.notna(row['市']) else '',
                    'receiver_district': row['区'] if pd.notna(row['区']) else '',
                    # 处理地址字段：省、市、区字样后加空格，并用空格隔开
                    'receiver_address': (
                        str(row['地址'])
                        .replace('省', '省 ')
                        .replace('市', '市 ')
                        .replace('区', '区 ')
                        .replace('县', '县 ')
                    ),
                    'receiver_mobile': row['手机'],
                    'post_amount': row['邮费'] if pd.notna(row['邮费']) else 0,
                    "cod_amount": 0,
                    "ext_cod_fee": 0,
                    "other_amount": 0,
                    "paid": 0,
                    'order_list': []
                    # 可根据接口文档补充其他字段
                }
            trades[tid]['order_list'].append(order_item)
        trade_data_list = list(trades.values())

        #return trade_data_list

        shops = self.get_shops()

        # 按shop_name分组
        shop_trades = {}
        results = []
        for trade in trade_data_list:
            shop_name = trade.get('shop_name', '')
            shop_trades.setdefault(shop_name, []).append(trade)
        for shop_name, trades in shop_trades.items():
            # 根据shop_name查找对应的shop_no
            shop_no = ''
            for shop in shops:
                if shop.get('shop_name') == shop_name:
                    shop_no = shop.get('shop_no')
                    break

            # 按50条分批推送
            batch_size = 50
            for start in range(0, len(trades), batch_size):
                batch_trades = trades[start:start + batch_size]
                params = {
                    'shop_no': shop_no,
                    'switch': 0,
                    'trade_list': batch_trades
                }
                print(f"Creating trades for shop: {shop_name} (shop_no: {shop_no}), batch {start // batch_size + 1}, number of trades: {len(batch_trades)}")
                print(f"Params: {json.dumps(params, ensure_ascii=False)}")
                result = self._post('trade_push.php', params)
                #if result.get('error_count') != 0:
                #    results.append({'shop_name': shop_name, 'result': result})
                results.append({'shop_name': shop_name, 'result': result})

        #把duplicate_tids也加入结果中
        duplicate_results = []
        for tid_info in duplicate_tids:
            tid = tid_info.get('tid', '')
            shop_name = tid_info.get('shop_name', '')
            duplicate_results.append({'shop_name': shop_name, 'result': f"订单 {tid} 在历史订单中已经出现，跳过创建。"})

        return results
    
    # 订单tid校验接口
    def _check_order_tid(self, order_tid):
        """
        确认tid是否已经创建了订单。
        :param order_tid: 订单编号（原始单号）
        :return: 是否存在该订单
        """
        if not order_tid:
            raise ValueError("必须提供订单编号")

        params = {'src_tid': order_tid}
        result = self._post('sales_trade_query.php', params)

        trades = result.get('trades', []) if result else []

        if not trades:
            return False
        return True

    def get_shops(self, page_size=100):
        """
        获取店铺列表（shop.php），自动分页，查询全量数据。
        :param page_size: 每页返回的数据条数，最大100
        :return: 店铺信息列表
        """
        all_shops = []
        page_no = 0
        while True:
            params = {
                'page_no': page_no,
                'page_size': page_size,
                'is_disabled': '0'
            }
            result = self._post('shop.php', params)
            shops = result.get('shoplist', []) if result else []
            all_shops.extend(shops)
            # 如果返回数量小于page_size，说明已到最后一页
            if len(shops) < page_size:
                break
            page_no += 1
        return all_shops
    # 订单查询接口
    def get_trade_by_order_and_logistics(self, order_no=None, logistics_no=None):
        """
        根据订单编号或物流单号查询订单信息（sales_trade_query.php）。
        :param order_no: 订单编号（可为系统订单编号或原始单号）
        :param logistics_no: 物流单号
        :return: 订单信息列表（只包含部分字段）
        """
        if not order_no and not logistics_no:
            raise ValueError("必须提供订单编号或物流单号")
        # 优先用订单编号查询
        if order_no:
            params = {'trade_no': order_no}
            result = self._post('sales_trade_query.php', params)
            # 如果未查到，尝试用原始单号查询
            if (not result.get('trades')) or (result.get('code') != 0):
                params = {'src_tid': order_no}
                result = self._post('sales_trade_query.php', params)
        else:
            # 用物流单号查询
            params = {'logistics_no': logistics_no}
            result = self._post('sales_trade_query.php', params)

        trades = result.get('trades', []) if result else []
        fields = [
            'src_tids', 'trade_status', 'refund_status', 'trade_time',
            'receiver_name', 'receiver_area', 'receiver_address', 'logistics_no',
            'receiver_mobile', 'logistics_name', 'goods_list'
        ]
        goods_fields = ['goods_name', 'spec_name', 'num']
        trade_status_map = {
            "5": "已取消",
            "10": "待付款",
            "12": "待尾款",
            "13": "待选仓",
            "15": "等未付",
            "16": "延时审核",
            "19": "预订单前处理",
            "20": "前处理(赠品，合并，拆分)",
            "21": "委外前处理",
            "22": "抢单前处理",
            "25": "预订单",
            "27": "待抢单",
            "30": "待客审",
            "35": "待财审",
            "40": "待递交仓库",
            "45": "递交仓库中",
            "50": "已递交仓库",
            "53": "未确认",
            "55": "已确认（已审核）",
            "90": "发货中",
            "95": "已发货",
            "105": "部分打款",
            "110": "已完成",
            "113": "异常发货"
        }
        refund_status_map = {
            "0": "无退款",
            "1": "申请退款",
            "2": "部分退款",
            "3": "全部退款",
            "4": "未付款关闭或手工关闭"
        }
        filtered_trades = []
        for trade in trades:
            filtered_trade = {k: trade.get(k) for k in fields}
            # 映射trade_status为中文
            status = str(filtered_trade.get('trade_status')) if filtered_trade.get('trade_status') is not None else ""
            filtered_trade['trade_status'] = trade_status_map.get(status, status)
            # 映射refund_status为中文
            refund_status = str(filtered_trade.get('refund_status')) if filtered_trade.get('refund_status') is not None else ""
            filtered_trade['refund_status'] = refund_status_map.get(refund_status, refund_status)
            if 'goods_list' in filtered_trade and isinstance(filtered_trade['goods_list'], list):
                filtered_trade['goods_list'] = [
                    {gk: goods.get(gk) for gk in goods_fields}
                    for goods in filtered_trade['goods_list']
                ]
            if 'src_tids' in filtered_trade:
                filtered_trade['order_id'] = filtered_trade.pop('src_tids')

            filtered_trades.append(filtered_trade)
        return filtered_trades
    
    # 可根据实际接口文档继续添加其他接口方法
    def get_stockout_order_status(self, order_no):
        """
        根据订单编号查询销售出库单状态，兼容系统订单编号和原始单号（自动识别）
        仅返回订单状态、出库状态、发货时间、截停原因、物流单号、退款状态。
        :param order_no: 订单编号（可为系统订单编号或原始单号）
        :return: dict
        """
        # 先用系统订单编号查询
        params = {
            'src_order_no': order_no
        }
        result = self._post('stockout_order_query_trade.php', params)
        # 如果未查到，尝试用原始单号查询（同样带时间参数）
        if (not result.get('stockout_list')) or (result.get('code') != 0):
            params = {
                'src_tid': order_no
            }
            result = self._post('stockout_order_query_trade.php', params)

        # print(result)
        # 提取需要的字段
        info = {}
        if result.get('stockout_list') and isinstance(result['stockout_list'], list) and len(result['stockout_list']) > 0:
            order = result['stockout_list'][0]
            refund_status_map = {
                "0": "无退款",
                "1": "申请退款",
                "2": "部分退款",
                "3": "全部退款"
            }
            stockout_status_map = {
                "5": "已取消",
                "48": "未确认",
                "50": "待审核",
                "52": "待推送",
                "53": "同步失败",
                "54": "获取面单号",
                "55": "已审核",
                "95": "已发货",
                "100": "已签收",
                "105": "部分打款",
                "110": "已完成",
                "113": "异常发货",
                "115": "回传失败",
                "120": "回传成功"
            }
            info = {
                '出库单状态': stockout_status_map.get(order.get('status'), order.get('status')),
                '发货时间': order.get('consign_time'),
                '物流公司': order.get('logistics_name'),
                '物流单号': order.get('logistics_no'),
                '退款状态': refund_status_map.get(order.get('refund_status'), "未知"),
            }
        return info

    def get_selling_suites_goods_info(self, suite_no):
        """
        获取所有在售组合装商品信息，自动翻页，拉取全部数据
        :return: 商品信息列表
        """
        all_goods = []
        #再追加查询组合装商品信息，并和售卖商品合并
        # 查询组合装商品信息并合并
        suite_page_no = 0
        suite_page_size = 100
        while True:
            suite_params = {
                'suite_no': suite_no,
                'page_no': suite_page_no,
                'page_size': suite_page_size,
                'deleted': 0,
                # 可根据需要添加时间参数，如最近30天
                # 'start_time': '2020-01-01 00:00:00',
                # 'end_time': '2020-01-30 23:59:59',
            }
            suite_result = self._post('suites_query.php', suite_params)
            suites = suite_result.get('suites', []) if suite_result else []
            all_goods.extend(suites)
            total_count = int(suite_result.get('total_count', 0)) if suite_page_no == 0 else None
            if not suites or (total_count is not None and len(all_goods) >= total_count):
                break
            suite_page_no += 1
        # 只保留每个记录中的 suite_no、suite_name、specs_list 字段
        all_goods = [
            {
            '组合装商品编码': item.get('suite_no'),
            '组合装名称': item.get('suite_name'),
            '组合装包含商品': [
                {
                    '产品名称': spec.get('goods_name'),
                    '规格名称': spec.get('spec_name'),
                    '商品编码': spec.get('spec_no'),
                    '数量': spec.get('num')
                }
                for spec in (item.get('specs_list') or [])
            ],
            '零售价': item.get('retail_price'),
            }
            for item in all_goods
        ]
        return all_goods

    def sales_refund_push_not_signed(self, src_id, reason):
        """
        针对未签收订单进行退款处理（sales_trade_refund.php）
        :param src_id: 订单编号（系统订单编号）
        :param reason: 退款原因
        :return: dict
        """        
        order_detail = self._get_trade_detail_by_order(src_id)
        if not order_detail or not order_detail[0]:
            raise ValueError(f"未找到订单信息，无法创建退款单，订单号：{src_id}")
        order_info = order_detail[0]

        goods_list = order_info.get('goods_list', [])
        order_list = [
            {
                'oid': goods.get('src_oid'),
                'num': goods.get('num')
            }
            for goods in goods_list
        ]
        params = {
            'api_refund_list': [
            {
                'platform_id': order_info.get('platform_id'),
                'shop_no': order_info.get('shop_no'),
                'tid': order_info.get('src_tids'),
                'refund_no': "AITK" + str(int(time.time())),
                'type': 3,  # type=1：退款(未发货退款)；type=2：退款不退货；type=3：退货
                'status': 'wait_seller_agree',  # wait_seller_agree-等待卖家同意, refund_success-退款成功, refund_closed-退款关闭
                'refund_time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
                'reason': reason,
                'order_list': order_list
            }
            ]
        }
        result = self._post('sales_refund_push.php', params)
        return result
    
    # 订单基本信息查询，用于创建退款单时获取订单信息
    def _get_trade_detail_by_order(self, order_no):
        """
        根据订单编号或物流单号查询订单信息（sales_trade_query.php）。
        :param order_no: 订单编号（可为系统订单编号或原始单号）
        :return: 订单信息列表（只包含部分字段）
        """
        # 优先用订单编号查询
        params = {'trade_no': order_no}
        result = self._post('sales_trade_query.php', params)
        # 如果未查到，尝试用原始单号查询
        if (not result.get('trades')) or (result.get('code') != 0):
            params = {'src_tid': order_no}
            result = self._post('sales_trade_query.php', params)

        trades = result.get('trades', []) if result else []
        fields = [
            'platform_id', 'shop_no', 'src_tids', 'goods_list'
        ]
        goods_fields = ['src_oid', 'num']
        filtered_trades = []
        for trade in trades:
            filtered_trade = {k: trade.get(k) for k in fields}
            if 'goods_list' in filtered_trade and isinstance(filtered_trade['goods_list'], list):
                filtered_trade['goods_list'] = [
                    {gk: goods.get(gk) for gk in goods_fields}
                    for goods in filtered_trade['goods_list']
                ]

            filtered_trades.append(filtered_trade)
        return filtered_trades

# 使用示例
# api = WangDianTongAPI(sid='xxx', appkey='xxx', appsecret='xxx', env='prod')
# result = api.get_trade_list(start_time='2024-01-01 00:00:00', end_time='2024-01-02 00:00:00')
# print(result)