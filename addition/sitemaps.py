from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class Our_Sitemap(Sitemap):

	changefreq = "daily"
	priority = 1.0
	protocol = 'https'

	def items(self):
		return ['home']

	def location(self, item):
		return reverse(item)


		
