import secrets
import time
import random
import requests
import string
import json
from user_agent import generate_user_agent as ua
from faker import Faker
crf=secrets.token_hex(16)
ti=str(time.time()).split('.')[0]
se=requests.Session()
Fk=Faker()
def Twitter(email):
	if '@' not in email:
		email=email+'@gmail.com'
	else:
		pass
	he={'user-agent':str(ua())}
	params = {
		 'email': email,
		}
	re =requests.get('https://api.x.com/i/users/email_available.json',params=params,headers=he,).text
	if '"taken":true' in re:
		return True
	else:
		return False
def users_instagram(user):
	url="https://www.instagram.com/api/v1/users/check_username/"
	payload = {
		'username': user,
				  }
	he = {
		'User-Agent': str(ua()),
		'x-csrftoken':crf}
	re= requests.post(url, headers=he,data=payload).text
	if '"available":true' in re:
		return True
	else:
		return False

def info(username):
	if '@' in username:
		username=username.split('@')[0]
	headers = {
		    'user-agent': str(ua()),
		    'x-csrftoken': crf,
		    'x-ig-app-id': '936619743392459',
		}
		
	params = {
		    'username': username,
		}
		
	re = requests.get(
		    'https://www.instagram.com/api/v1/users/web_profile_info/',
		    params=params,
		    headers=headers,
		).json()
	Name=re['data']['user']['full_name']
	followers=re['data']['user']['edge_followed_by']['count']
	follow=re['data']['user']['edge_follow']['count']
	Id=re['data']['user']['id']
	Bio=re['data']['user']['biography']
	try:
		headers = {
	    'X-Pigeon-Session-Id': '50cc6861-7036-43b4-802e-fb4282799c60',
	    'X-Pigeon-Rawclienttime': '1700251574.982',
	    'X-IG-Connection-Speed': '-1kbps',
	    'X-IG-Bandwidth-Speed-KBPS': '-1.000',
	    'X-IG-Bandwidth-TotalBytes-B': '0',
	    'X-IG-Bandwidth-TotalTime-MS': '0',
	    'X-Bloks-Version-Id': '009f03b18280bb343b0862d663f31ac80c5fb30dfae9e273e43c63f13a9f31c0',
	    'X-IG-Connection-Type': 'WIFI',
	    'X-IG-Capabilities': '3brTvw==',
	    'X-IG-App-ID': '567067343352427',
	    'User-Agent': 'Instagram 100.0.0.17.129 Android (29/10; 420dpi; 1080x2129; samsung; SM-M205F; m20lte; exynos7904; en_GB; 161478664)',
	    'Accept-Language': 'en-GB, en-US',
	     'Cookie': 'mid=ZVfGvgABAAGoQqa7AY3mgoYBV1nP; csrftoken=9y3N5kLqzialQA7z96AMiyAKLMBWpqVj',
	    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
	    'Accept-Encoding': 'gzip, deflate',
	    'Host': 'i.instagram.com',
	    'X-FB-HTTP-Engine': 'Liger',
	    'Connection': 'keep-alive',
	    'Content-Length': '356',
	}
		data = {
	    'signed_body': '0d067c2f86cac2c17d655631c9cec2402012fb0a329bcafb3b1f4c0bb56b1f1f.{"_csrftoken":"9y3N5kLqzialQA7z96AMiyAKLMBWpqVj","adid":"0dfaf820-2748-4634-9365-c3d8c8011256","guid":"1f784431-2663-4db9-b624-86bd9ce1d084","device_id":"android-b93ddb37e983481c","query":"'+username+'"}',
	    'ig_sig_key_version': '4',
	}	
		res = requests.post('https://i.instagram.com/api/v1/accounts/send_recovery_flow_email/',headers=headers,data=data,)
		r = res.json()['email']
		if r.split('@')[1]=='gmail.com':
			rr=r.split('@')[0]
			if rr[0]==username[0] and rr[-1]==username[-1]:
				rest=r
					
			else:
				rest=False
		else:
			rest=False
	except :
		rest = None
	return Name,username,followers,follow,Id,Bio,rest

