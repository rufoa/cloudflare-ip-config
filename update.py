import requests, re, pystache, json, sys, os, subprocess

def fatal(message):
	print message
	exit(1)

def fetch(url):
	try:
		response = requests.get(url, verify=True)
	except requests.exceptions.SSLError:
		fatal('Bad SSL cert while fetching ' + url)
	if response.status_code != 200:
		fatal('Bad status code ' + response.status_code + ' while fetching ' + url)
	return response.text

files = sys.argv[1:]
if len(files) >= 1:
	config = []
	for f in files:
		base = os.path.dirname(os.path.realpath(f))
		with open(f) as handle:
			j = handle.read()
		entries = json.loads(j)
		if isinstance(entries, dict):
			entries = [entries]
		for entry in entries:
			if 'template' in entry and 'destination' in entry:
				if not os.path.isabs(entry['template']):
					entry['template'] = os.path.join(base, entry['template'])
				if not os.path.isabs(entry['destination']):
					entry['destination'] = os.path.join(base, entry['destination'])
				if not os.path.exists(entry['template']):
					fatal(entry['template'] + ' does not exist')
				config.append(entry)
			else:
				fatal('Config file ' + f + ' missing a template or destination file')
else:
	fatal('No config file(s) specified')

v4 = fetch('https://www.cloudflare.com/ips-v4')
v6 = fetch('https://www.cloudflare.com/ips-v6')

ranges4 = []
for (ip, prefix) in re.findall('(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})/(\d{1,2})', v4):
	cidr = ip + '/' + prefix
	maskhex = format((2 ** int(prefix) - 1) << (32 - int(prefix)), '08x')
	mask = u'.'.join([str(int(maskhex[n:n+2], 16)) for n in [0,2,4,6]])
	ranges4.append({
		'ip': ip,
		'prefix': prefix,
		'cidr': cidr,
		'mask': mask
	})

ranges6 = []
for (ip, prefix) in re.findall('((?:[0-9a-fA-F]{1,4}:{0,2}){1,6})/(\d{1,2})', v6):
	cidr = ip + '/' + prefix
	ranges6.append({
		'ip': ip,
		'prefix': prefix,
		'cidr': cidr,
	})

for entry in config:
	with open(entry['template']) as handle:
		template = handle.read()
	rendered = pystache.render(template, {'ranges4': ranges4, 'ranges6': ranges6})
	if 'before' in entry:
		subprocess.check_call(entry['before'])
	with open(entry['destination'], 'w') as handle:
		handle.write(rendered)
	if 'after' in entry:
		subprocess.check_call(entry['after'])