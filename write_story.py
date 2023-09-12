import random
import os
import requests
import ast
import time
from anthropic import Anthropic
from config import anthropic_api_key
from config import llm_model_name
from config import completion_with_backoff
from config import save_novel_chapter
from config import generate_uuid

def print_step_costs(response, model):
    input = response['usage']['prompt_tokens']
    output = response['usage']['completion_tokens']

    if model == "gpt-4" or model == "gpt-4":
        input_per_token = 0.00003
        output_per_token = 0.00006
    if model == "gpt-3.5-turbo-16k":
        input_per_token = 0.000003
        output_per_token = 0.000004
    if model == "gpt-4-32k" or model == "gpt-4-32k":
        input_per_token = 0.00006
        output_per_token = 0.00012
    if model == "gpt-3.5-turbo" or model == "gpt-3.5-turbo":
        input_per_token = 0.0000015
        output_per_token = 0.000002
    if model == "claude-2":
        input_per_token = 0.00001102
        output_per_token = 0.00003268

    input_cost = int(input) * input_per_token
    output_cost = int(output) * output_per_token

    total_cost = input_cost + output_cost
    print('Step Cost (OpenAI):', total_cost)


def print_step_costs_anthropic(prompt, response):
    client = Anthropic()
    in_tokens = client.count_tokens(prompt)
    out_tokens = client.count_tokens(response)

    input_cost = 0.00001102 * in_tokens
    output_cost = 0.00003268 * out_tokens

    total_cost = input_cost + output_cost
    print('Step Cost (Anthropic):', total_cost)


def generate_plots(prompt):
    response = completion_with_backoff(
        model=llm_model_name,
        messages=[
            {"role": "system", "content": "You are a creative assistant that generates engaging fantasy novel plots."},
            {"role": "user", "content": f"Generate 10 fantasy novel plots based on this prompt: {prompt}"}
        ]
    )

    print_step_costs(response, llm_model_name)

    return response['choices'][0]['message']['content'].split('\n')


def select_most_engaging(plots):
    response = completion_with_backoff(
        model=llm_model_name,
        messages=[
            {"role": "system", "content": "You are an expert in writing fantastic fantasy novel plots."},
            {"role": "user",
             "content": f"Here are a number of possible plots for a new novel: "
                        f"{plots}\n\n--\n\nNow, write the final plot that we will go with. "
                        f"It can be one of these, a mix of the best elements of multiple, "
                        f"or something completely new and better. "
                        f"The most important thing is the plot should be fantastic, unique, and engaging."}
        ]
    )

    print_step_costs(response, llm_model_name)

    return response['choices'][0]['message']['content']


def improve_plot(plot):
    response = completion_with_backoff(
        model=llm_model_name,
        messages=[
            {"role": "system", "content": "You are an expert in improving and refining story plots."},
            {"role": "user", "content": f"Improve this plot: {plot}"}
        ]
    )

    print_step_costs(response, llm_model_name)

    return response['choices'][0]['message']['content']


def get_title(plot):
    response = completion_with_backoff(
        model=llm_model_name,
        messages=[
            {"role": "system", "content": "You are an expert writer."},
            {"role": "user",
             "content": f"Here is the plot: {plot}\n\nWhat is the title of this book? "
                        f"Just respond with the title, do nothing else. Please respond in Chinese."}
        ]
    )

    print_step_costs(response, llm_model_name)

    return response['choices'][0]['message']['content']


