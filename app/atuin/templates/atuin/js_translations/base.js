if (TRANSLATIONS === undefined) {
	var TRANSLATIONS = {};
}

TRANSLATIONS["Javascript text"] = {{ _('Javascript text translated')|tojson }};
TRANSLATIONS['FORMTOOLS-TRANSLATION'] = {
	'ft-required' : {{ _('Campo obbligatorio')|tojson }},
	'ft-min-length' : {{ _('Numero minimo di caratteri richiesto:')|tojson }},
	'ft-regex' : {{ _('Errore')|tojson }},
	'ft-email-validation' : {{ _('Indirizzo email non corretto')|tojson }},
	'ft-date-validation' : {{ _('Data errata. Il formato della data richiesto è:')|tojson }},
	'ft-date-range-after' : {{ _('Richiesta una data succesiva a:')|tojson }},
	'ft-date-range-before' : {{ _('Richiesta una data precedente a:')|tojson }},
};
