function parseQueryString(str) {
	var query = {},
		vars = str.split("&"),
		v,
		parts;

	for (v = 0; v < vars.length; v++) {
		parts = vars[v].split("=");
		query[parts[0]] = parts[1];
	}

	return query;
}

function parseHash() {
	return parseQueryString(window.location.hash.substr(1));
}

document.addEventListener("DOMContentLoaded", function () {
	var output = document.getElementById("oauth-token"),
		hash = parseHash();

	output.innerHTML = hash.access_token;
});
