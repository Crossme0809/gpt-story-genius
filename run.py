
import gradio as gr
from write_story import write_fantasy_novel
from author import create_cover_image
from author import create_epub
from config import anthropic_api_key

if anthropic_api_key != "YOUR ANTHROPIC API KEY":
    claude_true = True
else:
    claude_true = False


def generate_novel(prompt, num_chapters, writing_style, model_name):
    # 调用GPT和Claude API，生成小说结果
    # prompt = "A kingdom hidden deep in the forest, where every tree is a portal to another world."
    # num_chapters = 2
    # writing_style = "Clear and easily understandable, similar to a young adult novel. Lots of dialogue."
    # model_name = "gpt-3.5-turbo-16k"
    if not prompt or not writing_style:
        raise gr.Error("提示词和写作风格是必填项")
    if num_chapters < 1:
        raise gr.Error("章节数必须大于等于1")

    num_chapters = int(num_chapters)
    novel, title, chapters, chapter_titles = write_fantasy_novel(prompt,
                                                                 num_chapters, writing_style, claude_true, model_name)

    # 用chapter_titles中的正文取代章节说明
    for i, chapter in enumerate(chapters):
        chapter_number_and_title = list(chapter_titles[i].keys())[0]
        chapter_titles[i] = {chapter_number_and_title: chapter}

    # 生成小说的封面
    image_url = create_cover_image(str(chapter_titles))
    print(f"Image URL: {image_url}")

    # 生成小说 EPUB 文件
    file_url = create_epub(title, 'AI', chapter_titles, image_url)
    print(f"Novel URL: {file_url}")

    # novel, file_path = write_fantasy_novel(prompt, num_chapters, writing_style)
    return { "image_url": image_url, "file_url": file_url }


def generate_output(prompt, num_chapters, writing_style, model_name):
    try:
        output = generate_novel(prompt, num_chapters, writing_style, model_name)
        print(output)
        return (output["image_url"], output["file_url"])
    except Exception as e:
        raise gr.Error({str(e)})
        return f"An error occurred: {str(e)}"


inputs = [
    gr.Textbox(value="一个被遗忘的小岛，上面有一座古老的灯塔。当灯塔亮起时，岛上的生物就会发生奇异的变化。", lines=2, placeholder="Usage：一个被遗忘的小岛，上面有一座古老的灯塔。当灯塔亮起时，岛上的生物就会发生奇异的变化。", label="小说提示词"),
    gr.Number(value=1, label="小说章节数"),
    gr.Textbox(value="紧张刺激，类似于青少年恐怖小说。有很多对话和内心独白", lines=2, placeholder="Usage：紧张刺激，类似于青少年恐怖小说。有很多对话和内心独白", label="AI写作风格"),
    gr.Dropdown(["gpt-3.5-turbo-16k", "gpt-3.5-turbo", "gpt-4", "gpt-4-32k"], label="选择GPT模型", value="gpt-3.5-turbo")
]


outputs = [
    gr.Image(label="封面图片", width=1028, height=300),
    gr.File(label="EPUB文件")
]

title = "StoryGenius：一款AI自动创作小说工具"
description = "根据小说的提示词、写作风格和章节数量几分钟即可快速生成奇幻小说。并自动打包为电子书格式。"


iface = gr.Interface(fn=generate_output, inputs=inputs, outputs=outputs, title=title, description=description)
iface.launch(server_name="0.0.0.0", server_port=8000)