def write_first_chapter(plot, first_chapter_title, writing_style, claude=True):
    if claude:
        url = "https://api.anthropic.com/v1/complete"

        headers = {
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
            "x-api-key": anthropic_api_key,
        }

        prompt_one = f"\n\nHuman: You are a world-class fantasy writer. " \
                     f"I will give you the title of a novel, a high-level plot to follow, " \
                     f"and a desired writing style to use. " \
                     f"From the title, plot, and writing style, write the first chapter of the novel. " \
                     f"Make it incredibly unique, engaging, and well-written. " \
                     f"Start it off with a bang, and include dialogue. " \
                     f"Include only the chapter text, and no surrounding explanations or text. " \
                     f"Do you understand?\n\nAssistant: Yes, I understand. " \
                     f"Please provide the title, plot, and writing style, " \
                     f"and I will write a fantastic opening chapter with dialogue that will hook the reader." \
                     f"\n\nHuman: Here is the high-level plot to follow: {plot}" \
                     f"\n\nThe title of the novel is: `{first_chapter_title}`.\n\n" \
                     f"Here is a description of the writing style you should use: `{writing_style}`" \
                     f"\n\nWrite the first chapter please!\n\nAssistant: " \
                     f"Okay, I've got a really exciting first chapter for you. " \
                     f"It's twenty paragraphs long and very well-written. " \
                     f"As you can see, the language I use is very understandable — " \
                     f"I avoided using overly complex words and phrases. Please respond in Chinese:" \
                     f"\n\nTitle: {first_chapter_title}\n\nChapter #1 Text```"

        data = {
            "model": "claude-2",
            "prompt": prompt_one,
            "max_tokens_to_sample": 5000,
        }

        response = requests.post(url, headers=headers, json=data)

        initial_first_chapter = response.json()['completion'].strip().split('```')[0].strip()

        print_step_costs_anthropic(prompt_one, response.json()['completion'])

        prompt_two = f"\n\nHuman: You are a world-class fantasy writer. " \
                     f"Your job is to take your student's rough initial draft of the first chapter of their fantasy novel, " \
                     f"and rewrite it to be significantly better, with much more detail. " \
                     f"Do you understand?\n\nAssistant: Yes, I understand. " \
                     f"Please provide the plot and the student-written chapter, " \
                     f"and I will rewrite the chapter in a far superior way.\n\nHuman: " \
                     f"Here is the high-level plot you asked your student to follow: " \
                     f"{plot}\n\nHere is the first chapter they wrote: {initial_first_chapter}\n\n" \
                     f"Now, rewrite the first chapter of this novel, in a way that is far superior to your student's chapter. " \
                     f"It should still follow the exact same plot, but it should be far more detailed, much longer, and more engaging. " \
                     f"Here is a description of the writing style you should use: `{writing_style}`\n\nAssistant: Okay, I've rewritten the first chapter. " \
                     f"I took great care to improve it. While the plot is the same, " \
                     f"you can see that my version is noticeably longer, easier to read, " \
                     f"and more exciting. Also, the language I used is far more accessible to a broader audience." \
                     f"Please respond in Chinese.\n\n```"
        data = {
            "model": "claude-2",
            "prompt": prompt_two,
            "max_tokens_to_sample": 5000,
        }

        response_improved = requests.post(url, headers=headers, json=data)

        print_step_costs_anthropic(prompt_two, response_improved.json()['completion'])

        return response_improved.json()['completion'].strip().split('```')[0].strip()


    else:
        response = completion_with_backoff(
            model=llm_model_name,
            messages=[
                {"role": "system", "content": "You are a world-class fantasy writer."},
                {"role": "user",
                 "content": f"Here is the high-level plot to follow: {plot}\n\nWrite the first chapter of this novel: `{first_chapter_title}`.\n\nMake it incredibly unique, engaging, and well-written.\n\nHere is a description of the writing style you should use: `{writing_style}`\n\nInclude only the chapter text. There is no need to rewrite the chapter name. Please respond in Chinese."}
            ]
        )

        print_step_costs(response, llm_model_name)

        improved_response = completion_with_backoff(
            model=llm_model_name,
            messages=[
                {"role": "system",
                 "content": "You are a world-class fantasy writer. Your job is to take your student's rough initial draft of the first chapter of their fantasy novel, and rewrite it to be significantly better, with much more detail."},
                {"role": "user",
                 "content": f"Here is the high-level plot you asked your student to follow: {plot}\n\nHere is the first chapter they wrote: {response['choices'][0]['message']['content']}\n\nNow, rewrite the first chapter of this novel, in a way that is far superior to your student's chapter. It should still follow the exact same plot, but it should be far more detailed, much longer, and more engaging. Here is a description of the writing style you should use: `{writing_style}`.Please respond in Chinese."}
            ]
        )

        print_step_costs(response, llm_model_name)

        return improved_response['choices'][0]['message']['content']


