param(
	[string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
)

$ErrorActionPreference = 'Stop'

function Add-Failure {
	param(
		[System.Collections.Generic.List[string]]$Failures,
		[string]$Message
	)

	$Failures.Add($Message) | Out-Null
}

function Get-FrontmatterValue {
	param(
		[string]$Frontmatter,
		[string]$Key
	)

	$pattern = '(?m)^' + [regex]::Escape($Key) + ':\s*(.+?)\s*$'
	$match = [regex]::Match($Frontmatter, $pattern)
	if (-not $match.Success) {
		return $null
	}

	return $match.Groups[1].Value.Trim().Trim("'`"")
}

$repoRoot = (Resolve-Path $RepoRoot).Path
$failures = [System.Collections.Generic.List[string]]::new()

foreach ($relativePath in @('AGENTS.md', 'docs/ai-operating-model.md', 'docs/AI-WIP-TRACKER.md', 'docs/ROADMAP-DECISIONS.md')) {
	$fullPath = Join-Path $repoRoot $relativePath
	if (-not (Test-Path $fullPath -PathType Leaf)) {
		Add-Failure -Failures $failures -Message "Arquivo obrigatorio ausente: $relativePath"
	}
}

$trackerPath = Join-Path $repoRoot 'docs/AI-WIP-TRACKER.md'
if (Test-Path $trackerPath -PathType Leaf) {
	$trackerContent = Get-Content $trackerPath -Raw
	foreach ($marker in @(
			'<!-- ai-worklog:doing:start -->',
			'<!-- ai-worklog:doing:end -->',
			'<!-- ai-worklog:done:start -->',
			'<!-- ai-worklog:done:end -->',
			'<!-- ai-worklog:log:start -->',
			'<!-- ai-worklog:log:end -->'
		)) {
		if ($trackerContent -notmatch [regex]::Escape($marker)) {
			Add-Failure -Failures $failures -Message "Marcador obrigatorio ausente em docs/AI-WIP-TRACKER.md: $marker"
		}
	}
}

$decisionsPath = Join-Path $repoRoot 'docs/ROADMAP-DECISIONS.md'
if (Test-Path $decisionsPath -PathType Leaf) {
	$decisionsContent = Get-Content $decisionsPath -Raw
	foreach ($marker in @(
			'<!-- roadmap:suggestions:start -->',
			'<!-- roadmap:suggestions:end -->',
			'<!-- roadmap:cycles:start -->',
			'<!-- roadmap:cycles:end -->'
		)) {
		if ($decisionsContent -notmatch [regex]::Escape($marker)) {
			Add-Failure -Failures $failures -Message "Marcador obrigatorio ausente em docs/ROADMAP-DECISIONS.md: $marker"
		}
	}
}

$skillsRoot = Join-Path $repoRoot '.codex/skills'
if (-not (Test-Path $skillsRoot -PathType Container)) {
	Add-Failure -Failures $failures -Message 'Pasta obrigatoria ausente: .codex/skills'
}
else {
	$skillDirs = Get-ChildItem $skillsRoot -Directory | Sort-Object Name
	if ($skillDirs.Count -eq 0) {
		Add-Failure -Failures $failures -Message 'Nenhuma skill encontrada em .codex/skills'
	}

	foreach ($skillDir in $skillDirs) {
		$skillMdPath = Join-Path $skillDir.FullName 'SKILL.md'
		$agentYamlPath = Join-Path $skillDir.FullName 'agents/openai.yaml'
		$referencesDir = Join-Path $skillDir.FullName 'references'

		if (-not (Test-Path $skillMdPath -PathType Leaf)) {
			Add-Failure -Failures $failures -Message "SKILL.md ausente em $($skillDir.Name)"
			continue
		}

		if (-not (Test-Path $agentYamlPath -PathType Leaf)) {
			Add-Failure -Failures $failures -Message "agents/openai.yaml ausente em $($skillDir.Name)"
		}

		if (-not (Test-Path $referencesDir -PathType Container)) {
			Add-Failure -Failures $failures -Message "references/ ausente em $($skillDir.Name)"
		}

		$skillContent = Get-Content $skillMdPath -Raw
		if ($skillContent -match 'TODO') {
			Add-Failure -Failures $failures -Message "Placeholder TODO encontrado em $($skillDir.Name)/SKILL.md"
		}

		$frontmatterMatch = [regex]::Match($skillContent, '(?s)\A---\r?\n(?<front>.*?)\r?\n---')
		if (-not $frontmatterMatch.Success) {
			Add-Failure -Failures $failures -Message "Frontmatter invalido em $($skillDir.Name)/SKILL.md"
			continue
		}

		$frontmatter = $frontmatterMatch.Groups['front'].Value
		$skillName = Get-FrontmatterValue -Frontmatter $frontmatter -Key 'name'
		$description = Get-FrontmatterValue -Frontmatter $frontmatter -Key 'description'

		if (-not $skillName) {
			Add-Failure -Failures $failures -Message "name ausente em $($skillDir.Name)/SKILL.md"
		}
		elseif ($skillName -ne $skillDir.Name) {
			Add-Failure -Failures $failures -Message "name '$skillName' difere da pasta '$($skillDir.Name)'"
		}
		elseif ($skillName -notmatch '^[a-z0-9-]+$') {
			Add-Failure -Failures $failures -Message "name invalido em $($skillDir.Name)/SKILL.md"
		}

		if (-not $description) {
			Add-Failure -Failures $failures -Message "description ausente em $($skillDir.Name)/SKILL.md"
		}

		if (Test-Path $agentYamlPath -PathType Leaf) {
			$agentYaml = Get-Content $agentYamlPath -Raw
			if ($agentYaml -notmatch '(?m)^interface:\s*$') {
				Add-Failure -Failures $failures -Message "interface ausente em $($skillDir.Name)/agents/openai.yaml"
			}

			$defaultPromptPattern = '(?m)^\s*default_prompt:\s*".*\$' + [regex]::Escape($skillDir.Name) + '.*"\s*$'
			if ($agentYaml -notmatch $defaultPromptPattern) {
				$expectedSkillRef = '$' + $skillDir.Name
				Add-Failure -Failures $failures -Message "default_prompt precisa mencionar $expectedSkillRef em $($skillDir.Name)/agents/openai.yaml"
			}

			$shortDescriptionMatch = [regex]::Match($agentYaml, '(?m)^\s*short_description:\s*"(?<value>.+)"\s*$')
			if (-not $shortDescriptionMatch.Success) {
				Add-Failure -Failures $failures -Message "short_description ausente em $($skillDir.Name)/agents/openai.yaml"
			}
			else {
				$shortLength = $shortDescriptionMatch.Groups['value'].Value.Length
				if ($shortLength -lt 25 -or $shortLength -gt 64) {
					Add-Failure -Failures $failures -Message "short_description fora do intervalo 25-64 em $($skillDir.Name)/agents/openai.yaml"
				}
			}
		}
	}
}

$agentsRoot = Join-Path $repoRoot '.agents'
if (-not (Test-Path $agentsRoot -PathType Container)) {
	Add-Failure -Failures $failures -Message 'Pasta obrigatoria ausente: .agents'
}
else {
	$requiredHeadings = @(
		'## Objetivo',
		'## Quando usar',
		'## Entradas',
		'## Saidas',
		'## Fluxo',
		'## Guardrails',
		'## Criterios de conclusao'
	)

	$agentCards = Get-ChildItem $agentsRoot -Filter '*.md' -File | Sort-Object Name
	if ($agentCards.Count -eq 0) {
		Add-Failure -Failures $failures -Message 'Nenhum cartao de agente encontrado em .agents'
	}

	foreach ($agentCard in $agentCards) {
		$content = Get-Content $agentCard.FullName -Raw
		foreach ($heading in $requiredHeadings) {
			if ($content -notmatch [regex]::Escape($heading)) {
				Add-Failure -Failures $failures -Message "Heading obrigatorio ausente em .agents/$($agentCard.Name): $heading"
			}
		}
	}
}

if ($failures.Count -gt 0) {
	Write-Host 'Falhas encontradas na camada de IA:' -ForegroundColor Red
	foreach ($failure in $failures) {
		Write-Host " - $failure" -ForegroundColor Red
	}
	exit 1
}

Write-Host 'AI assets OK.' -ForegroundColor Green
