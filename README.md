# Metallum Scrapper

This is an attempt on scrapping Metallum Bands belonging to certain genres and their Discography pages.
Currently, this is development is still in it's primitvie stages. However, it has given me what I wanted, that is Disgographies of 'Funeral Doom' bands.

As I keep doing the refinements and tests over the published version, the process is bound to improve. And It can be extended to other genres. Expect a better documentations codes and process in future.

## What you get at end of the run

* Bands and their meta information
* Their Discograpies and Reivew numbers

## Future Improvements

* **Discog Reivew Summaries**: Although, the code includes steps to pull one-level-further scrapping of review pages, during the end-to-end, it kept failing for some reason. I will keep looking into that. It's important to me personally to summarize what the reviews are mentioning when they are describing a record. Although, I imagine it may not matter so much to the end user.
* **A webbased API**: There is learning curve involved, and I will try to create a web application (simple, of course) for better user experience.

## Essential Requirements
```Python
selenium==4.21.0
pandas==2.2.1
```

You would also require latest version of **Chrome** 


