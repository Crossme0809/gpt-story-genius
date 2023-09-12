<h1 align="center">● gpt-story-genius</h1>

<p align="center">
    <br>
    <b>StoryGenius：一款AI自动创作小说工具。</b><br><br>
    根据小说的提示词、写作风格和章节数量几分钟即可快速生成奇幻小说。并自动打包为电子书格式。<br>
</p>
<br>

![poster](https://github.com/Crossme0809/frenzy_repo/blob/main/assets/story_genius.png)
<br>


**gpt-story-genius** 是一个自动创作小说的AI，它可以在几分钟内根据用户提供的初始提示和章节数生成一整本奇幻小说，并自动打包为电子书格式。
该项目利用 **GPT-4**、**Stable Diffusion API** 和 **Anthropic API** 等一系列大模型调用组成的链来生成原创奇幻小说。<br>

此外，它还可以根据这本书创建一个原创封面，并将整本作品一次性转换为PDF或电子书格式，并且`制作成本低廉，制作一本15章的小说仅需4美元成本`，并且该工具是开源的，可以免费使用。
<br>

## 快速使用

在 Google Colab 中，只需打开笔记本，添加 API 密钥，然后按顺序运行单元即可。 </br></br>
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Crossme0809/frenzyTechAI/blob/main/gpt-author/gpt_author_v2.ipynb)

在笔记本的最后一个单元格中，您可以自定义小说的提示和章节数。例如：

```python
prompt = "一个被遗忘的小岛，上面有一座古老的灯塔。当灯塔亮起时，岛上的生物就会发生奇异的变化。"
num_chapters = 10
writing_style = "紧张刺激，类似于青少年恐怖小说。有很多对话和内心独白"
novel, title, chapters, chapter_titles = write_fantasy_novel(prompt, num_chapters, writing_style)
```

这将根据给定的提示生成一本 10 章的小说。**注意——少于 7 章的提示往往会导致问题。**

## 本地部署

- 下载项目代码
```bash
git clone https://github.com/Crossme0809/gpt-story-genius.git
```

- 复制项目配置文件
```bash
cp .env.example .env
```

- 配置GPT Key
```bash
# OpenAI 接口代理地址，（可选配置）
OPENAI_API_BASE="your-openai-proxy-url"

# * 配置你的 OpenAI key（建议使用GPT-4正式账号，临时账号有每分钟3次请求限制）
OPENAI_API_KEY="your-openai-api-key"

# * 生成小说封面，具体可访问 https://platform.stability.ai/ 地址申请key
STABILITY_API_KEY="your-stablity-api-key"

# 配置你的 Claude2 API Key（可选配置）
ANTHROPIC_API_KEY="your-anthropic-api-key"
```

- 安装项目依赖
```bash
pip install -r requirements.txt
```

- 启动项目
```bash
gradio run.py
```

- 后台进程启动
```bash
nohup gradio run.py > log.txt 2>&1 &
```

启动成功后，访问8000端口即可打开 **StoryGenius** 项目主页，如需要修改端口，只需要编辑 `run.py` 最后一行中的 `server_port` 即可。
<br><br>
<p>生成完的小说Epub文可以下载其文件并在 https://www.fviewer.com/view-epub 上查看，或将其安装在 Kindle 等上。（Mac上直接预览）</p>

![poster](https://github.com/Crossme0809/frenzy_repo/blob/main/assets/novel_epub.png)

## 特别说明

本项目基于[gpt-author](https://github.com/mshumer/gpt-author)开发，由[@mattshumer_](https://twitter.com/mattshumer_)创建。

