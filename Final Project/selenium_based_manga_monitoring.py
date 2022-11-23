#!/usr/bin/env python
# coding: utf-8

# # Imports Block

# In[ ]:


from pyvirtualdisplay import Display
from selenium import webdriver
import selenium
import re


# # Functions Block

# In[ ]:


# decorator for more comfortable output in CLI
def print_decorator(func):
    
    def printer():
        
        print()
        func()
        print()
    
    return printer

def extract_integer_from_string(string):
    
    '''
    Tries to extract a float or integer from any string value and returns an integer value.
    
    '''
    
    integer_value = int(float(
                        ''.join(re.findall('\d|[.,]', str(string)))
                        )
                    )
    
    return integer_value

@print_decorator
def get_user_input():
    
    '''
    A simple functioun to ineractively get 2 input values (and globalize them as variables) from User: 
    
    user_input_1 - a title of Manga; 
    user_input_2 - a number of chapters that user have already read; 
    
    and user_input_1_adapted handled from user_input_1 and processed with regex.
    
    Note: in fact, there is also an input between user_input_1 and user_input_1 actually for User 
          with question 'Did you read it? (Y|N)' 
          (so that 'n' answer means that user_input_2 == '0' but anything else follows by question 
           'What chapter you stop on? (one number)' to get another user_input_2).
    
    '''
    
    global user_input_1, user_input_2, user_input_1_adapted
    
    user_input_1 = input('What Manga you want to check on new chapters? (enter full title correctly) ')
    
    user_input_2 = input('Did you read it? (Y|N) ')
    
    if user_input_2 == '' or user_input_2.strip().lower()[0] != 'n':
        
        user_input_2 = input('What chapter did you stop on? (one number) ')
        
        while re.sub('\D', '', user_input_2) == '':
            print('\nYour previous input has not a number :( please, try again...')
            user_input_2 = input('What chapter did you stop on? (one number) ')
        
        user_input_2 = extract_integer_from_string(user_input_2)
        
    else:
        
        user_input_2 = 0
    
    user_input_1_adapted = re.sub('\s+', ' ', user_input_1).strip()
    user_input_1_adapted = '-'.join(
                              [re.sub('\W', '', word) for word in user_input_1_adapted.split()]
                           ).lower()

def start_or_reload_display(driver_name='Chrome', 
                            detach_display=True):
    
    '''
    Returns 2 objects: selenium.webdriver and pyvirtualdisplay.Display (None if detach_display argument is False)
    Supported values for driver_name argument are 'Chrome' and 'Safari'
    
    Note: XVFB should be installed in OS if detach_display argument is True.
    
    '''
    
    if detach_display:
        
        virtual_display = Display(
            visible=0, 
            size=(1024, 768)
        )
        
        virtual_display.start()
    else:
        virtual_display = None
    
    if driver_name == 'Chrome':
        selenium_object = webdriver.Chrome()
    elif driver_name == 'Safari':
        selenium_object = webdriver.Safari()
    
    # just to check initialized selenium_object
    selenium_object.maximize_window()
    
    return selenium_object, virtual_display

def get_latest_chapter_text(selenium_object, 
                            good_css_selector, 
                            url_to_print, 
                            title_css_selector=None, 
                            good_css_selector_num=0, 
                            title_css_selector_num=0, 
                            bad_css_selector='.not-found-content'):
    
    '''
    Extracts and returns 2 string values with useful text from specified good_css_selector 
    and title_css_selector (None if not specified) in a list with length 2.
    
    Expected text with a pointer to a number of the latest chapter in good_css_selector 
    (when prepared webdriver at a page with a content about some kind of Manga) 
    as well as a title text in title_css_selector (optionally).
    
    selenium_object - prepared webdriver; 
    good_css_selector - CSS-selector where is the text about the latest chapter for the Manga presented; 
    url_to_print - specified url (of resource's mainpage, for example, as well as the direct page of the Manga); 
    title_css_selector - CSS-selector where is the title text for the Manga presented; 
    
    good_css_selector_num - if there are more than one text-blocks are presented when handle 
                            with good_css_selector argument (0 is the first one from list); 
    title_css_selector_num - on the analogy of good_css_selector_num for title_css_selector argument; 
    bad_css_selector - CSS-selector where is the text represents a page with 404 (not found) error 
                       to handle it instead of getting message about fail.
    
    If good_css_selector element is not found on the page, there is one of the messages 
    (about not found Manga on this resource if bad_css_selector argument is specified 
     or, in another way, about fail while checking this resource) is being printed 
    with specified url_to_print argument.
    
    '''
    
    title_text = None
    
    try:
        latest_chapter_text = selenium_object.find_elements("css selector", 
                                                            good_css_selector
                              )[good_css_selector_num].text
        if title_css_selector is not None:
            try:
                title_text = selenium_object.find_elements("css selector", 
                                                           title_css_selector
                             )[title_css_selector_num].text
                title_text = re.sub('\s+', ' ', title_text.replace('\n', '')).strip()
            except:
                pass
    except IndexError:
        try:
            latest_chapter_text = selenium_object.find_element("css selector", bad_css_selector).text
            print(f'This Manga is not presented on {url_to_print} but you still can try find here other Mangas!')
        except:
            latest_chapter_text = 'bad request'
            print(f'Unfortunately, check for new chapters failed on {url_to_print} for this Manga')
        latest_chapter_text = None
    
    return [latest_chapter_text, title_text]

