version: 1

platforms:
  atlassian:
    enabled: true
    provider: atlassian-cloud
    auth:
      mode: service-account-api-token
      site_url: "op://<vault>/<item>/<section>/site-url"
      email: "op://<vault>/<item>/<section>/email"
      token: "op://<vault>/<item>/<section>/api-token"
      service_account: "op://<vault>/<item>/<section>/service-account"
      cloud_id: "op://<vault>/<item>/<section>/cloud-id"
    jira:
      enabled: true
      project_key: "op://<vault>/<item>/<section>/project-key"
    confluence:
      enabled: true
      space_key: "op://<vault>/<item>/<section>/space-key"
