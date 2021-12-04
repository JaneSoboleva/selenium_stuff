import selenium_config
import pixiv_cred
import os
import sys
import time
import traceback
import asyncio
import async_timeout
import aiohttp
import aiofiles
import requests
import secrets
import threading
import logging
import http.client as http_client
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException


def show_exception_info(custom_message):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    exc_fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(custom_message, exc_type, exc_fname, exc_tb.tb_lineno, '| full details:')
    traceback.print_exc()


async def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)


def sync_exec(coro):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)


async def test_async_func(value, test_async_comment):
    async with sem:
        async with async_timeout.timeout(100):
            await asyncio.sleep(1)
            print("test async:", test_async_comment, " | ", int(value), " | starting...")
            await asyncio.sleep(int(value))
            print("test async:", test_async_comment, " | ", int(value), " | ended.")


def download_file_legacy(file_url, save_path, rename_to=""):
    try:
        print("Legacy; saving", file_url, "to", save_path, "... ")
        directory = os.path.dirname(save_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        file_name = save_path + file_url[file_url.rfind('/') + 1:]
        if rename_to != "":
            file_name = save_path + rename_to + file_url[file_url.rfind('.'):]
        headers = {
            "User-Agent":
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/94.0.4606.81 Safari/537.36 "
        }

        # urllib.request.urlretrieve(file_url, file_name)  # this is an old way, I'll be using "requests" now

        # using requests lib here
        s = requests.session()
        s.headers.update(headers)
        for cookie in driver.get_cookies():
            c = {cookie['name']: cookie['value']}
            s.cookies.update(c)
        r = s.get(file_url, allow_redirects=True)
        open(file_name, 'wb').write(r.content)
        print("Legacy; done downloading", file_url)
    except:
        show_exception_info("download_file_legacy for " + file_url + " failed, exception details:")


async def download_file(file_url, save_path, rename_to="", cookies=None, random_delay=0.01):
    try:
        async with sem:
            async with async_timeout.timeout(600):
                await asyncio.sleep(random_delay)
                print(random_delay, "Saving", file_url, "to", save_path, "... ")
                await ensure_dir(save_path)
                file_name = save_path + file_url[file_url.rfind('/') + 1:]
                if rename_to != "":
                    file_name = save_path + rename_to + file_url[file_url.rfind('.'):]
                headers = {
                    "User-Agent":
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/94.0.4606.81 Safari/537.36 "
                }

                # reprocessing cookies to be accepted by aiohttp.ClientSession
                reprocessed_cookies = {}
                for cookie in cookies:
                    reprocessed_cookies[cookie['name']] = cookie['value']

                # old and wrong method of repacking cookies, which costed me a few days to debug, cuz i'm stupid
                # reprocessed_cookies = []
                # for cookie in cookies:
                #     new_cookie = {'name': cookie['name'], 'value': cookie['value']}
                #     reprocessed_cookies.append(new_cookie)
                # ends

                # using aiohttp here
                async with aiohttp.ClientSession(headers=headers, cookies=reprocessed_cookies) as session:
                    async with session.get(file_url) as resp:
                        if resp.status == 200:
                            f = await aiofiles.open(file_name, mode='wb')
                            await f.write(await resp.read())
                            await f.close()
                        else:
                            print(random_delay, "Response status is not 200; instead, got", resp.status)
                print(random_delay, "Done downloading", file_url)
    except:
        show_exception_info("download_file for " + file_url + " failed, exception details:")


def login_to_fanbox():
    try:
        print('Logging in to fanbox...')
        s_login, s_pwd = pixiv_cred.loadLoginInfo()
        driver.get("https://www.fanbox.cc/auth/start")
        wait.until(presence_of_element_located((By.XPATH, "//input")))
        elems = driver.find_elements_by_xpath("//input")
        counter = 0
        for elem in elems:
            if counter == 0:
                elem.send_keys(s_login)
            else:
                elem.send_keys(s_pwd)
                elem.submit()
                break
            counter += 1
        try:
            print('Verifying success of login to fanbox...')
            wait.until(presence_of_element_located((By.XPATH, "//button/div[starts-with(text(), 'Login')]")))
            print('For some reason, the login button is still detected, meaning login failed.')
        except:
            print('Logged in successfully.')
    except Exception as e:
        show_exception_info('login_to_fanbox failed, exception details:')


def fanbox_handle_age_verification():
    try:
        short_wait.until(presence_of_element_located((By.XPATH, "//button/div[starts-with(text(),'Yes')]")))
        btn = driver.find_element_by_xpath("//button/div[starts-with(text(),'Yes')]")
        btn.click()
        print("Age verification should be passed.")
    except TimeoutException:
        print("Age verification function for fanbox didn't detect a Yes button.")


def download_domria_images(needed_url):
    try:
        print('Downloading dom.ria.com images, URL: ' + needed_url)
        save_dir = needed_url[needed_url.rfind('/') + 1:] + "/"
        driver.get(needed_url)
        elem = driver.find_element_by_xpath("//picture")
        elem.click()
        time.sleep(1)
        elems = driver.find_elements_by_xpath("//img")
        for elem in elems:
            s_url = elem.get_attribute("src")
            if "cdn.riastatic.com/photosnew" in s_url and "m.jpg" in s_url:
                s_url = s_url[:-5] + "xg.jpg"
                download_file(s_url, save_dir)
    except:
        show_exception_info('download_ria_images failed, exception details:')


def get_filtered_links(filter_string):
    results = []
    elems = driver.find_elements_by_xpath("//*[@href]")
    for elem in elems:
        s_url = elem.get_attribute("href")
        if filter_string in s_url:
            results.append(s_url)
    elems = driver.find_elements_by_xpath("//*[@src]")
    for elem in elems:
        s_url = elem.get_attribute("src")
        if filter_string in s_url:
            results.append(s_url)
    return list(tuple(results))


def download_images_from_fanbox_url(needed_url, skip_if_file_exists=False, async_flag=True):
    try:
        print('Downloading from a fanbox post, URL: ' + needed_url)
        post_id = needed_url[needed_url.rfind('/') + 1:]
        author_name = fanbox_extract_author_name_from_url(needed_url)
        driver.get(needed_url)
        fanbox_handle_age_verification()
        elems = driver.find_elements_by_xpath("//h1")
        post_tagname = post_id  # + "--" + elems[1].text + "--" + elems[2].text
        actual_save_folder = local_folder  # folder path for saving is set here
        actual_save_folder += author_name + "/"  # adding author's name to the path
        if actual_save_folder[-1] != '/':
            actual_save_folder += '/'
        elems = driver.find_elements_by_xpath("//*[@href]")
        elem_counter = 0

        # trying to do async stuff now
        loop = asyncio.get_event_loop()
        tasks = []  # for storing all the tasks we will create in the next step
        processed_urls = []
        for elem in elems:
            s_url = elem.get_attribute("href")
            if "downloads.fanbox.cc" in s_url and s_url not in processed_urls:
                processed_urls.append(s_url)
                elem_counter += 1
                elem_s_counter = str(elem_counter)
                if elem_counter < 10:
                    elem_s_counter = "0" + elem_s_counter
                if elem_counter < 100:
                    elem_s_counter = "0" + elem_s_counter
                rename_to = post_tagname + "--" + elem_s_counter  # file naming format is set here. "" for default
                actual_final_path = actual_save_folder + s_url[s_url.rfind('/') + 1:]
                if rename_to != "":
                    actual_final_path = actual_save_folder + rename_to + s_url[s_url.rfind('.'):]
                if skip_if_file_exists and os.path.exists(actual_final_path):
                    print('File ' + actual_final_path + ' already exists, aborting.')
                    return False

                if async_flag:
                    task_dl = loop.create_task(download_file(s_url, actual_save_folder, rename_to, driver.get_cookies(),
                                                             float((1 + secrets.randbelow(100))) / 100))
                    tasks.append(task_dl)
                else:
                    download_file_legacy(s_url, actual_save_folder, rename_to)
        if async_flag and len(tasks) > 0:
            loop.run_until_complete(asyncio.wait(tasks))

        print("Post download completed.")
        return True
    except Exception as e:
        show_exception_info('download_images_from_fanbox_url failed, exception details:')
        return False


def fanbox_extract_author_name_from_url(needed_url):
    fanbox_cc_index = needed_url.find(".fanbox.cc")
    if fanbox_cc_index != -1:
        left_part = needed_url[:fanbox_cc_index]
    else:
        left_part = needed_url
    if left_part.find("//") != -1:
        author_name = left_part[left_part.find("//") + 2:]
    elif left_part.find("/") != -1:
        author_name = left_part[left_part.find("/") + 1:]
    else:
        author_name = left_part
    return author_name


def download_author_from_fanbox_url(needed_url, forced=0, async_flag=True):
    # forced: 0 - quit after encountering an existing dir; 1 - download all, skip existing dirs; 2 - download all
    current_page = 0
    author_name = fanbox_extract_author_name_from_url(needed_url)
    print("Downloading images from the fanbox author: " + author_name)
    following_url = "https://" + author_name + ".fanbox.cc"
    driver.get(following_url)
    fanbox_handle_age_verification()
    try:
        while True:
            current_page += 1
            following_url = "https://" + author_name + ".fanbox.cc/posts?page=" + str(current_page)
            print('Visiting another page:', following_url)
            driver.get(following_url)

            time.sleep(2)

            if driver.current_url != following_url:
                print("/posts?page=something returned to /posts. Looks like we've reached the end.")
                break
            wait.until(presence_of_element_located((By.XPATH, "//a[starts-with(@href,'/posts/')]")))
            elems = driver.find_elements_by_xpath("//a[starts-with(@href,'/posts/')]")
            post_links = []
            for elem in elems:
                paywall_present = False
                try:
                    elem.find_element_by_xpath(".//div[starts-with(text(), 'Plan list')]")
                    paywall_present = True
                except NoSuchElementException:
                    pass
                if not paywall_present:
                    post_links.append(elem.get_attribute("href"))
                    post_links.append(elem.get_attribute("href"))
            # print(post_links) -- check out later, for why exactly paywalled posts still appear in the list
            processed_links = []
            for post_link in post_links:
                if post_link not in processed_links:
                    processed_links.append(post_link)
                    try_download = download_images_from_fanbox_url(post_link, forced < 2, async_flag)
                    if not try_download and forced == 0:
                        print('Presumably met an existing directory while trying to handle the following URL:')
                        print(following_url)
                        print('Finishing early.')
                        return False
    except TimeoutException:
        show_exception_info("Nothing. Is it really a fanbox author page?")
    print("Author download completed.")


def run_commands_from_file(filename):
    file_task = open(filename, 'r')
    file_abs_path = os.path.abspath(filename)
    task_lines = file_task.read().splitlines()
    for task_line in task_lines:
        my_cmd_params = task_line.split(" ")
        process_command(my_cmd_params, referrer_path=file_abs_path)


def process_command(params, referrer_path=""):
    global process_command_depth
    process_command_depth += 1
    if process_command_depth > 20:  # to prevent accidental recursion
        try:
            print("♂It's so fucking deep♂")
            driver.quit()
            raise SystemExit
        except:
            pass
    print("Running:", params)
    command = params[0].lower()
    if command == "finish" or command == "quit" or command == "exit":
        driver.quit()
        raise SystemExit
    if command == "fanbox_age":
        fanbox_handle_age_verification()
    if command == "visit":
        try:
            if len(params) >= 2:
                driver.get(params[1])
        except:
            print("Visiting", params[1], "failed.")
    if command == "sleep":
        try:
            time.sleep(int(params[1]))
        except:
            time.sleep(1)
    if command == "run_from_file":
        try:
            run_commands_from_file(params[1])
        except:
            print("Running commands from file", params[1], "failed.")
    if command == "test":
        # try:
        #     print(1 / 0)
        # except:
        #     show_exception_info("Here's what happened: ")
        async_tasks.append(params[1])
    if command == "fanbox_login":
        login_to_fanbox()
    if command == "fanbox_save_credentials":
        if len(params) >= 3:
            pixiv_cred.saveLoginInfo(params[1], params[2])
        else:
            pixiv_cred.saveLoginInfo()
    if command == "domria":
        download_domria_images(params[1])
    if command == "fanbox_dl_post" or command == "fanbox_post_dl":
        async_flag = True
        try:
            if params[2] == 's':
                async_flag = False
        except:
            pass
        download_images_from_fanbox_url(params[1], async_flag=async_flag)
    if command == "fanbox_dl_author" or command == "fanbox_author_dl":
        try:
            last_param = params[2]
        except IndexError:
            last_param = 'none'
        if last_param == "f":
            download_author_from_fanbox_url(params[1], 1)
        elif last_param == "F":
            download_author_from_fanbox_url(params[1], 2)
        else:
            download_author_from_fanbox_url(params[1])
    if command == "set_local_folder":
        global local_folder
        local_folder = params[1]
        if local_folder[-1] != "/":
            local_folder += "/"
    if command == "xpath":
        final_index = v2_destination_to_final_index(params[1], referrer_path)
        xpath_param = ""
        for i in range(len(params)):
            if i > 1:
                xpath_param += params[i]
        v2_xpath_filter_to_variable(xpath_param, final_index)
    if command == "click":
        final_index = v2_destination_to_final_index(params[1], referrer_path)
        element_number = 0
        if len(params) >= 3:
            element_number = int(params[2])
        v2_element_click(final_index, element_number)

    process_command_depth -= 1


def v2_destination_to_final_index(destination_index, referrer_path=""):
    global process_command_depth
    return referrer_path + "///" + str(process_command_depth) + "///" + destination_index


def v2_xpath_filter_to_variable(xpath, final_index):
    global global_vars
    global_vars[final_index] = driver.find_elements_by_xpath(xpath)


def v2_element_click(final_index, element_number=0):
    global global_vars
    try:
        global_vars[final_index][element_number].click()
    except:
        print("v2_element_click failed")


async def async_stuff_runs_here(the_lock):
    global async_tasks
    while True:
        await asyncio.sleep(2)
        # accessing the shared resource, and thus surrounding it with acquire/release... hopefully doing it right
        the_lock.acquire()
        async_tasks_copy = async_tasks.copy()
        async_tasks = []
        the_lock.release()
        for async_task in async_tasks_copy:
            print(async_task)


def async_stuff_thread():
    # creating a new loop cause otherwise apparently an exception occurs
    my_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(my_loop)
    my_lock = threading.Lock()
    my_coros = [asyncio.ensure_future(async_stuff_runs_here(my_lock))]
    my_loop.run_until_complete(asyncio.wait(my_coros))


task_file_to_load = ""
global_vars = {}
async_tasks = []
process_command_depth = 0
if len(sys.argv) > 1:
    task_file_to_load = str(sys.argv[1])
local_folder = selenium_config.local_folder
driver = selenium_config.driver
wait = WebDriverWait(driver, 5)
short_wait = WebDriverWait(driver, 2)
sem = asyncio.Semaphore(selenium_config.simultaneous_tasks)  # using this, we set a limit of simultaneous tasks

# new async section: a function that will handle all async subfunctions (will get dumped to async_tasks)
my_thread = threading.Thread(target=async_stuff_thread, args=())
my_thread.start()

# logging stuff below
# http_client.HTTPConnection.debuglevel = 1
# logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True

if task_file_to_load == "":
    while True:
        cmd_params = input(">> ").split(" ")
        process_command(cmd_params)
else:
    run_commands_from_file(task_file_to_load)
process_command("quit")