def get_new_chapters_integer(latest_chapter_text, 
                             chapters_already_read):
    
    '''
    Extracts an integer number meaning the latest chapter of the Manga 
    from any text in latest_chapter_text argument pointing to it 
    and returns an integer of new chapters count (calculated by chapters_already_read argument) 
    that user can read.
    
    latest_chapter_text - a string with useful information about the latest chapter of the Manga; 
    chapters_already_read - a number of chapters that user have already read.
    
    '''
    
    chapters_already_read = extract_integer_from_string(chapters_already_read)
    
    try:
        latest_chapter = extract_integer_from_string(latest_chapter_text)
        new_chapters_found = latest_chapter - chapters_already_read
    except ValueError:
        raise Exception('unexpected element found while extracting latest chapter')
    
    return new_chapters_found

def print_output_message(url_to_print, 
                         new_chapters_integer, 
                         title_text=None):
    
    '''
    Constructs and prints a message depending on calculated count of new chapters of the Manga to output.
    
    url_to_print - specified url (of resource's mainpage, for example, as well as the direct page of the Manga); 
    new_chapters_integer - the calculated count of new chapters that user can read; 
    title_text - the Manga's title.
    
    '''
    
    message = f'According to {url_to_print} '
    
    if new_chapters_integer == 0:
        message += 'there are no new chapters you can read.'
    elif new_chapters_integer == 1:
        message += 'there is 1 more chapter you can read!'
    elif new_chapters_integer > 1:
        message += f'there are {new_chapters_integer} more chapters you can read!'
    
    if title_text is not None:
        message += f' \n(If you meant Manga titled as {title_text})'
    
    if new_chapters_integer < 0:
        if title_text is None:
            text_by_title = 'for this Manga'
        else:
            text_by_title = f'if you meant Manga titled as {title_text}'
        message = (f'Unfortunately, check for new chapters failed on {url_to_print} \n'
                   f'({new_chapters_integer} chapters detected {text_by_title})')
    
    print(message)

def get_processed_core_page(selenium_object, 
                            good_css_selector, 
                            url_to_print, 
                            chapters_already_read, 
                            title_css_selector=None, 
                            good_css_selector_num=0, 
                            title_css_selector_num=0, 
                            bad_css_selector='.not-found-content'):
    
    '''
    Wraps up sequential calls to 
    
    get_latest_chapter_text, 
    get_new_chapters_integer and 
    print_output_message 
    
    functions defined above. 
    
    '''
    
    latest_chapter_text, title_text = get_latest_chapter_text(selenium_object=selenium_object, 
                                                              good_css_selector=good_css_selector, 
                                                              url_to_print=url_to_print, 
                                                              title_css_selector=title_css_selector, 
                                                              good_css_selector_num=good_css_selector_num, 
                                                              title_css_selector_num=title_css_selector_num, 
                                                              bad_css_selector=bad_css_selector)
    if latest_chapter_text is not None:
        new_chapters_count = get_new_chapters_integer(latest_chapter_text=latest_chapter_text, 
                                                      chapters_already_read=chapters_already_read)
        print_output_message(url_to_print=url_to_print, 
                             new_chapters_integer=new_chapters_count, 
                             title_text=title_text)


