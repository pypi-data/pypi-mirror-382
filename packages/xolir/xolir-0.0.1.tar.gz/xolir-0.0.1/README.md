
# Xolir (Tel IR schema)

## Goal

Some languages, like [Tel](https://github.com/mverleg/tel), compile to multiple other languages. All the parsing and type checking is shared, but codegen is different.

To facilitate this, there needs to be a clear api that different code generator backends can consume. Since these backends may be different processes, it should be serializable.

That is Xolir - a cross-language intermediary representation (xo l ir). It is made for, but not restricted to, [Tel](https://github.com/mverleg/tel).

## Usage

The IR is specified in Protobuf3 format. You can compile this yourself with protoc 

```bash
rm -rf target/ &&\
bash run.sh build &&\
sudo chown $USER:$USER -R target/
```

## Tests

There is a test that generates some Xolir data with python and generates Java code.

See `tests/test.sh` to run this.

## Implementation

Note that the language you generate the code for doesn't have to be the same language that the code generator is implemented in.

This uses protobuf. While this is not as descriptive as e.g. json-schema, this has better support for generating fast code in a range of languages.
