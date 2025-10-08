.PHONY: install-openapi-generator
install-openapi-generator:
	brew install openapi-generator

.PHONY: update-vardef-openapi-definition
update-vardef-openapi-definition:
	cp \
		../vardef/build/generated/ksp/main/resources/META-INF/swagger/variable-definitions/variable-definitions-internal.yml \
		tests/variable_definitions/resources/openapi/variable-definitions-internal.yml

.PHONY: generate-vardef-client
generate-vardef-client:
	export PYTHON_POST_PROCESS_FILE="bin/openapi_generate_post_process.sh" && \
	openapi-generator generate \
		--enable-post-process-file \
		-i tests/variable_definitions/resources/openapi/variable-definitions-internal.yml \
		-g python \
		-o src/dapla_metadata/variable_definitions/_generated \
		--additional-properties=packageName=vardef_client \
		--skip-validate-spec
