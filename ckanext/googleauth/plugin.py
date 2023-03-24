# coding=utf-8
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.lib.plugins import DefaultTranslation
import json
import uuid

from google.oauth2 import id_token
from google.auth.transport import requests
import pylons
import pylons.config as config
import ckan.lib.helpers as helpers
import requests
import re



#get 'ckan.googleauth_clientid' from ini file
def get_clientid():
    return config.get('ckan.googleauth_clientid', '')


def get_loginuri():
    site_url = config.get('ckan.site_url')
    return '%s/user/login' % (site_url)


#get ckan.googleauth_hosted_domain from ini file
def get_hosted_domain():
    return config.get('ckan.googleauth_hosted_domain', '')


def omit_domain():
    return toolkit.asbool(
        config.get('ckan.googleauth_omit_domain_from_username',
                   False))


def email_to_ckan_user(email):
    if omit_domain():
        email = email.rsplit('@', 2)[0]

    return re.sub('[^A-Za-z0-9]+', '_', email)


class GoogleAuthException(Exception):
    pass



class GoogleauthPlugin(plugins.SingletonPlugin, DefaultTranslation):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IAuthenticator)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.ITranslation)


    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')


    #declare new helper functions
    def get_helpers(self):
        return {'googleauth_get_clientid': get_clientid,
                'googleauth_get_loginuri': get_loginuri,
		'googleauth_get_hosted_domain': get_hosted_domain}



    #if exist returns ckan user
    def get_ckanuser(self, user):
    	import ckan.model

        user_ckan = ckan.model.User.by_name(user)

        if user_ckan:
            user_dict = toolkit.get_action('user_show')(data_dict={'id': user_ckan.id})
            return user_dict
        else:
            return None



    #generates a strong password
    def get_ckanpasswd(self):
        import datetime
        import random

        passwd = str(random.random())+ datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")+str(uuid.uuid4().hex)
        passwd = re.sub(r"\s+", "", passwd, flags=re.UNICODE)
        return passwd



    def _logout_user(self):
        #import pylons

	#to revoke the Google token uncomment the code below

	#if 'ckanext-google-accesstoken' in pylons.session:
	#    atoken = pylons.session.get('ckanext-google-accesstoken')
	#    res = requests.get('https://accounts.google.com/o/oauth2/revoke?token='+atoken)
	#    if res.status_code == 200:
	#    	del pylons.session['ckanext-google-accesstoken']
	#    else:
	#	raise GoogleAuthException('Token not revoked')
        if 'ckanext-google-user' in pylons.session:
            del pylons.session['ckanext-google-user']
        if 'ckanext-google-email' in pylons.session:
            del pylons.session['ckanext-google-email']
        pylons.session.save()



    #at every access the email address is checked. if it is authorized ckan username is created and access is given
    def login(self):

    	params = toolkit.request.params

        if 'credential' in params:
            # https://developers.google.com/identity/gsi/web/reference/js-reference#CredentialResponse
            # https://developers.google.com/identity/gsi/web/guides/verify-google-id-token
            id_info = id_token.verify_oauth2_token(
                params['credential'], requests.Request(), get_clientid()
            )
            if id_info.get('hd', '') != get_hosted_domain():
                toolkit.abort(500)

            email = id_info['email']
            user_account = email_to_ckan_user(email)

            user_ckan = self.get_ckanuser(email)

            if not user_ckan:
                user_ckan = toolkit.get_action('user_create')(
                                        context={'ignore_auth': True},
                                        data_dict={'email': email,
                                            'name': user_account,
                                            'password': self.get_ckanpasswd()})

            pylons.session['ckanext-google-user'] = user_ckan['name']
            pylons.session['ckanext-google-email'] = email

            #to revoke the Google token uncomment the code below
            #pylons.session['ckanext-google-accesstoken'] = params['token']
            pylons.session.save()

    #if someone is logged in will be set the parameter c.user
    def identify(self):
        user_ckan = pylons.session.get('ckanext-google-user')
        if user_ckan:
            toolkit.c.user = user_ckan



    def logout(self):
        self._logout_user()

    def abort(self, status_code=None, detail='', headers=None, comment=None):
        if status_code == 403 or status_code == 404:
            return (status_code, detail, headers, comment)
        self._logout_user()

        return (status_code, detail, headers, comment)
