def contains_url(message) :
    try :
        message.message_create["message_data"]["entities"]["urls"][0]["expanded_url"]
        link_exists = True
        print("link exists in message")
        return link_exists
    except :
        link_exists = False
        print("link does not exist in " + message.id)
        return link_exists

def url_already_exists(message, messages) :
    if messages.count_documents({
        "link" : message.message_create["message_data"]["entities"]["urls"][0]["expanded_url"]},
        limit = 1) == 1 :
            url_in_db = True
            print("link exists in db")
            return url_in_db
    else :
        url_in_db = False
        print("link does not exist in db for " + message.id)
        return url_in_db

def return_search(recipient_id, message, messages, api) :
    try :
        message_string = ""
        for item in messages.find() :
            message_string = message_string + item["link"] + " "
        api.send_direct_message(recipient_id, message_string)
        api.destroy_direct_message(message.id)
        print("search complete")
    except :
        print("search failed to complete")


async def amazon_main(driver, link, WebDriverWait, EC, By, api, links_array) :
    driver.get(link)
    try:
        wait_available = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "html"))
        )
        isPresent = driver.find_elements(By.XPATH, "//*[@id='add-to-cart-button']")
        if len(isPresent) < 1 :
            print(link + " not in stock")
        else :
            print(link + " is in stock!")
            await api.update_status("Item is back in stock!" + link)
            links_array.pop(link)
    except:
        print("Error finding element in " + link)

async def walgreens_main(driver, link, WebDriverWait, EC, By, api, links_array) :
    driver.get(link)
    try:
        wait_available = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "html"))
        )
        isPresent = driver.find_elements(By.XPATH, "//*[@id='receiveing-addToCartbtn']")
        if len(isPresent) < 1 :
            print(link + " not in stock")
        else :
            print(link + " is in stock!")
            await api.update_status("Item is back in stock!" + link)
            links_array.pop(link)
    except:
        print("Error finding element")

async def seaworld_main(driver, link, WebDriverWait, EC, By, api, links_array) :
    driver.get(link)    
    try:
        wait_available = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "html"))
        )
        isPresent = driver.find_elements(By.XPATH, "//span[contains(text(), 'Add to Cart')]")
        if len(isPresent) < 1 :
            print(link + " not in stock")
        else :
            print(link + " is in stock!")
            await api.update_status("Item is back in stock!" + link)
            links_array.pop(link)
    except:
        print("Error finding element")

async def walmart_main(driver, link, WebDriverWait, EC, By, api, links_array) :
    driver.get(link)    
    try:
        wait_available = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "html"))
        )
        isPresent = driver.find_elements(By.XPATH, "//span[contains(text(), 'Add to Cart')]")
        if len(isPresent) < 1 :
            print(link + " not in stock")
        else :
            print(link + " is in stock!")
            await api.update_status("Item is back in stock!" + link)
            links_array.pop(link)
    except:
        print("Error finding element")

async def cedar_main(driver, link, WebDriverWait, EC, By, api, links_array) :
    driver.get(link)    
    try:
        wait_available = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "html"))
        )
        isPresent = driver.find_elements(By.XPATH, "//*[@id='AddToCartText']")
        if len(isPresent) < 1 :
            print(link + " not in stock")
        else :
            print(link + " is in stock!")
            await api.update_status("Item is back in stock!" + link)
            links_array.pop(link)
    except:
        print("Error finding element")