def check_instagram(email):
	if '@' not in email:
		email+'@gmail.com'
	elif '@' in email:
		pass
	he = {
		    'user-agent': str(ua()),
		    'x-csrftoken': crf,
		    'x-ig-app-id': '936619743392459',
		}
	data = {
		    'email': email,
		}
	re = requests.post('https://www.instagram.com/api/v1/web/accounts/check_email/',headers=he,
		data=data,
		).text
	if "email_is_taken" in re:
		return True
	else:
		return False
def gmail(username):
	name=str(Fk.name())
	year=str(random.randrange(1980,2010))
	month=str(random.randrange(1,12))
	day=str(random.randrange(1,28))
	if '@'  in username:
		username=username.split('@')[0]
	if '@'  not in username:
		username=username
	headers = {
	    'authority': 'accounts.google.com',
	    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
	    'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
	    'user-agent': str(ua()),
	    'x-chrome-connected': 'source=Chrome,eligible_for_consistency=true',
	    'x-client-data': 'CMbxygE=',
	}
	params = {
	    'biz': 'false',
	    'continue': 'http://support.google.com/mail/answer/56256?hl=ar',
	    'ec': 'GAlAdQ',
	    'flowEntry': 'SignUp',
	    'flowName': 'GlifWebSignIn',
	    'hl': 'ar',
	    'authuser': '0',
	}
	
	res = se.get('https://accounts.google.com/lifecycle/flows/signup', params=params,headers=headers)
	
	TL=res.url.split('TL=')[1].split()[0]
	at=res.text.split('"SNlM0e":"')[1].split('"')[0].replace(':','%3A')
	xr=res.text.split('"Qzxixc":"')[1].split('"')[0]
	
	
	headers = {
	    'authority': 'accounts.google.com',
	    'accept': '*/*',
	    'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
	    'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
	    'user-agent': str(ua()),
	    'x-chrome-connected': 'source=Chrome,eligible_for_consistency=true',
	    'x-client-data': 'CMbxygE=',
	    'x-goog-ext-278367001-jspb': '["GlifWebSignIn"]',
	    'x-goog-ext-391502476-jspb': f'["{xr}"]',
	    'x-same-domain': '1',
	}
	
	params = {
	    'rpcids': 'E815hb',
	    'source-path': '/lifecycle/steps/signup/name',
	    'f.sid': '8878106518468624430',
	    'bl': 'boq_identity-account-creation-evolution-ui_20250319.07_p0',
	    'hl': 'ar',
	    'TL': TL,
	    '_reqid': '129653',
	    'rt': 'c',
	}
	
	data = f'f.req=%5B%5B%5B%22E815hb%22%2C%22%5B%5C%22{name}%D8%AC%D9%86%D8%B1%D8%A7%D9%84%5C%22%2C%5C%22%5C%22%2Cnull%2Cnull%2Cnull%2C%5B%5D%2Cnull%2C1%5D%22%2Cnull%2C%22generic%22%5D%5D%5D&at={at}&'
	
	rex = se.post(
	    'https://accounts.google.com/lifecycle/_/AccountLifecyclePlatformSignupUi/data/batchexecute',
	    params=params,
	    headers=headers,
	    data=data,
	)
	
	
	
	headers = {
	    'authority': 'accounts.google.com',
	    'accept': '*/*',
	    'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
	    'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
	    'user-agent': str(ua()),
	    'x-chrome-connected': 'source=Chrome,eligible_for_consistency=true',
	    'x-client-data': 'CMbxygE=',
	    'x-goog-ext-278367001-jspb': '["GlifWebSignIn"]',
	    'x-goog-ext-391502476-jspb': f'["{xr}"]',
	    'x-same-domain': '1',
	}
	
	params = {
	    'rpcids': 'eOY7Bb',
	    'source-path': '/lifecycle/steps/signup/birthdaygender',
	    'f.sid': '8878106518468624430',
	    'bl': 'boq_identity-account-creation-evolution-ui_20250319.07_p0',
	    'hl': 'ar',
	    'TL': TL,
	    '_reqid': '429653',
	    'rt': 'c',
	}
	data = f'f.req=%5B%5B%5B%22eOY7Bb%22%2C%22%5B%5B{year}%2C{month}%2C{day}%5D%2C1%2Cnull%2Cnull%2Cnull%2C%5C%22%3Ce7dqt-8CAAYS9oQNMvaNI-E0kDL2R8b0ADQBEArZ1Ii0ewZerS_7PBbUbK96k4d-7EUxCP2CNXM6XGobK0PC7E4HshzM1i7q2FVJ94jazQAAAwedAAAAKqcBB7EATTRIdjiLSgfcYKbEmqvAUgvTdx47_HplH3SQ0tr7csO3cf_aXFTEVFv9kA1RjEYYe9qfVreYjX4nVaFxRkvoFij3x6CiWd_z9-QD6m1bVgaqUu8nJlmtfsAihcv-HolbkeE8dfLkxoQtSyA_uhBUsZFX6A56Ul-A2T4c__nyopEGMXYZbvo2yorCm1rfQhJqwnHJCLT5xAACQg0fFT_yvhQj_3WSPfDc7QANHJgxzcH6kdHY0n-U_U1gbi0eJ0B0hrq_BTWwcPrGQAhBIgJBkMsXgu3eo3Mdx0zXF_0rNfkpF_8HSycSWLNTR38PS__rB1LvS5P2YRtCRavP9byAZ-CN_roEhEc9Qx3OI_VWdUlCASoMYp3lX1TapTw-KcHNA481z5tGLY__Z5CdTUyHtqeEJcOI1pU0axO0q2ATMZXO0P9YdP9NlO5Qhdubh90ZaT1O3zmDPoGiHYZ8ol0qRsxKwDwsqh8OpxaIShfjura9MnJj0Rn3ZcW2Pbvmg2vjpGobqe7X5hwrjytE5WsYtZgoUSQFUgIgqCdKs70n_mDvItjF2fEGu0g9q7a6ozXJR2-ZTUxpbMIktze_ttp_rICWGXBo1N3VIz0fgRHKEfd1E--QQ4MV9n6Fl_EkhphO5fUJFGYitCK1OEBjZL3sG6TxUxwLzq5bZwT0_x3_w2iZZFWad4oaI9UiIgHs09PSj7O0oV1IZcaL2MxPlrSP4_oXpgb8WS_TeovMGaYNtERgJEkjywqOIQU86X-O5rySXn3_ZyFBBaBDRhhWtJ93_4TIUe7Xb6zrNOpH9lhFWPV8j9sD_f_78HwE1MMCVPZ4_Yb-YxPODcvpAyl7_LgxY0IbIuqntFiGdLH277Hgj2LdEf-GwSNXDONR8bgD_f8Hd2ynPWu6aiiXGqDAF6zqUSk_8gGYcPaVKvj-xR-Ay8eBeZg32brhuFiDbDbd-7aWuJ_qvP9F5CvIPbaMh1IMUuCq18Ek7zjxh4nRLs8oN_Bf4biSl5_-9A9svKzrS_BMqfC2GYmBkWyCaf50TJ8ImgAFdA3xSerzi5UTahcK6F3B7E2wuH8sUi-yEDi_VHX9zAatz8A8WFSuK_D1Fp6kHEMOXtDjI4iDZHIn-ytQGNeoJoKhTfoPlQ4vhDtzH1BP3RuqzuHyGxCvbwvclsl4rV4gEqcR7hxuzt6WRmn6KGP4UXncpZKi0SliLpPCQMLLtdUvZqUhaN9FYMkdp2AkVJC4qhmbYsQYQBGAzklyvjUCh4DoQs9mhl9HlSMjcpCV-OJkCKMcButOvDrD0nQuANzusT419Ox1oVgEsUMdErZfywBm7YDqGth1T97anpiAeFG_QeDabJzidbHSD6WRgqwFs4dJ9mv7M5HPg2xX5j10244kIbc5UQgL68TVClLj83QNdpSZZMu5kNREbjOs3NELDv4f2wVzI5cFQyld0PkGfsI4CgobzFXgkqcyKbvmi4TkmCH6jkzJK8bx986hQGjVdX31Gg9bexhNXD2wlohQQfQUwpxIKu2TLFT_TZyPMGAIlFw89NHAH-NXSa1oXuOY_zgH7T2ESNQ4P3DjkUGPOBxl6AyqEh2DkKbwvOhRP3Yo7ceAVMpwxKYjwmaHD6OmZhnNF603lgvuKPfjdIwgYL66EnYel7S5tY3MOHlTFeM29gMzh8nC86bTKZwxRf2KlT5b-8mGAbrEcggQXdZp7PBi5M5xw9KxboB_Jf_mpgoRBl-_tgsWiQil4VVWICp-QVB94lLM1UWwGBR34kb5IbDDbl7LE-9s1qGcNVGL6q6YLRiJjL1M-roVJSn-JZQEuzoG7pBceotln2l87YTtN2jTB0w_xBtzH_O8H18cwF0QMNWwO_F-AsM21hmKPNCFoctsTWdmiPR4D2py1MjaNZoQe499SxOUGsFyiUI-ij2B2HNB_5LWUUxA4i9M9hQXE2bN8jqYc-AWq9hauHIXfkin5JpUoEPuLa4xyL2dwUZYK1xrg8gWOGhW0o9dLvWewAhM12XFUyXVHvIjUdJgqX26T3wmIJW6AiEAhvWHyuhoDQQuUG30mJeeG4YLm2_LORmSa6QGmmPjXAkFt-mMcvVAep3AjteJTozNvKAXIp5kd35fyJtLgkMRP-J1IqhyneiuajBTvldAXxBZsh5SzmMamwzjnrOzZ-yD94odwwiBduS16F2yiz3N5-pOqklt3AiRTD13-CRniPl6MASfSujoX3XADBAJujd6eURxhbx-ef_RhxdbpucwtDc2tmaL9LFjHh-RUDROvHOS1dKKCH31TtrnwjOjYG-shDoYsF0zRl7cUVzMNdVOxQ_jB7ttmFeEWX2mgkDJ6M78DdwcyRvtYH2tb8uNOXXa5WQwvgmk7L7-Aa1Zn10%5C%22%2C%5Bnull%2Cnull%2C%5C%22http%3A%2F%2Fsupport.google.com%2Fmail%2Fanswer%2F56256%3Fhl%3Dar%5C%22%2Cnull%2Cnull%2Cnull%2C%5B%5C%22GAlAdQ%5C%22%5D%5D%5D%22%2Cnull%2C%22generic%22%5D%5D%5D&at={at}&'
	
	response = se.post(
	    'https://accounts.google.com/lifecycle/_/AccountLifecyclePlatformSignupUi/data/batchexecute',
	    params=params,
	    headers=headers,
	    data=data,
	)
	
	
	
	
	headers = {
	    'authority': 'accounts.google.com',
	    'accept': '*/*',
	    'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
	    'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
	    'user-agent': str(ua()),
	    'x-chrome-connected': 'source=Chrome,eligible_for_consistency=true',
	    'x-client-data': 'CMbxygE=',
	    'x-goog-ext-278367001-jspb': '["GlifWebSignIn"]',
	    'x-goog-ext-391502476-jspb': f'["{xr}"]',
	    'x-same-domain': '1',
	}
	
	params = {
	    'rpcids': 'NHJMOd',
	    'source-path': '/lifecycle/steps/signup/username',
	    'f.sid': '8878106518468624430',
	    'bl': 'boq_identity-account-creation-evolution-ui_20250319.07_p0',
	    'hl': 'ar',
	    'TL': TL,
	    '_reqid': '1029653',
	    'rt': 'c',
	}
		
	data = f'f.req=%5B%5B%5B%22NHJMOd%22%2C%22%5B%5C%22{username}%5C%22%2C1%2C0%2Cnull%2C%5Bnull%2Cnull%2Cnull%2Cnull%2C0%2C196219%5D%2C0%2C40%5D%22%2Cnull%2C%22generic%22%5D%5D%5D&at={at}&'
	
	re = se.post(
	    'https://accounts.google.com/lifecycle/_/AccountLifecyclePlatformSignupUi/data/batchexecute',
	    params=params,
	    headers=headers,
	    data=data,
	).text
	if 'password' in re:
		return True
	else:
		return False
def search():
	data = {
	            'lsd': ''.join(random.choices(string.ascii_letters + string.digits, k=32)),
	            'variables': json.dumps({
	                'id': int(random.randrange(1629010000, 2500000000)),
	                'render_surface': 'PROFILE'
	            }),
	            'doc_id': '25618261841150840'
	        }
	headers = {'X-FB-LSD': data['lsd']}
	try:
		response = requests.post('https://www.instagram.com/api/graphql', headers=headers, data=data)
		user = response.json().get('data', {}).get('user', {})
		username = user.get('username')
		if '_' not in username:
			if len(username) >=6:
				return username
			else:
				pass
		else:
			pass
	except:
		search()