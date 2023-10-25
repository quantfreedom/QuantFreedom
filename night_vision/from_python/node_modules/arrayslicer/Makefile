test:
	@node_modules/.bin/mocha --ui tdd test/test.js

coverage:
	@test -d reports || mkdir reports
	@node_modules/.bin/istanbul cover --dir ./reports node_modules/.bin/_mocha -- --ui tdd test/test.js

.PHONY: test coverage
