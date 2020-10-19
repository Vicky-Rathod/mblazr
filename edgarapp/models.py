# edgarapp/models.py
# for database
# @radiasl

from django.db import models


class Company(models.Model):
	cik = models.CharField(max_length=255)
	ticker = models.CharField(max_length=255)
	name = models.CharField(max_length=255)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=['cik', 'name'], name='cik_name constraint')
		]

	def __str__(self):
		return self.name

class Filing(models.Model):
	cik = models.CharField(max_length=255)
	name = models.CharField(max_length=255)
	filingtype = models.CharField(max_length=255)
	filingdate = models.CharField(max_length=255)
	filingpath = models.CharField(max_length=255) # local file path

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=['filingpath','filingdate'], name='path_date constraint')
		]

	def __str__(self):
		return self.name

class Funds(models.Model):
	fund = models.CharField(max_length=255)
	company = models.CharField(max_length=255)
	classTitle = models.CharField(max_length=255)
	CUSIP = models.CharField(max_length=255)
	value = models.CharField(max_length=255)
	share_prn_amount = models.CharField(max_length=255)
	share_prn_type = models.CharField(max_length=255)
	put_call = models.CharField(max_length=255)
	investment_discretion = models.CharField(max_length=255)
	other_manager = models.CharField(max_length=255)
	sole_voting_authority = models.CharField(max_length=255)
	shared_voting_authority = models.CharField(max_length=255)
	none_voting_authority = models.CharField(max_length=255)

class Directors(models.Model):
	company = models.CharField(max_length=255)
	director = models.CharField(max_length=255)
	age = models.CharField(max_length=255)
	bio = models.CharField(max_length=255)

class Proxies(models.Model):
	cik = models.CharField(max_length=255)
	name = models.CharField(max_length=255)
	filingtype = models.CharField(max_length=255)
	filingdate = models.CharField(max_length=255)
	filingpath = models.CharField(max_length=255) # local file path

class Executives(models.Model):
	company = models.CharField(max_length=255)
	executives = models.CharField(max_length=255)
	filingdate = models.CharField(max_length=255)
	


class FilingTOC(models.Model):
	body = models.TextField()
	filing = models.ForeignKey(Filing, on_delete=models.SET_NULL,null=True, related_name='table_of_contents')
