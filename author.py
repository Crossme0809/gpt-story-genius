from ebooklib import epub
import base64
import os
import requests
from config import completion_with_backoff
from config import stability_api_key


def generate_cover_prompt(plot):
    response = completion_with_backoff(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system",
             "content": "You are a creative assistant that writes a spec for the cover art of a book, based on the book's plot."},
            {"role": "user",
             "content": f"Plot: {plot}\n\n--\n\nDescribe the cover we should create, based on the plot. This should be two sentences long, maximum."}
        ]
    )
    return response['choices'][0]['message']['content']


def create_cover_image(plot):
    plot = str(generate_cover_prompt(plot))

    engine_id = "stable-diffusion-xl-beta-v2-2-2"
    api_host = os.getenv('API_HOST', 'https://api.stability.ai')
    api_key = stability_api_key

    if api_key is None:
        raise Exception("Missing Stability API key.")

    response = requests.post(
        f"{api_host}/v1/generation/{engine_id}/text-to-image",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}"
        },
        json={
            "text_prompts": [
                {
                    "text": plot
                }
            ],
            "cfg_scale": 7,
            "clip_guidance_preset": "FAST_BLUE",
            "height": 768,
            "width": 512,
            "samples": 1,
            "steps": 30,
        },
    )

    if response.status_code != 200:
        raise Exception("Non-200 response: " + str(response.text))

    data = response.json()

    # 检查目录是否存在，如果不存在则创建
    directory = "./cover/"
    if not os.path.exists(directory):
        os.makedirs(directory)

    for i, image in enumerate(data["artifacts"]):
        image_bytes = base64.b64decode(image["base64"])
        file_path = f"./cover/cover_{i}.png"  # 修改为您想要的文件路径
        with open(file_path, "wb") as f:
            f.write(image_bytes)

        return file_path


def create_epub(title, author, chapters, cover_image_path='cover.png'):
    book = epub.EpubBook()

    # Set metadata
    book.set_identifier('id123456')
    book.set_title(title)
    book.set_language('zh-cn')
    book.add_author(author)

    # Add cover image
    with open(cover_image_path, 'rb') as cover_file:
        cover_image = cover_file.read()
    book.set_cover('cover.png', cover_image)

    # Create chapters and add them to the book
    epub_chapters = []
    for i, chapter_dict in enumerate(chapters):
        full_chapter_title = list(chapter_dict.keys())[0]
        chapter_content = list(chapter_dict.values())[0]
        if ' - ' in full_chapter_title:
            chapter_title = full_chapter_title.split(' - ')[1]
        else:
            chapter_title = full_chapter_title

        chapter_file_name = f'chapter_{i + 1}.xhtml'
        epub_chapter = epub.EpubHtml(title=chapter_title, file_name=chapter_file_name, lang='zh-cn')

        # Add paragraph breaks
        formatted_content = ''.join(
            f'<p>{paragraph.strip()}</p>' for paragraph in chapter_content.split('\n') if paragraph.strip())

        epub_chapter.content = f'<h1>{chapter_title}</h1>{formatted_content}'
        book.add_item(epub_chapter)
        epub_chapters.append(epub_chapter)

    # Define Table of Contents
    book.toc = (epub_chapters)

    # Add default NCX and Nav files
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Define CSS style
    style = '''
    @namespace epub "http://www.idpf.org/2007/ops";
    body {
        font-family: Cambria, Liberation Serif, serif;
    }
    h1 {
        text-align: left;
        text-transform: uppercase;
        font-weight: 200;
    }
    '''

    # Add CSS file
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
    book.add_item(nav_css)

    # Create spine
    book.spine = ['nav'] + epub_chapters

    # 检查目录是否存在，如果不存在则创建
    directory = "./epub/"
    if not os.path.exists(directory):
        os.makedirs(directory)

    # 保存 EPUB 文件
    file_path = f"./epub/{title}.epub"  # 修改为您想要的文件路径
    epub.write_epub(file_path, book)

    return file_path
