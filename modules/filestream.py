from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import os
import time
import config

# URL = "http://filestream.me"
URL = "https://chiko.filestream.me/?jakoredirect=no"

def remove_stupid_popup():
    try: driver.find_element_by_class_name("modal-footer").click()
    except: pass


pw = config.filestream["pw"]
user = config.filestream["user"]
pcurl = config.filestream["pcurl"]
download_folder = config.filestream["download_folder"]

def get_magnet_from_tpb(url):
    driver = webdriver.Chrome()
    driver.get(url)
    amagnet = driver.find_element_by_xpath("//*[starts-with(@href,'magnet')]")
    magnet_link = amagnet.get_attribute("href")
    driver.quit()
    return magnet_link



def get_filename_and_link(magnet):

    driver = webdriver.Chrome()
    driver.get(URL)
    elem = driver.find_element_by_id("mylogin")
    time.sleep(1)
    elem.send_keys(Keys.RETURN)
    elem = driver.find_element_by_class_name("input1")
    time.sleep(1)
    elem.send_keys(user)
    elem = driver.find_element_by_name("password")
    time.sleep(1)
    elem.send_keys(pw)
    time.sleep(2) # javascript generates the next element, so we wait until the transition completes before we can click
    elem = driver.find_element_by_id("sbmtlgn")
    elem.click()

    elem = driver.find_element_by_class_name("button_container_Addbut")
    elem.send_keys(magnet)
    elem = driver.find_element_by_class_name("button1")
    elem.click()

    time.sleep(2)
    remove_stupid_popup()

    torrent_rows = driver.find_elements_by_xpath("//*[starts-with(@id,'stn_')]")

    status = ""
    for i in range(100):
        status = driver.find_elements_by_xpath("//*[starts-with(@id,'sts_')]")[0].text
        print "Iteration %i with status: %s" % (i, status)
        if status == "complete": break
        time.sleep(30)

    torrent_rows[0].click()

    time.sleep(2)
    remove_stupid_popup()

    # drop first row stuff because that is the 'directory up' button
    torrent_rows = driver.find_elements_by_xpath("//*[starts-with(@id,'stn_')]")[1:]
    torrent_sizes = map(lambda x: x.text, driver.find_elements_by_xpath("//*[starts-with(@id,'stsiz_')]")[1:])
    torrent_files = driver.find_elements_by_xpath("//*[starts-with(@onclick,'showDownload')]")

    sizes = []
    for size in torrent_sizes:
        try: size = float(size.replace("KB","e3").replace("MB","e6").replace("GB","e9"))
        except: size = 0.0
        sizes.append(size)
    idx = sizes.index(max(sizes))    
    # idx = sizes.index(sorted(sizes)[-2])     # second largest for debugging

    download_link = torrent_files[idx].get_attribute("onclick").split("CWND('")[1].split("', ")[0].replace("http:","https:")
    torrent_name = torrent_rows[idx].text

    driver.quit()

    return download_link, torrent_name


def download_parallel(url, output):
    outfile = "%s/%s" % (download_folder, output)

    # return if already downloaded
    if os.path.isfile(outfile): return outfile
    if not os.path.isdir(download_folder): os.makedirs(download_folder)
    print "downloading %s (%s) to %s/" % (url, output, download_folder)
    try:
        cmd = "%s '%s' '%s/%s'" % (pcurl, url, download_folder, output)
        print cmd
        os.system(cmd)
    except:
        pass

    if os.path.isfile(outfile): return outfile
    else: return None

def sanitize(txt):
    # sanitize output or else pcurl will do weird things
    return txt.replace(" ","_").replace(")","_").replace("(","_")
    

def get(links):
    for link in links:
        print link
        magnet =  get_magnet_from_tpb(link)
        # magnet = "magnet:?xt=urn:btih:445d1c83619750b2495bd791d05aad5c9242ddff&dn=The.Hunger.Games.Mockingjay.Part.2.2015.BRRip.720p-PRiSiSTiNE&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A%2F%2Fopen.demonii.com%3A1337&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A6969&tr=udp%3A%2F%2Fexodus.desync.com%3A6969"
        print magnet

        url, output = get_filename_and_link(magnet)
        # url, output = "https://fs-cache-1.filestream.me/stream/56eb991d175c56bb4c85c8d3?st=v97wFI0c8gbFkb-HeRshXQ&e=1458885558&u=1prxmWvbdk/AGRXcimeg9akPuNrdnDs1GAVmVDdAeg==", "Sample.mp4"

        output = sanitize(output)
        print url, output

        out = download_parallel(url, output)
        if out:
            print "Successfully downloaded %s" % out
        else:
            print "ERROR in downloading"


if __name__=='__main__':
    url = "https://thepiratebay.se/torrent/13837693"
    # magnet =  get_magnet_from_tpb(url)
    magnet = "magnet:?xt=urn:btih:445d1c83619750b2495bd791d05aad5c9242ddff&dn=The.Hunger.Games.Mockingjay.Part.2.2015.BRRip.720p-PRiSiSTiNE&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A%2F%2Fopen.demonii.com%3A1337&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A6969&tr=udp%3A%2F%2Fexodus.desync.com%3A6969"
    print magnet

    # url, output = get_filename_and_link(magnet)
    url, output = "https://fs-cache-1.filestream.me/stream/56eb991d175c56bb4c85c8d3?st=v97wFI0c8gbFkb-HeRshXQ&e=1458885558&u=1prxmWvbdk/AGRXcimeg9akPuNrdnDs1GAVmVDdAeg==", "Sample.mp4"
    print url, output


    out = download_parallel(url, output)
    if out:
        print "Successfully downloaded %s" % out
    else:
        print "ERROR in downloading"