# # Selenium Based Manga Monitoring

# In[ ]:


get_user_input()

# prepare webdriver
selenium_spider, virtual_display = start_or_reload_display(driver_name='Chrome', detach_display=False)

# specify a group of resources with the same CSS elements
urls_batch_1 = ['https://1stkissmanga.io', 
                'https://zinmanga.com', 
                'https://coffeemanga.com', 
                'https://kunmanga.com']

for url in urls_batch_1:
    
    # construct the direct link to manga to check it if it exists
    direct_link_to_manga = f'{url}/manga/{user_input_1_adapted}'
    # connect webdriver to the direct link
    selenium_spider.get(direct_link_to_manga)
    
    # get the list of elements from '.heading' CSS-selectors
    list_of_heading_elements_found = selenium_spider.find_elements("css selector", '.heading')
    
    # check if the first '.heading' CSS-selector found text is about specific 404 error
    if len(list_of_heading_elements_found) > 0 and (
       list_of_heading_elements_found[0].text != 'Oops! page not found.'):
        # if not - process this page
        
        # check the page on new chapters of the manga
        get_processed_core_page(selenium_object=selenium_spider, 
                                good_css_selector='li.wp-manga-chapter:nth-child(1) > a:nth-child(1)', 
                                url_to_print=url, 
                                chapters_already_read=user_input_2, 
                                title_css_selector='.post-title', 
                                good_css_selector_num=0, 
                                title_css_selector_num=0, 
                                bad_css_selector='.not-found-content')
        
    else:
        
        # construct the link with suitable mangas found on searching page of the resource
        user_input_1_readapted = '+'.join(user_input_1.lower().split())
        searching_url = url + f'/?s={user_input_1_readapted}&post_type=wp-manga'
        # and connect webdriver to this link
        selenium_spider.get(searching_url)
        
        # check the page on new chapters of the manga
        get_processed_core_page(selenium_object=selenium_spider, 
                                good_css_selector='span.font-meta:nth-child(2)', 
                                url_to_print=url, 
                                chapters_already_read=user_input_2, 
                                title_css_selector='.post-title', 
                                good_css_selector_num=0, 
                                title_css_selector_num=0, 
                                bad_css_selector='.not-found-content')

# resource with other CSS elements
webtoons_url = 'https://www.webtoons.com/en/dailySchedule'
# connect webdriver to webtoons_url
selenium_spider.get(webtoons_url)
# and get all of this public source code with selenium and some preprocessing
full_page_text_source = selenium_spider.page_source.replace('\n', '').replace('\t', '')

# try to find suitable links to the manga in full_page_text_source
list_of_useful_rows = re.findall(('(?:https://www.webtoons.com/en/)'
                                  '(?:\w|-)+'
                                  f'(?:/{user_input_1_adapted}/)'
                                  '(?:list\?title_no=\d+)').lower(), 
                                 full_page_text_source.lower())
if len(list_of_useful_rows) == 0:
    list_of_useful_rows = re.findall(('(?:https://www.webtoons.com/en/)'
                                      '(?:\w|-)+/(?:\w|-)*'
                                      f'(?:{user_input_1_adapted})'
                                      '(?:\w|-)*(?:/)'
                                      '(?:list\?title_no=\d+)').lower(), 
                                     full_page_text_source.lower())

if len(list_of_useful_rows) > 0:
    # if at least one link to the manga found inside full_page_text_source
    
    # take the first of them
    webtoons_link_to_manga = list_of_useful_rows[0]
    # and redirect webdriver to it
    selenium_spider.get(webtoons_link_to_manga)
    
    # check the page on new chapters of the manga
    get_processed_core_page(selenium_object=selenium_spider, 
                            good_css_selector='span:nth-child(6)', 
                            url_to_print=webtoons_url, 
                            chapters_already_read=user_input_2, 
                            title_css_selector='h1.subj', 
                            good_css_selector_num=1, 
                            title_css_selector_num=0, 
                            bad_css_selector='.error_area')
    
else:
    
    print(f'This Manga is not presented on {webtoons_url} but you still can try find here other Mangas!')

print()

selenium_spider.quit()
if virtual_display is not None:
    virtual_display.stop()


#  

#  

#  
