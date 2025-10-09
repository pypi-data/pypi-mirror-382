from datacenter_client.tests.base import BaseClientTest
import unittest


class TestMarginSummaryClient(BaseClientTest):
    """融资融券总结客户端测试类"""
    
    def test_page_list(self):
        """测试分页获取融资融券总结"""
        print("\n" + "=" * 50)
        print("测试融资融券总结客户端 - 分页获取")
        print("=" * 50)
        
        try:
            result = self.client.margin_summary.page_list(page=1, page_size=10)
            print(f"状态: {result.status}")
            self.print_pagination_info(result)
        except Exception as e:
            print(f"测试分页获取时出错: {e}")
    
    def test_list(self):
        """测试不分页获取融资融券总结"""
        print("\n" + "=" * 50)
        print("测试融资融券总结客户端 - 不分页获取")
        print("=" * 50)
        
        try:
            result = self.client.margin_summary.list()
            print(f"状态: {result.status}")
            self.print_list_info(result)
        except Exception as e:
            print(f"测试不分页获取时出错: {e}")
    
    def test_list_with_date_range_and_exchange(self):
        """测试按日期范围和交易所不分页获取融资融券总结"""
        print("\n" + "=" * 50)
        print("测试融资融券总结客户端 - 按日期范围和交易所不分页获取")
        print("=" * 50)
        
        try:
            result = self.client.margin_summary.list(start_date="2023-01-01", end_date="2023-01-31", exchange_id="SZSE", limit=5)
            print(f"状态: {result.status}")
            self.print_list_info(result)
        except Exception as e:
            print(f"测试按日期范围和交易所不分页获取时出错: {e}")


if __name__ == "__main__":
    # 创建测试套件
    suite = unittest.TestSuite()
    
    # 添加单个测试方法
    # suite.addTest(TestMarginSummaryClient('test_page_list'))
    # suite.addTest(TestMarginSummaryClient('test_list'))
    suite.addTest(TestMarginSummaryClient('test_list_with_date_range_and_exchange'))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)