#ckanext-googleauth

CKAN extension for use Google as authentication authority.

##Requirements

ckanext-googleauth was created and tested in CKAN 2.5.1. The functioning with other versions of CKAN is not guaranteed.

To use this extension you must register your application with Google to obtaining authorization credentials. For more information please visit https://developers.google.com/identity/sign-in/web/devconsole-project 

##Installation

To install ckanext-googleauth:

1. Clone this repository and run:	

    <code>python setup.py install</code>

2. Configure Client ID and (optionally) Hosted Domain (See "Config Settings" section)

3. Add ``googleauth`` to the ``ckan.plugins`` setting in your CKAN config file (by default the config file is located at
   ``/etc/ckan/default/production.ini``).

4. Restart CKAN.

##Config Settings

In your config file (``/etc/ckan/default/production.ini``) add these properties:

* ``ckan.googleauth_clientid = client_id_value`` (REQUIRED). It contains the Client ID. For more information on how to create Client ID please visit https://developers.google.com/identity/sign-in/web/devconsole-project.

* ``ckan.googleauth_hosted_domain = hosted_domain_value`` (OPTIONAL) It contains the domain authorized to authenticate. If it isn't set you will have access with any Google Account Credentials.

##Development Installation

To install ckanext-googleauth for development, activate your CKAN virtualenv and do::
	
    git clone https://github.com/yacme/ckanext-googleauth.git
    cd ckanext-googleauth
    python setup.py develop

##License
This extension is licensed under the terms of GNU AFFERO GENERAL PUBLIC LICENSE Version 3.

##Credits
This extension was deleveloped with the support of ARPA Emilia Romagna.



