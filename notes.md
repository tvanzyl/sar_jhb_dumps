Reference
https://towardsdatascience.com/getting-started-with-snap-toolbox-in-python-89e33594fa04
https://asf.alaska.edu/wp-content/uploads/2019/05/generate_insar_with_s1tbx_v5.4.pdf
http://step.esa.int/docs/tutorials/S1TBX%20TOPSAR%20Interferometry%20with%20Sentinel-1%20Tutorial_v2.pdf

https://www.esa.int/esapub/tm/tm19/TM-19_ptA.pdf
> Interferograms with very small perpendicular baseline values (< 30 m), though easy to unwrap, are almost useless due to their high sensitivity to phase noise and atmospheric effects. 
> Check https://forum.step.esa.int/t/base-line-in-snap/6237 for the tool to compare

Install
* install latest snap
* install snaphu
* conda create --name snap python=3.5
* conda install jupyter
* http://step.esa.int/docs/tutorials/SNAP_CommandLine_Tutorial.pdf
    * snap --nosplash --nogui --modules --update-all --refresh
* beware versions of python that are supported

# Lessons Learnt
## Snap GUI
* when doing split make sure to select the bands, highlight in yellow
* always make sure selections are done

### Snap CmdLine Update
https://senbox.atlassian.net/wiki/spaces/SNAP/pages/30539785/Update+SNAP+from+the+command+line

# Geographic tools
https://www.latlong.net/lat-long-dms.html
http://arthur-e.github.io/Wicket/sandbox-gmaps3.html
https://apps.sentinel-hub.com/eo-browser/?zoom=12&lat=-22.81733&lng=-43.78704&themeId=DEFAULT-THEME&datasetId=S1&fromTime=2021-01-18T00%3A00%3A00.000Z&toTime=2021-01-18T23%3A59%3A59.999Z&layerId=6_VV_DB_ORTHORECTIFIED&visualizationUrl=https%3A%2F%2Feocloud.sentinel-hub.com%2Fv1%2Fwms%2F6a6b787f-0dda-4153-8ae9-a1729dd0c890


# Download the images from:

## JHB
https://search.asf.alaska.edu/#/?zoom=9.699250560565591&center=27.691824,-26.910893&polygon=POLYGON((27.6914%20-26.3074,28.2651%20-26.3107,28.128%20-26.1377,27.7958%20-26.219,27.6914%20-26.3074))&start=2018-11-01T00:00:00Z&end=2020-12-01T23:59:00Z&resultsLoaded=true&granule=S1A_IW_SLC__1SDV_20201122T164650_20201122T164717_035363_0421C7_2335-SLC&flightDirs=Ascending&beamModes=IW&productTypes=SLC

## RIO
https://search.asf.alaska.edu/#/?zoom=8.748863213168661&center=-43.570862,-23.446499&polygon=POINT(-43.7613%20-22.7912)&start=2017-11-30T00:00:00Z&end=2020-12-01T23:59:00Z&resultsLoaded=true&granule=S1B_IW_SLC__1SDV_20201201T082148_20201201T082215_024506_02E9BB_170B-SLC&flightDirs=Descending&beamModes=IW&productTypes=SLC

## Istanbul
https://search.asf.alaska.edu/#/?zoom=8.380138087789478&center=28.876778,40.109126&polygon=POINT(29.096%2041.0956)&resultsLoaded=true&granule=S1B_IW_SLC__1SDV_20191031T040538_20191031T040605_018714_02345E_12E9-SLC&searchType=Geographic%20Search&start=2017-12-01T00:00:00Z&end=2020-12-31T23:59:00Z&productTypes=SLC&beamModes=IW&path=138-&frame=456-


Get all SBAS pairs:
https://search.asf.alaska.edu/#/?searchType=SBAS%20Search&zoom=7.297397670585765&center=25.706626,-28.233405&resultsLoaded=true&granule=S1A_IW_SLC__1SDV_20201216T164650_20201216T164716_035713_042DE5_3381-SLC&master=S1A_IW_SLC__1SDV_20171102T164632_20171102T164659_019088_0204A3_D54A&perp=151to&temporal=36to

Create Interferograms 
1. Use the GPT tool and the graphs
    1. https://asf.alaska.edu/how-to/data-recipes/create-an-interferogram-using-esas-sentinel-1-toolbox/    
    2. http://step.esa.int/docs/tutorials/SNAP_CommandLine_Tutorial.pdf
    3. https://blogs.fu-berlin.de/reseda/s2-bulk-preprocessing/ 
    4. Export to SNAPHU
2. Use SNAPHU to unwrap the interferograms
    1. https://asf.alaska.edu/how-to/data-recipes/phase-unwrap-an-interferogram/
3. Import unwrapped interferograms into SNAP?
4. Create a deformation map
    1. https://asf.alaska.edu/how-to/data-recipes/interpreting-an-unwrapped-interferogram-creating-a-deformation-map/

gpt TOPSAR\ Coreg\ Interferogram\ VV\ IW\ 2_3\ B\ 8_9.xml -Ptarget=../dinsar/20180101_20180113.dim -Pmaster=../S1A_IW_SLC__1SDV_20180101T164630_20180101T164656_019963_021FFB_2D88.zip -Pslave=../S1A_IW_SLC__1SDV_20180113T164629_20180113T164656_020138_022584_64C9.zip



# GDP
> NAH: https://data.oecd.org/gdp/quarterly-gdp.htm#indicator-chart

https://data.imf.org/regular.aspx?key=62771448


