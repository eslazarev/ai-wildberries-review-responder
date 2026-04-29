{{- define "wb-responder.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "wb-responder.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- if contains $name .Release.Name -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}
{{- end -}}

{{- define "wb-responder.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "wb-responder.labels" -}}
helm.sh/chart: {{ include "wb-responder.chart" . }}
{{ include "wb-responder.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{- define "wb-responder.selectorLabels" -}}
app.kubernetes.io/name: {{ include "wb-responder.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{- define "wb-responder.serviceAccountName" -}}
{{- if .Values.serviceAccount.create -}}
{{- default (include "wb-responder.fullname" .) .Values.serviceAccount.name -}}
{{- else -}}
{{- default "default" .Values.serviceAccount.name -}}
{{- end -}}
{{- end -}}

{{- define "wb-responder.secretName" -}}
{{- if .Values.secrets.existingSecret -}}
{{- .Values.secrets.existingSecret -}}
{{- else -}}
{{- include "wb-responder.fullname" . -}}
{{- end -}}
{{- end -}}

{{- define "wb-responder.configMapName" -}}
{{- if .Values.settings.existingConfigMap -}}
{{- .Values.settings.existingConfigMap -}}
{{- else -}}
{{- include "wb-responder.fullname" . -}}
{{- end -}}
{{- end -}}
