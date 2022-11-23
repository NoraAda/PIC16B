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


def extract_integer_from_string(string):
    
    '''
    Tries to extract a float or integer from any string value and returns an integer value.
    
    '''
    
    integer_value = int(float(
                        ''.join(re.findall('\d|[.,]', str(string)))
                        )
                    )
    
    return integer_value

def get_user_input():
    
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
    
    if detach_display:
        
        virtual_display = Display(
            visible=0, 
            size=(1024, 768)
        )
        
        virtual_display.start()
    
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
                            good_css_selector_num=0, 
                            bad_css_selector='.not-found-content'):
    
    try:
        latest_chapter_text = selenium_object.find_elements("css selector", 
                                                            good_css_selector
                              )[good_css_selector_num].text
    except IndexError:
        try:
            latest_chapter_text = selenium_object.find_element("css selector", bad_css_selector).text
            print(f'This Manga is not presented on {url_to_print} but you still can try find here other Mangas!')
        except:
            latest_chapter_text = 'bad request'
            print(f'Unfortunately, check for new chapters failed on {url_to_print} for this Manga')
        latest_chapter_text = None
    
    return latest_chapter_text

def get_new_chapters_integer(latest_chapter_text, 
                             chapters_already_read):
    
    chapters_already_read = extract_integer_from_string(chapters_already_read)
    
    try:
        latest_chapter = extract_integer_from_string(latest_chapter_text)
        new_chapters_found = latest_chapter - chapters_already_read
    except ValueError:
        raise Exception('unexpected element found while extracting latest chapter')
    
    return new_chapters_found

def print_output_message(url_to_print, 
                         new_chapters_integer):
    
    message = f'According to {url_to_print} '
    
    if new_chapters_integer == 0:
        message += 'there are no new chapters you can read.'
    elif new_chapters_integer == 1:
        message += 'there is 1 more chapter you can read!'
    else:
        message += f'there are {new_chapters_integer} more chapters you can read!'
    
    print(message)

def get_processed_core_page(selenium_object, 
                            good_css_selector, 
                            url_to_print, 
                            chapters_already_read, 
                            good_css_selector_num=0, 
                            bad_css_selector='.not-found-content'):
    
    latest_chapter_text = get_latest_chapter_text(selenium_object=selenium_object, 
                                                  good_css_selector=good_css_selector, 
                                                  url_to_print=url_to_print, 
                                                  good_css_selector_num=good_css_selector_num, 
                                                  bad_css_selector=bad_css_selector)
    if latest_chapter_text is not None:
        new_chapters_count = get_new_chapters_integer(latest_chapter_text=latest_chapter_text, 
                                                      chapters_already_read=chapters_already_read)
        print_output_message(url_to_print=url_to_print, 
                             new_chapters_integer=new_chapters_count)


# # Selenium Based Manga Monitoring

# In[ ]:


get_user_input()

selenium_spider, virtual_display = start_or_reload_display(driver_name='Chrome', detach_display=True)

urls_batch_1 = ['https://1stkissmanga.io', 
                'https://zinmanga.com', 
                'https://coffeemanga.com', 
                'https://kunmanga.com']

for url in urls_batch_1:
    
    direct_link_to_manga = f'{url}/manga/{user_input_1_adapted}'
    selenium_spider.get(direct_link_to_manga)
    
    list_of_heading_elements_found = selenium_spider.find_elements("css selector", '.heading')
    
    if len(list_of_heading_elements_found) > 0 and (
       list_of_heading_elements_found[0].text != 'Oops! page not found.'):
        
        get_processed_core_page(selenium_object=selenium_spider, 
                                good_css_selector='li.wp-manga-chapter:nth-child(1) > a:nth-child(1)', 
                                url_to_print=url, 
                                chapters_already_read=user_input_2, 
                                good_css_selector_num=0, 
                                bad_css_selector='.not-found-content')
        
    else:
        
        user_input_1_readapted = '+'.join(user_input_1.lower().split())
        searching_url = url + f'/?s={user_input_1_readapted}&post_type=wp-manga'
        
        selenium_spider.get(searching_url)
        
        get_processed_core_page(selenium_object=selenium_spider, 
                                good_css_selector='span.font-meta:nth-child(2)', 
                                url_to_print=url, 
                                chapters_already_read=user_input_2, 
                                good_css_selector_num=0, 
                                bad_css_selector='.not-found-content')

print()

selenium_spider.quit()
if virtual_display is not None:
    virtual_display.stop()


#  

#  

#  