def write_chapter(previous_chapters, plot, chapter_title, claude=True):
    if claude:
        url = "https://api.anthropic.com/v1/complete"

        headers = {
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
            "x-api-key": anthropic_api_key,
        }

        prompt = f"\n\nHuman: You are a world-class fantasy writer. I will provide you with the plot of the novel, the previous chapters, and the plan for the next chapter. Your task is to write the next chapter of the novel in Chinese, following the plot and taking in the previous chapters as context. Do you understand?\n\nAssistant: Yes, I understand. You want me to write the next chapter of a novel, using the plot you provide, the previous chapters for context, and a specific plan for the next chapter. I will ensure the chapter is beautifully written and I will not rewrite the chapter name.\n\nHuman: That's correct. Here is the plot: {plot}\n\nHere are the previous chapters: {previous_chapters}\n\nHere is the plan for the next chapter: {chapter_title}\n\nWrite it beautifully. Include only the chapter text. There is no need to rewrite the chapter name.\n\nAssistant: Here is the next chapter. As you can see, it's around the same length as the previous chapters, and contains witty dialogue:\n```Chapter"

        data = {
            "model": "claude-2",
            "prompt": prompt,
            "max_tokens_to_sample": 5000,
        }

        response = requests.post(url, headers=headers, json=data)

        print_step_costs_anthropic(prompt, response.json()['completion'])

        return 'Chapter ' + response.json()['completion'].strip().split('```')[0].strip()
    else:
        try:
            i = random.randint(1, 2242)
            response = completion_with_backoff(
                model=llm_model_name,
                messages=[
                    {"role": "system", "content": "You are a world-class fantasy writer. "},
                    {"role": "user",
                     "content": f"Plot: {plot}, Previous Chapters: {previous_chapters}\n\n--\n\nWrite the next chapter of this novel in Chinese, following the plot and taking in the previous chapters as context. Here is the plan for this chapter: {chapter_title}\n\nWrite it beautifully. Include only the chapter text. There is no need to rewrite the chapter name."}
                ]
            )

            print_step_costs(response, llm_model_name)

            return response['choices'][0]['message']['content']
        except:
            response = completion_with_backoff(
                model=llm_model_name,
                messages=[
                    {"role": "system", "content": "You are a world-class fantasy writer."},
                    {"role": "user",
                     "content": f"Plot: {plot}, Previous Chapters: {previous_chapters}\n\n--\n\nWrite the next chapter of this novel in Chinese, following the plot and taking in the previous chapters as context. Here is the plan for this chapter: {chapter_title}\n\nWrite it beautifully. Include only the chapter text. There is no need to rewrite the chapter name."}
                ]
            )

            print_step_costs(response, llm_model_name)

            return response['choices'][0]['message']['content']


