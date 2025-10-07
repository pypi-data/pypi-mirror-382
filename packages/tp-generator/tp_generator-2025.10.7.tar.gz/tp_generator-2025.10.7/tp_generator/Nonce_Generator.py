def WordPress_Nonce(nonce_action, WORDPRESS_NONCE_KEY, WORDPRESS_NONCE_SALT, user_id=0, wordpress_logged_in_COOKIE="", DAY_IN_SECONDS=24*60*60):
	import time, math, hmac, re, platform

	token = ""
	if user_id > 0:
		token = re.split("\\||%7C|%7c", wordpress_logged_in_COOKIE)[2]

	nonce_tick = int(math.ceil(time.time() / (DAY_IN_SECONDS / 2)))

	data = "{nonce_tick}|{nonce_action}|{user_id}|{token}".format(nonce_tick=nonce_tick, nonce_action=nonce_action, user_id=user_id, token=token)

	if platform.python_version_tuple()[0] == "3":
		return hmac.new((WORDPRESS_NONCE_KEY+WORDPRESS_NONCE_SALT).encode("utf-8"), data.encode("utf-8"), "MD5").hexdigest()[-12:-2]
	else:
		return hmac.new((WORDPRESS_NONCE_KEY+WORDPRESS_NONCE_SALT).encode("utf-8"), data.encode("utf-8")).hexdigest()[-12:-2]