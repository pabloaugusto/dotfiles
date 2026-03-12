FROM mcr.microsoft.com/powershell AS base
SHELL ["pwsh", "-Command"]
RUN Install-Module -Name PSScriptAnalyzer -Scope AllUsers -Force
RUN Import-Module PSScriptAnalyzer

FROM base AS lint-powershell
WORKDIR /src
COPY [".", "."]
RUN Invoke-ScriptAnalyzer .
WORKDIR /src/df
RUN Invoke-ScriptAnalyzer .
WORKDIR /src/app/df/powershell
RUN Invoke-ScriptAnalyzer .

FROM mcr.microsoft.com/powershell AS base-pwsh
WORKDIR /src
COPY [".", "."]
WORKDIR /src/app/df/bash
RUN bash -n .bashrc
#RUN bash -n ./bootstrap.sh