def generate_storyline(prompt, num_chapters):
    print("Generating storyline with chapters and high-level details...")
    json_format = """[{"Chapter CHAPTER_NUMBER_HERE - CHAPTER_TITLE_GOES_HERE": 
    "CHAPTER_OVERVIEW_AND_DETAILS_GOES_HERE"}, ...]"""
    response = completion_with_backoff(
        model=llm_model_name,
        messages=[
            {"role": "system",
             "content": "You are a world-class fantasy writer. Your job is to write a detailed storyline,"
                        " complete with chapters, for a fantasy novel. "
                        "Don't be flowery -- you want to get the message across in as few words as possible. "
                        "But those words should contain lots of information. Please respond in Chinese"},
            {"role": "user",
             "content": f'Write a fantastic storyline with {num_chapters} chapters and high-level details based on this plot:'
                        f' {prompt}.\n\nDo it in this list of dictionaries format {json_format}.'
                        f' And Please respond in Chinese. The response content must be in standard JSON format, without any prefixes and special symbols.'}
        ]
    )

    print_step_costs(response, llm_model_name)

    improved_response = completion_with_backoff(
        model=llm_model_name,
        messages=[
            {"role": "system",
             "content": "You are a world-class fantasy writer. "
                        "Your job is to take your student's rough initial draft of the storyline of a fantasy novel in Chinese, "
                        "and rewrite it to be significantly better. Please respond in Chinese"},
            {"role": "user",
             "content": f"Here is the draft storyline they wrote: {response['choices'][0]['message']['content']}\n\nNow, "
                        f"rewrite the storyline in Chinese, in a way that is far superior to your student's version. "
                        f"It should have the same number of chapters, "
                        f"but it should be much improved in as many ways as possible. "
                        f"Remember to do it in this list of dictionaries format {json_format}. please respond in Chinese"
                        f' And please, only return the JSON content without any prefix.'}
        ]
    )

    print_step_costs(improved_response, llm_model_name)

    return improved_response['choices'][0]['message']['content']


def write_to_file(prompt, content):
    # Create a directory for the prompts if it doesn't exist
    if not os.path.exists('prompts'):
        os.mkdir('prompts')

    # Replace invalid characters for filenames
    valid_filename = ''.join(c for c in prompt if c.isalnum() or c in (' ', '.', '_')).rstrip()
    file_path = f'prompts/{valid_filename}.txt'

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f'Output for prompt "{prompt}" has been written to {file_path}\n')


def write_fantasy_novel(prompt, num_chapters, writing_style, claude_true=False, model_name="gpt-3.5-turbo-16k"):
    global llm_model_name
    llm_model_name = model_name

    # 每本小说生成一个唯一的uuid
    novel_id = generate_uuid()

    plots = generate_plots(prompt)
    print('generated plots')
    print(f'【plots】: {plots}\n\n')

    best_plot = select_most_engaging(plots)
    print('selected best plot')
    print(f'【best_plot】: {best_plot}\n\n')

    improved_plot = improve_plot(best_plot)
    print('plot improved')
    print(f'【improved_plot】: {improved_plot}\n\n')
    time.sleep(20)

    title = get_title(improved_plot)
    print('title generated')
    print(f'【title】: {title}\n\n')

    storyline = generate_storyline(improved_plot, num_chapters)
    print('storyline generated')
    print(f'【storyline】: {storyline}\n\n')

    chapter_titles = ast.literal_eval(storyline)
    print(f'【chapter_titles】: {chapter_titles}\n\n')

    novel = f"Storyline:\n{storyline}\n\n"

    first_chapter = write_first_chapter(storyline, chapter_titles[0], writing_style.strip(), claude_true)
    print('first chapter written')
    save_novel_chapter(novel_id, 0, list(chapter_titles[0])[0], first_chapter)
    print(f'【first_chapter】: {first_chapter}\n\n')
    time.sleep(20)

    novel += f"Chapter 1:\n{first_chapter}\n"
    chapters = [first_chapter]

    for i in range(num_chapters - 1):
        print(f"Writing chapter {i + 2}...")  # + 2 because the first chapter was already added
        time.sleep(30)

        chapter = write_chapter(novel, storyline, chapter_titles[i + 1], claude_true)
        try:
            if len(str(chapter)) < 100:
                time.sleep(30)
                print('Length minimum not hit. Trying again.')
                chapter = write_chapter(novel, storyline, chapter_titles[i + 1], claude_true)
        except:
            time.sleep(20)
            chapter = write_chapter(novel, storyline, chapter_titles[i + 1], claude_true)

        novel += f"Chapter {i + 2}:\n{chapter}\n"
        chapters.append(chapter)
        print(f'【Chapter_{i + 2}】: {chapter}\n\n')
        save_novel_chapter(novel_id, (i+1), list(chapter_titles[i + 1])[0], chapter)

    return novel, title, chapters, chapter_titles
