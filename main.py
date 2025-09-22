# from langchain_openai import ChatOpenAI
# from browser_use import Agent
# import asyncio
# from dotenv import load_dotenv
# load_dotenv()

# async def main():
#     agent = Agent(
#         task="去 https://chuhaijiang.com 进入登录页面，使用 15622206473 密码 daijiahua.123 登录，注意登录页面要勾选协议按钮再点登录",
#         llm=ChatOpenAI(model="deepseek-chat", base_url='https://api.deepseek.com/v1', api_key='sk-8fda971235de424aa68a6bd12c97dcff'),
#     )
#     await agent.run()

from playwright.async_api import async_playwright
import asyncio
import os

async def main():
    # 读取 domTree.js 文件内容
    current_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(current_dir, 'domTree.js'), 'r') as f:
        js_code = f.read()

    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # 访问百度
        await page.goto('https://www.sina.com')
        
        # 执行 domTree.js 的内容
        result = await page.evaluate(js_code, { 'doHighlightElements': True })
        
        domMap = result['map']
        
        # 等待查看结果
        await asyncio.sleep(30)
        
        # 关闭浏览器
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
