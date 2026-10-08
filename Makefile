SHELL := /usr/bin/env bash
.SHELLFLAGS := -euo pipefail -c
.DEFAULT_GOAL := help

SCHEMA_URL ?= https://raw.githubusercontent.com/datreeio/CRDs-catalog/main/{{.Group}}/{{.ResourceKind}}_{{.ResourceAPIVersion}}.json

.PHONY: help
help: ## Muestra este menú de ayuda
	@awk 'BEGIN{FS=":.*## "} /^[a-zA-Z_-]+:.*## /{printf "  \033[36m%-15s\033[0m %s\n",$$1,$$2}' $(MAKEFILE_LIST)

.PHONY: lint
lint: ## Ejecuta validación estática de Helm values
	@echo "==> Validating Helm template syntax..."
	@helm template kube-prometheus-stack prometheus-community/kube-prometheus-stack -f helm/kube-prometheus-stack/values.yaml > /dev/null
	@echo "✅ Helm template syntax is valid"

.PHONY: template
template: ## Renderiza los manifiestos de kube-prometheus-stack a stdout
	@helm template kube-prometheus-stack prometheus-community/kube-prometheus-stack -f helm/kube-prometheus-stack/values.yaml

.PHONY: validate
validate: ## Valida los manifiestos generados contra esquemas de Kubernetes usando Kubeconform
	@echo "==> Rendering and validating kube-prometheus-stack with Kubeconform..."
	@helm template kube-prometheus-stack prometheus-community/kube-prometheus-stack -f helm/kube-prometheus-stack/values.yaml \
		| kubeconform -summary -schema-location default -schema-location '$(SCHEMA_URL)' -ignore-missing-schemas
	@echo "✅ Manifests conform to Kubernetes schemas"
