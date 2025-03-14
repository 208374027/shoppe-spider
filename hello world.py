import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import pandas as pd
import matplotlib.pyplot as plt
import logging

# 配置日志记录
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def scrape_amazon_data(keyword, num_pages=2):
    try:
        # 初始化浏览器驱动
        logging.debug("正在初始化 Chrome 浏览器驱动...")
        service = Service('E:\project-py\pythonProject\chromedriver.exe')  # 请替换为你的 ChromeDriver 路径
        driver = webdriver.Chrome(service=service)
        all_products = []
        for page in range(1, num_pages + 1):
            url = f"https://www.amazon.com/s?k={keyword}&page={page}"
            logging.debug(f"正在访问页面: {url}")
            driver.get(url)
            logging.debug("等待页面加载...")
            time.sleep(5)  # 等待页面加载
            products = driver.find_elements(By.CSS_SELECTOR, 'div.s-result-item')
            logging.debug(f"在第 {page} 页找到了 {len(products)} 个产品元素")
            for index, product in enumerate(products):
                try:
                    title = product.find_element(By.CSS_SELECTOR, 'span.a-size-medium.a-color-base.a-text-normal').text
                    price = product.find_element(By.CSS_SELECTOR, 'span.a-offscreen').text
                    rating = product.find_element(By.CSS_SELECTOR, 'span.a-icon-alt').text
                    reviews = product.find_element(By.CSS_SELECTOR, 'span.a-size-base.s-underline-text').text
                    all_products.append({
                        'title': title,
                        'price': price,
                        'rating': rating,
                        'reviews': reviews
                    })
                    logging.debug(f"成功提取第 {page} 页第 {index + 1} 个产品的数据")
                except Exception as e:
                    logging.warning(f"在提取第 {page} 页第 {index + 1} 个产品的数据时发生错误: {e}")
        driver.quit()
        logging.debug("浏览器驱动已关闭")
        return pd.DataFrame(all_products)
    except Exception as e:
        logging.error(f"在抓取数据时发生错误: {e}")
        return pd.DataFrame()


def generate_analysis_report(df):
    try:
        # 数据清洗
        logging.debug("开始数据清洗...")
        df['price'] = df['price'].str.replace('$', '').astype(float)
        df['rating'] = df['rating'].str.split(' ').str[0].astype(float)
        df['reviews'] = df['reviews'].str.replace(',', '').astype(int)
        logging.debug("数据清洗完成")

        # 生成分析报告
        logging.debug("正在生成选品分析报告...")
        report = {
            '平均价格': df['price'].mean(),
            '平均评分': df['rating'].mean(),
            '总评论数': df['reviews'].sum()
        }

        # 可视化分析
        logging.debug("正在生成可视化图表...")
        plt.figure(figsize=(12, 6))
        plt.subplot(1, 2, 1)
        df['price'].hist()
        plt.title('价格分布')
        plt.xlabel('价格')
        plt.ylabel('数量')

        plt.subplot(1, 2, 2)
        df['rating'].hist()
        plt.title('评分分布')
        plt.xlabel('评分')
        plt.ylabel('数量')

        plt.tight_layout()
        plt.savefig('analysis_report.png')
        logging.debug("可视化图表已保存为 analysis_report.png")

        return report
    except Exception as e:
        logging.error(f"在生成分析报告时发生错误: {e}")
        return {}


if __name__ == "__main__":
    keyword = 'smartphone'
    logging.info(f"开始抓取关键词为 {keyword} 的亚马逊数据...")
    data = scrape_amazon_data(keyword)
    if not data.empty:
        logging.info("数据抓取完成，开始生成分析报告...")
        report = generate_analysis_report(data)
        if report:
            logging.info("选品分析报告生成完成：")
            for key, value in report.items():
                print(f"{key}: {value}")
        else:
            logging.warning("选品分析报告生成失败")
    else:
        logging.warning("数据抓取失败，无法生成分析报告")
