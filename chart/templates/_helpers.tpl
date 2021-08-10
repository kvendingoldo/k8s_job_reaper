{{/* vim: set filetype=mustache: */}}

{{/*
Create a default qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "name" -}}
{{- if .Values.name.override -}}
{{-   .Values.name.override | trunc 63 | trimSuffix "-" -}}
{{- else if .Values.name.useReleaseName -}}
{{-   .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{-   if contains .Chart.Name .Release.Name -}}
{{-     .Release.Name | trunc 63 | trimSuffix "-" -}}
{{-   else -}}
{{-     printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" -}}
{{-   end -}}
{{- end -}}
{{- end -}}

{{/* Labels */}}
{{- define "labels" -}}
app: {{ template "name" . }}
chart: "{{ .Chart.Name }}-{{ .Chart.Version | replace "+" "_" }}"
release: {{ .Release.Name }}
managed-by: helm
{{- end -}}

{{/* Manage match labels for selector */}}
{{- define "matchLabels" -}}
app: {{ template "name" . }}
release: {{ .Release.Name }}
{{- end -}}

{{/* image name */}}
{{- define "image" -}}
{{- if eq .Values.images.reaper.tag "" -}}
{{- .Values.images.reaper.image -}}
{{- else -}}
{{- printf "%s/%s:%s" .Values.registry.url .Values.images.reaper.image .Values.images.reaper.tag -}}
{{- end -}}
{{- end -}}
