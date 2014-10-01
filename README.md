appraiser
=========

A data project to see if we can predict housing prices in select areas of the Bay Area

Take Aways
----------

 * It's really easy to craft an architecture that can be limiting to your overall project
   Gather all your data, store it somewhere (in unadulterated form), and then filter/modify it.
   Do not store your data in filtered form. You are just asking to refactor your work.
 * It's hard to engineer features. With something like housing prices you have so many variables
   some which are difficult to discern from a machines perspective. For example is the house near
   a highway or in a dilapidated industrial area, well we don't necessarily know that and it is
   hard to tell from the basic data given to us through zillow. Complete feature representation
   for homes at least should probably come from a variety of sources, not the least user surveys
   about an area.
