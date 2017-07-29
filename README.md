# JSON Mapper

This package is intended to tkae an input JSON payload and map
it to some output payload. The package assumes that there is a schema
for both the input and output. Look to Avro as an example

The output_creator will take a set of implicit mappings and generate the
output payload by walking through the tree. This package will be useful in
any data pipelines that requires mappings between JSON schemas
