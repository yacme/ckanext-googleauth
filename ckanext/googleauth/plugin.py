'''This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

                    GNU AFFERO GENERAL PUBLIC LICENSE
                       Version 3, 19 November 2007

 Copyright (C) 2007 Free Software Foundation, Inc. <http://fsf.org/>
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.'''



# coding=utf-8
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import json
import uuid
import pylons
import pylons.config as config
import ckan.lib.helpers as helpers
import requests
import re



#get 'ckan.googleauth_clientid' from ini file
def get_clientid():
    return config.get('ckan.googleauth_clientid', '')


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



class GoogleauthPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IAuthenticator)
    plugins.implements(plugins.ITemplateHelpers)



    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'googleauth')


    #declare new helper functions
    def get_helpers(self):
        return {'googleauth_get_clientid': get_clientid,
		'googleauth_get_hosted_domain': get_hosted_domain}



    #verify email address within token
    def verify_email(self, token):
        res = requests.post('https://www.googleapis.com/oauth2/v3/tokeninfo?id_token='+token, verify=True)

        if res.ok:
                is_email_verified=json.loads(res.content)
                if is_email_verified['email_verified'] == 'true':
                        email_verified = is_email_verified['email']
                        return email_verified
                else:
                        raise GoogleAuthException(is_email_verified)
        else:
                raise GoogleAuthException(res)



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

	if 'id_token' in params:
		try:
			mail_verified = self.verify_email(params['id_token'])
		except GoogleAuthException, e:
			toolkit.abort(500)

		user_account = email_to_ckan_user(mail_verified)

		user_ckan = self.get_ckanuser(user_account)

		if not user_ckan:
			user_ckan = toolkit.get_action('user_create')(
                    				context={'ignore_auth': True},
                    				data_dict={'email': mail_verified,
                               			'name': user_account,
                               			'password': self.get_ckanpasswd()})

		pylons.session['ckanext-google-user'] = user_ckan['name']
        	pylons.session['ckanext-google-email'] = mail_verified

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



    def abort(self):
	self._logout_user()
