/*This program is free software: you can redistribute it and/or modify
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
 of this license document, but changing it is not allowed.*/


var googleUser = {};
var cid = getMetaContent('google-signin-client_id');
var hd = getMetaContent('google-signin-hosted_domain');
var startApp = function() {
  gapi.load('auth2', function(){
    auth2 = gapi.auth2.init({
      client_id: cid,
      cookiepolicy: 'single_host_origin',
      hosted_domain: hd
    });
    var button = document.getElementById('g-signin-button');
    if (button) {
        attachSignin(button);
    }
  });
};



function attachSignin(element) {
  auth2.attachClickHandler(element, {},
      function(googleUser) {

        var profile = googleUser.getBasicProfile();
        var name = profile.getName();
        var email = profile.getEmail();

	var response = googleUser.getAuthResponse();
	var id_token = response['id_token'];
	var access_token = response['access_token'];

	$.ajax({
	type: 'POST',
       	url:'/user/login',
	data: {name: name, email: email, id_token: id_token, token: access_token},
       	success: function(res, status, xhr) {
        	window.location.replace("/dashboard");
       	},
       	error: function(xhr, status, err) {
         	alert("Login failure: " + err);
       }
     });

      }, function(error) {


      });

}



/*get content from meta tag*/
function getMetaContent(propName) {
  var metas = document.getElementsByTagName('meta');
  for (i = 0; i < metas.length; i++) {
	if (metas[i].getAttribute("name") == propName) {
		return metas[i].getAttribute("content");
	}
  }
  return "";
}
