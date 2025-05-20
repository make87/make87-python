#!/usr/bin/env bash

datamodel-codegen \
  --input make87/internal/schemas/application_env_config.schema.json \
  --input-file-type jsonschema \
  --use-title-as-name \
  --output make87/models/application_env_config.py \
  --output-model-type pydantic_v2.BaseModel \
  --formatters ruff-format
