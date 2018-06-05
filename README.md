GAE Atuin CMS
=============

GAE Atuin CMS is a Content Management System to build cloud-based websites that
rely on top of the [GAE Atuin Web Framework]. This CMS is designed to be deployed on 
[Google App Engine] and to use the [Google Datastore].

Features
--------

- The good famous [Flask] web framework
- i18n with [Babel]
- Google Auth support and decorators
- The [atuin-tools] development environment for
	
	- SASS preprocessing
	- CSS concatenation and minification
	- JS concatenation, minification and obfuscation
	- Images optimization
	- Translations management (extraction, compilation )
	- Pre-deploy preparation task
	- Deploy procedure
 
Dependencies
------------

- docker-compose

Quick start
-----------

```bash
git clone git@github.com:atuinframework/gae-atuin-cms.git

cd gae-atuin-cms

# install dependencies
docker-compose run tools gulp update

docker-compose up
```


Links
-----

- GAE Atuin CMS [documentation]
- [Atuin Web Framework]


[GAE Atuin Web Framework]: https://github.com/atuinframework/gae-atuin
[Google App Engine]: https://cloud.google.com/appengine/
[Google Datastore]: https://cloud.google.com/datastore/
[Flask]: https://github.com/pallets/flask
[Babel]: http://babel.pocoo.org/en/latest/
[atuin-tools]: https://github.com/atuinframework/atuin-tools
[documentation]: http://gae-atuin-cms.rtfd.io/
[Atuin Web Framework]: https://github.com/atuinframework
