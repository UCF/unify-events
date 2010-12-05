def sluggify(original):
	"""docstring for sluggify"""
	import re
	slug  = original.lower().replace(' ', '-')
	slug  = re.sub("[^A-Za-z1-9\s\-]", '', slug)
	return slug