# Image-Editor-Site
A website allowing users to edit images.

The website stores a cookie containing a session id. This is used to identify users after leaving the site to resume editing.
The cookie and associated images are deleted after 1 week of inactivity, or 2 weeks max, or every month. Maximum undos/redos is 5.

A session cleaner script runs after a set time period to remove any keys without images, or remove any folders without keys. Also, it deletes
after inactivity period and max period.

I have overwritten the default method to delete sessions by creating my own SessionStore class (handles interaction with the session database),
so that when sessions are removed from the database, the images are too.

Client uses AJAX calls to send the server data about what to edit, and after the server has edited and rearranged image files, returns a
link to the image, for the client to reload.

Custom middleware is included to check if cookies are enabled. If the cookiestest = true cookie isn't in the request, middleware redirects to
a cookie check page, where a test cookie is set, and if it isn't there on the next request, asks users to enable cookies.
