MeowURL URL Shortener & Pastebin
=================================

Not-So-Simple URL Shortener that has lots of functions

MeowURL is an URL Shortener that combines the functions of a regular shortener and pastebin. It is written in Python 3 and Flask, and is designed to deploy to Heroku. It is also pip packaged so pip can be used to install the package from git. It also requires an SQL Server (or SQLite) and Memcache.

MeowURL is still under development and is not expected to finish soon. It is not designed for large-scale use as dealing with spam is not planned. It has an invite system so the site can be closed for personal use and invite only.

===========================
Why another URL Shortener?
===========================

Yes, there are already lots of URL Shorteners one can use. However I see non of them meets my need. I have been "dreaming" of this project for a long time, I just don't have the ability to implement it (PHP's a pain for me). Then I decided to write it in Python.

In my design a good URL shortener would be:

* Short URL **easy to write down** or talk on the phone. That means no mix of uppercase and lowercase letters, because they are so confusing.
* URL **editable** with or without login. If you tell your friend a link, you can update it when the original link's broken without telling your friend again.
* Twitter-like **feed** for each user. Show your friend all the awesome links you got.
* Not only URLs, but also **text**. Why you can only paste a link? You can also shorten a paragraph you like.
* Not only text, but also **Markdown**. Format a paragraph as you wish, then publish it in a short link.
* Not only text, Markdown, but also **code**. Yes, it's exactly a pastebin! (Like Github Gists, too)
* It's not over, share **files** as well! Actually, it's share links of a file or a folder, but you can put as many mirrors as you like. DDL, torrent, Sync, all together, but best of all it's editable, so if the link's down, you can always update it easily.
* All contents are **password protectable**. Require a password to view the content.

Eventually if I'm able to make it, MeowURL would have all the functions, plus maybe a few other fun functions like check-in. （猫猫签到 You won't understand why）

======================
Warning: Experimental
======================

This is an experimental package! Data could be corrupt across updates. Do not use on production server yet.

=====================
Copyright
=====================

  The MIT License (MIT)

  Copyright (c) 2017 Dexter MaomiHz

  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
