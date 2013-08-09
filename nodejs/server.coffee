io = require('socket.io').listen 8080

cookie_reader = require 'cookie'
querystring = require 'querystring'
http = require 'http'

redis = require 'redis'
client = redis.createClient()  # pub/sub
client2 = redis.createClient()  # for queries


io.configure ->
	io.set 'authorization', (data, accept) ->
		console.log "HANDSHAKE::xdomain", data['xdomain']
		if data.headers.cookie
			data.cookie = cookie_reader.parse data.headers.cookie  # parse cookies
			return accept null, true

		return accept 'Cookies not defined!', false

	io.set 'log level', 1


io.sockets.on 'connection', (socket)->
	time = (new Date).toLocaleTimeString()

	# proxy to django
	socket.on 'send', (options, fn)->
		method = if options['method'] then options['method'] else 'get'
		url = options['url']
		data = options['data']
		csrftoken = if options['csrftoken'] then options['csrftoken'] else socket.handshake.cookie['csrftoken']
		sessionid = socket.handshake.cookie['sessionid']

		values = querystring.stringify data
		cookie = "sessionid=#{sessionid}; csrftoken=#{csrftoken}"

		options =
			host: "127.0.0.1"
			port: 8000
			path: url
			method: method
			headers:
				'Cookie': cookie
				'X-CSRFToken': csrftoken
				'X-Requested-With': 'XMLHttpRequest'
				'Content-Length': values.length

		if method is 'GET' or method is 'get'
			options['headers']['Content-Type'] = 'application/json'
		else
			options['headers']['Content-Type'] = 'application/x-www-form-urlencoded'

		req = http.request options, (res)->
			res.setEncoding 'utf8'
			res.message = ""
			console.log JSON.stringify res.headers
			res.on 'data', (chunk)->
				res.message += chunk.toString()

			res.on 'end', ->
				try
					data = JSON.parse(res.message);
					fn data, no
				catch err
					console.log "DJANGO! ITS FUCKING NOT JSON!!!: ", res.message
					fn no, yes

		req.on 'error', (e)->
			console.log "DJANGO::CONNECTOR", e.message
			fn no, yes

		req.write values
		req.end()


client.on "message", (channel, message)->
	console.log "REDIS", "Chanel: #{channel}, message: #{message}"
	io.sockets.emit 'django_message', message

client.subscribe "nodejs"