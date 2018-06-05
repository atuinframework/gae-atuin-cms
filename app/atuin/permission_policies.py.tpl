# -*- coding: utf-8 -*-
# Roles define classes of users. Each user has to be assigned at least (and at most) to one role.
# A role defines multiple policies. Policies can be used in more than one role.
# A policy is a group of functions.

user_role_polices = {
	'ADMIN': {
		'title': 'Administrator',
		'description': 'Administrator. All rights.',
		'policies': None
	},
	'MODERATOR': {
		'title': 'Moderator',
		'description': 'Makes decisions regarding content and the direction of threads.',
		'policies': ['policy_1', 'policy_3']
	},
	'PUBLISHER': {
		'title': 'Publisher',
		'description': 'Makes and publishes new articles.',
		'policies': ['policy_1', 'policy_2']
	}
}

role_policy_functions = {
	'policy_1': ['function_1', 'function_2', 'function_3'],
	'policy_2': ['function_1', 'function_2', 'function_3'],
	'policy_3': ['function_1', 'function_2', 'function_3']
}

user_roles = user_role_polices.keys()
