SHELL := /usr/bin/env bash
.SHELLFLAGS := -euo pipefail -c
.DEFAULT_GOAL := help

SCHEMA_URL ?= https://raw.githubusercontent.com/datreeio/CRDs-catalog/main/{{.Group}}/{{.ResourceKind}}_{{.ResourceAPIVersion}}.json

.PHONY: help
help: ## Muestra este menú de ayuda
	@awk 'BEGIN{FS=":.*## "} /^[a-zA-Z_-]+:.*## /{printf "  \033[36m%-15s\033[0m %s\n",$$1,$$2}' $(MAKEFILE_LIST)

.PHONY: lint
lint: lint-prometheus lint-loki lint-alloy lint-tempo lint-otel ## Valida la sintaxis de plantillas de todos los componentes Helm

.PHONY: lint-prometheus
lint-prometheus:
	@echo "==> Validating kube-prometheus-stack Helm template..."
	@helm template kube-prometheus-stack prometheus-community/kube-prometheus-stack -f helm/kube-prometheus-stack/values.yaml > /dev/null
	@echo "✅ kube-prometheus-stack template is valid"

.PHONY: lint-loki
lint-loki:
	@echo "==> Validating Loki Helm template..."
	@helm template loki grafana/loki -f helm/loki/values.yaml > /dev/null
	@echo "✅ Loki template is valid"

.PHONY: lint-alloy
lint-alloy:
	@echo "==> Validating Alloy Helm template..."
	@helm template alloy grafana/alloy -f helm/alloy/values.yaml > /dev/null
	@echo "✅ Alloy template is valid"

.PHONY: lint-tempo
lint-tempo:
	@echo "==> Validating Tempo Helm template..."
	@helm template tempo grafana/tempo -f helm/tempo/values.yaml > /dev/null
	@echo "✅ Tempo template is valid"

.PHONY: lint-otel
lint-otel:
	@echo "==> Validating OpenTelemetry Collector Helm template..."
	@helm template opentelemetry-collector open-telemetry/opentelemetry-collector -f helm/opentelemetry-collector/values.yaml > /dev/null
	@echo "✅ OpenTelemetry Collector template is valid"

.PHONY: validate
validate: validate-prometheus validate-loki validate-alloy validate-tempo validate-otel ## Valida manifiestos generados contra esquemas OpenAPI con Kubeconform

.PHONY: validate-prometheus
validate-prometheus:
	@echo "==> Validating kube-prometheus-stack with Kubeconform..."
	@helm template kube-prometheus-stack prometheus-community/kube-prometheus-stack -f helm/kube-prometheus-stack/values.yaml \
		| kubeconform -summary -schema-location default -schema-location '$(SCHEMA_URL)' -ignore-missing-schemas
	@echo "✅ kube-prometheus-stack conforms to Kubernetes schemas"

.PHONY: validate-loki
validate-loki:
	@echo "==> Validating Loki with Kubeconform..."
	@helm template loki grafana/loki -f helm/loki/values.yaml \
		| kubeconform -summary -schema-location default -schema-location '$(SCHEMA_URL)' -ignore-missing-schemas
	@echo "✅ Loki conforms to Kubernetes schemas"

.PHONY: validate-alloy
validate-alloy:
	@echo "==> Validating Alloy with Kubeconform..."
	@helm template alloy grafana/alloy -f helm/alloy/values.yaml \
		| kubeconform -summary -schema-location default -schema-location '$(SCHEMA_URL)' -ignore-missing-schemas
	@echo "✅ Alloy conforms to Kubernetes schemas"

.PHONY: validate-tempo
validate-tempo:
	@echo "==> Validating Tempo with Kubeconform..."
	@helm template tempo grafana/tempo -f helm/tempo/values.yaml \
		| kubeconform -summary -schema-location default -schema-location '$(SCHEMA_URL)' -ignore-missing-schemas
	@echo "✅ Tempo conforms to Kubernetes schemas"

.PHONY: validate-otel
validate-otel:
	@echo "==> Validating OpenTelemetry Collector with Kubeconform..."
	@helm template opentelemetry-collector open-telemetry/opentelemetry-collector -f helm/opentelemetry-collector/values.yaml \
		| kubeconform -summary -schema-location default -schema-location '$(SCHEMA_URL)' -ignore-missing-schemas
	@echo "✅ OpenTelemetry Collector conforms to Kubernetes schemas"
