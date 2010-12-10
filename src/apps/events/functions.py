def sluggify(original):
	"""docstring for sluggify"""
	import re
	slug  = original.lower().strip()
	slug  = re.sub("[\s]+", '-', slug)
	slug  = re.sub("[^a-z1-9\s\-]", '', slug)
	return slug