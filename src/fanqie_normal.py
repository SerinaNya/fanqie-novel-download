"""
作者：星隅（xing-yv）

版权所有（C）2023 星隅（xing-yv）

本软件根据GNU通用公共许可证第三版（GPLv3）发布；
你可以在以下位置找到该许可证的副本：
https://www.gnu.org/licenses/gpl-3.0.html

根据GPLv3的规定，您有权在遵循许可证的前提下自由使用、修改和分发本软件。
请注意，根据许可证的要求，任何对本软件的修改和分发都必须包括原始的版权声明和GPLv3的完整文本。

本软件提供的是按"原样"提供的，没有任何明示或暗示的保证，包括但不限于适销性和特定用途的适用性。作者不对任何直接或间接损害或其他责任承担任何责任。在适用法律允许的最大范围内，作者明确放弃了所有明示或暗示的担保和条件。

免责声明：
该程序仅用于学习和研究Python网络爬虫和网页处理技术，不得用于任何非法活动或侵犯他人权益的行为。使用本程序所产生的一切法律责任和风险，均由用户自行承担，与作者和版权持有人无关。作者不对因使用该程序而导致的任何损失或损害承担任何责任。

请在使用本程序之前确保遵守相关法律法规和网站的使用政策，如有疑问，请咨询法律顾问。

无论您对程序进行了任何操作，请始终保留此信息。
"""

# 导入必要的模块
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re


# 定义正常模式用来下载番茄小说的函数
def fanqie_n(url, encoding, user_agent):

    headers = {
        "User-Agent": user_agent
    }

    # 获取网页源码
    response = requests.get(url, headers=headers)
    html = response.text

    # 解析网页源码
    soup = BeautifulSoup(html, "html.parser")

    # 获取小说标题
    title = soup.find("h1").get_text()
    # , class_ = "info-name"

    # 获取小说信息
    info = soup.find("div", class_="page-header-info").get_text()

    # 获取小说简介
    intro = soup.find("div", class_="page-abstract-content").get_text()

    # 拼接小说内容字符串
    content = f"""使用 @星隅(xing-yv) 所作开源工具下载
开源仓库地址:https://github.com/xing-yv/fanqie-novel-download
任何人无权限制您访问本工具，如果有向您提供代下载服务者未事先告知您工具的获取方式，请向作者举报:xing_yv@outlook.com

{title}
{info}
{intro}
"""

    # 获取所有章节链接
    chapters = soup.find_all("div", class_="chapter-item")

    # 遍历每个章节链接
    for chapter in chapters:
        # 获取章节标题
        chapter_title = chapter.find("a").get_text()

        # 获取章节网址
        chapter_url = urljoin(url, chapter.find("a")["href"])

        # 获取章节 id
        chapter_id = re.search(r"/(\d+)", chapter_url).group(1)

        # 构造 api 网址
        api_url = f"https://novel.snssdk.com/api/novel/book/reader/full/v1/?device_platform=android&parent_enterfrom=novel_channel_search.tab.&aid=2329&platform_id=1&group_id={chapter_id}&item_id={chapter_id}"

        retry_count = 1
        while retry_count < 4:  # 设置最大重试次数
            # 获取 api 响应
            api_response = requests.get(api_url, headers=headers)

            # 解析 api 响应为 json 数据
            api_data = api_response.json()

            if "data" in api_data and "content" in api_data["data"]:
                chapter_content = api_data["data"]["content"]
                break  # 如果成功获取章节内容，跳出重试循环
            else:
                if retry_count == 1:
                    print(f"{chapter_title} 获取失败，正在尝试重试...")
                print(f"第 ({retry_count}/3) 次重试获取章节内容")
                retry_count += 1  # 否则重试

        if retry_count == 4:
            print(f"无法获取章节内容: {chapter_title}，跳过。")
            continue  # 重试次数过多后，跳过当前章节

        # 提取文章标签中的文本
        chapter_text = re.search(r"<article>([\s\S]*?)</article>", chapter_content).group(1)

        # 将 <p> 标签替换为换行符
        chapter_text = re.sub(r"<p>", "\n", chapter_text)

        # 去除其他 html 标签
        chapter_text = re.sub(r"</?\w+>", "", chapter_text)
        '''
        # 将 <p> 标签转换为换行符
        chapter_text = chapter_text.replace("<p>", "\n")

        # 去除 html 标签和空白字符
        chapter_text = re.sub(r"<\w+>|</\w+>|\s+", "", chapter_text)
        '''

        # 在小说内容字符串中添加章节标题和内容
        content += f"\n\n{chapter_title}\n{chapter_text}"

        # 打印进度信息
        print(f"已获取 {chapter_title}")

    # 根据编码转换小说内容字符串为二进制数据
    if encoding == "utf-8":
        data = content.encode("utf-8", errors='ignore')
    elif encoding == "gb2312":
        data = content.encode("gb2312", errors='ignore')
    else:
        print("不支持的编码")
        return

    # 定义文件名
    filename = title + ".txt"

    # 保存文件
    with open(filename, "wb") as f:
        f.write(data)

    # 打印完成信息
    print(f"已保存 {filename}")
