import scrapy
 
#creating class that will inherite from scrapy.Spider
class ImdbSpider(scrapy.Spider):
    
    name = 'imdb_spider' #each spider
    
    start_urls = ['https://www.imdb.com/title/tt4633694/'] #the urls that user wants to look at
    
    def parse(self, response):
        
        '''
        Takes every URL of film on IMDB specified in ImdbSpider.start_urls 
        to be redirected on its subpage titled as 'Full Cast & Crew'.
        
        '''
        
        #the first parsing method
        for url in self.start_urls:
            
            # it adds the path to 'Full Cast & Crew' subpage from the main URL
            url += 'fullcredits/' if url[-1] == '/' else '/fullcredits'
            yield scrapy.Request(url=url, 
                                 callback=self.parse_full_credits)
    
    def parse_full_credits(self, response):
        
        '''
        Starts with page titled as 'Full Cast & Crew' by particular filmpage 
        as a result of ImdbSpider.parse method.
        
        '''
        
        #creating list with parsed paths to actors subpages from page with credits
        paths_to_actors_list = [a.attrib["href"] for a in response.css("td.primary_photo a")]
        
        #looking at every actor
        for path_to_actor in paths_to_actors_list:
            yield scrapy.Request(url='https://www.imdb.com'+path_to_actor, 
                                 callback=self.parse_actor_page)
    
    def parse_actor_page(self, response):
        
        '''
        Starts with a page of particular actor by the same filmpage 
        as a result of both ImdbSpider.parse and ImdbSpider.parse_full_credits methods.
        
        '''
        
        #on actor's page finding actor's name in span tag inside h1-header and get it clean
        actor_name = response.css("h1.header span::text").get()
        
        #define filmography block as the separate response-element for Scrapy to parse
        element = response.css("div.filmo-category-section")
        
        #note: movie titles on actor's page are in bold, therefore, I can extracte them as strings using regex method in Scrapy
        bold_rows = element.css("div.filmo-row").re('<b>.*</b>') #list of strings
        
        #taking every title element from actor's films block
        for row in bold_rows:
            
            #extracting every movie name directly by wraping in scrapy.Selector every such sring from bold_rows to get clean titles as text
            movie_or_TV_name = scrapy.Selector(text=row).css('::text').get()
            
            #this finalizes the work of parsing appending the needed output data
            yield {"actor": actor_name, 
                   "movie_or_TV_name": movie_or_TV_name}
