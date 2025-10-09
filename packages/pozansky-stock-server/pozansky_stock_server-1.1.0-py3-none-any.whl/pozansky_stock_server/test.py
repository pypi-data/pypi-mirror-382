#!/usr/bin/env python3
"""
修复版快速测试文件
"""

import asyncio
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from server import stock_analyzer, analyze_stock_multiple_intervals

async def quick_test(symbol="AAPL"):
    """快速测试单个股票"""
    print(f"🚀 快速测试 {symbol}...")
    
    try:
        # 初始化
        await stock_analyzer.initialize()
        
        # 多周期分析 - 使用正确的MCP工具函数
        print(f"\n📊 正在分析 {symbol}...")
        result = await analyze_stock_multiple_intervals(symbol)
        
        # 显示简化结果
        print(result)
        
        print(f"\n🎉 {symbol} 测试完成!")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    finally:
        await stock_analyzer.close()

async def test_multiple_stocks():
    """测试多个股票"""
    stocks = [
  
    "601318.SS", "AAPL", "GOOGL", "TSLA", "MSFT", "AMZN", "META", "NVDA", "NFLX", 
                "AMD", "INTC", "BABA", "PDD", "JD", "BAC", "JPM", "WMT", "DIS", "V", "MA"

]
    # stocks = ["JPM"]
    
    for symbol in stocks:
        print(f"\n{'='*50}")
        print(f"测试 {symbol}")
        print('='*50)
        await quick_test(symbol)

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='股票分析快速测试')
    parser.add_argument('symbol', nargs='?', default='AAPL', 
                       help='股票代码 (默认: AAPL)')
    parser.add_argument('--all', action='store_true',
                       help='测试多个股票')
    
    args = parser.parse_args()
    asyncio.run(test_multiple_stocks())

    # if args.all:
    # else:
    #     asyncio.run(quick_test(args.symbol))

if __name__ == "__main__":
    main()