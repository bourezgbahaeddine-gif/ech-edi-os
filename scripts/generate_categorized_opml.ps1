param(
    [string]$LegacyPath = 'D:\Echorouk Editorial OS\ech_sources.opml',
    [string]$EditorialPath = 'D:\Echorouk Editorial OS\Editorial_feeds.xml',
    [string]$OutputPath = '',
    [string]$StrictOutputPath = '',
    [string]$ReviewOutputPath = ''
)

$ErrorActionPreference = 'Stop'
$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptRoot

if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $OutputPath = Join-Path $RepoRoot 'ech_sources_final_categorized.opml'
}
if ([string]::IsNullOrWhiteSpace($StrictOutputPath)) {
    $StrictOutputPath = Join-Path $RepoRoot 'freshrss_master_clean.opml'
}
if ([string]::IsNullOrWhiteSpace($ReviewOutputPath)) {
    $ReviewOutputPath = Join-Path $RepoRoot 'uncategorized_review.opml'
}

function Normalize-Url([string]$url) {
    if ([string]::IsNullOrWhiteSpace($url)) { return '' }
    try {
        $u = [uri]$url.Trim()
        $host = $u.Host.ToLower()
        if ($host.StartsWith('www.')) { $host = $host.Substring(4) }
        $path = $u.AbsolutePath.TrimEnd('/')
        return ('{0}://{1}{2}{3}' -f $u.Scheme.ToLower(), $host, $path, $u.Query)
    } catch {
        return $url.Trim().ToLower()
    }
}

function Get-Host([string]$url) {
    if ([string]::IsNullOrWhiteSpace($url)) { return '' }
    try {
        $u = [uri]$url.Trim()
        $host = $u.Host.ToLower()
        if ($host.StartsWith('www.')) { $host = $host.Substring(4) }
        return $host
    } catch {
        return ''
    }
}

function Get-Items([string]$path) {
    [xml]$xml = Get-Content -LiteralPath $path -Raw
    $nodes = Select-Xml -Xml $xml -XPath '//outline[@xmlUrl]'
    foreach ($n in $nodes) {
        $node = $n.Node
        $xmlUrl = ([string]$node.xmlUrl).Trim()
        [pscustomobject]@{
            Text = ([string]$node.text).Trim()
            Title = ([string]$node.title).Trim()
            Name = ($(if ([string]::IsNullOrWhiteSpace([string]$node.title)) { [string]$node.text } else { [string]$node.title })).Trim()
            XmlUrl = $xmlUrl
            HtmlUrl = ([string]$node.htmlUrl).Trim()
            Category = ([string]$node.category).Trim()
            NormUrl = Normalize-Url $xmlUrl
            Host = Get-Host $xmlUrl
        }
    }
}

function Get-Category([object]$item, [hashtable]$hostCategoryMap) {
    if (-not [string]::IsNullOrWhiteSpace($item.Category)) {
        return $item.Category
    }

    $name = ([string]$item.Name).ToLower()
    $url = ([string]$item.XmlUrl).ToLower()
    $feedHost = ([string]$item.Host).ToLower()

    if ($hostCategoryMap.ContainsKey($feedHost) -and $hostCategoryMap[$feedHost].Count -eq 1) {
        return $hostCategoryMap[$feedHost][0]
    }

    if ($feedHost -match 'cnet\.com|theverge\.com|wired\.com|nature\.com|science\.org') {
        return 'Tech'
    }

    if ($feedHost -match 'olympics\.com|uefa\.com|lfp\.dz|faf\.dz') {
        return 'Sports'
    }

    if ($feedHost -match 'imf\.org|worldbank\.org|who\.int') {
        return 'Economy'
    }

    if ($feedHost -match 'afp\.com|apnews\.com|reuters\.com|cnn\.com|bbc\.co\.uk|bbc\.com|france24\.com|rfi\.fr|lemonde\.fr|lefigaro\.fr|liberation\.fr|nytimes\.com|theguardian\.com|ft\.com|forbes\.com|euronews\.com') {
        return 'Global'
    }

    if ($name -match 'econom|economie|business|market|finance|bloomberg|ft|opec|wto|cnbc' -or
        $url -match 'econom|economie|business|finance|market') {
        return 'Economy'
    }

    if ($name -match 'sport|football|fifa|espn|marca|sky sports|equipe|caf|goal|dzfoot|competition' -or
        $url -match 'sport|football|fifa|espn|marca|goal|dzfoot|competition') {
        return 'Sports'
    }

    if ($name -match 'tech|ai|openai|ars technica|hacker news|venturebeat|meta|google ai|security' -or
        $url -match 'tech|openai|googleblog|venturebeat|thehackernews|security') {
        return 'Tech'
    }

    if ($name -match 'earthquake|weather|gdacs|noaa|relief|em-dat' -or
        $url -match 'gdacs|noaa|earthquake|reliefweb') {
        return 'Alerts'
    }

    if ($name -match 'telegram|youtube|reddit|google news|flipboard' -or
        $url -match 'reddit|youtube|news.google.com|flipboard') {
        return 'Trends'
    }

    if ($name -match 'interlignes|middle east eye|al-monitor|jeune afrique|maghreb|orient xxi|north africa post' -or
        $url -match 'middleeasteye|al-monitor|jeuneafrique|maghrebemergent|maghreb-intelligence|orientxxi|northafricapost') {
        return 'Competitors'
    }

    if ($name -match 'arts|culture|entertainment|pitchfork|variety|hollywood|netflix' -or
        $url -match 'culture|arts|pitchfork|variety|hollywoodreporter|netflix') {
        return 'Entertainment'
    }

    if ($feedHost -match 'aps\.dz|elkhabar\.com|ennaharonline\.com|tsa-algerie\.com|algerie360\.com|expressdz\.dz|lematindalgerie\.com|observalgerie\.com|elwatan\.com|el-mouradia\.dz|premier-ministre\.gov\.dz|mdn\.dz|mre\.gov\.dz|interieur\.gov\.dz|elbilad\.net|radioalgerie\.dz|tv4algerie\.com|algerie-dz\.com|meteo\.dz|protectioncivile\.dz|bank-of-algeria\.dz|sonatrach\.dz|marchespublics\.gov\.dz|startup\.dz|dzfoot\.com|competition\.dz') {
        return 'Algeria'
    }

    if ($feedHost -match 'aljazeera|alarabiya|skynewsarabia|arabic\.cnn|bbci\.co\.uk|spa\.gov\.sa|wam\.ae|qna\.org\.qa|aa\.com\.tr|aawsat|arabnews|gulfnews|thenationalnews|ahram|masrawy|royanews|jordantimes|lbcgroup|hespress|le360|tunisienumerique|kapitalis|mosaiquefm') {
        return 'Arab_World'
    }

    if ($feedHost -match 'cnn\.com|bbc\.com|bbci\.co\.uk|reuters\.com|apnews\.com|france24\.com|rfi\.fr|lemonde\.fr|lefigaro\.fr|liberation\.fr|nytimes\.com|washingtonpost\.com|dw\.com|npr\.org|politico\.com|marketwatch\.com|news\.sky\.com|jpost\.com') {
        return 'Global'
    }

    return 'Uncategorized'
}

$legacyItems = @(Get-Items $LegacyPath)
$editorialItems = @(Get-Items $EditorialPath)

$hostCategoryMap = @{}
foreach ($item in $editorialItems) {
    if ([string]::IsNullOrWhiteSpace($item.Host) -or [string]::IsNullOrWhiteSpace($item.Category)) { continue }
    if (-not $hostCategoryMap.ContainsKey($item.Host)) {
        $hostCategoryMap[$item.Host] = New-Object System.Collections.Generic.List[string]
    }
    if (-not $hostCategoryMap[$item.Host].Contains($item.Category)) {
        [void]$hostCategoryMap[$item.Host].Add($item.Category)
    }
}

$seen = @{}
$combined = New-Object System.Collections.Generic.List[object]
foreach ($item in $legacyItems + $editorialItems) {
    if ([string]::IsNullOrWhiteSpace($item.NormUrl)) { continue }
    if ($seen.ContainsKey($item.NormUrl)) { continue }
    $seen[$item.NormUrl] = $true
    $combined.Add([pscustomobject]@{
        Name = $item.Name
        Text = $item.Text
        Title = $item.Title
        XmlUrl = $item.XmlUrl
        HtmlUrl = $item.HtmlUrl
        Category = (Get-Category $item $hostCategoryMap)
    })
}

$categoryOrder = @('Algeria','Arab_World','Global','Economy','Sports','Tech','Competitors','Alerts','Trends','Entertainment','Uncategorized')

function Write-OpmlFile([string]$path, [string]$title, [object[]]$items, [string[]]$categories) {
    $settings = New-Object System.Xml.XmlWriterSettings
    $settings.Indent = $true
    $settings.Encoding = New-Object System.Text.UTF8Encoding($false)
    $writer = [System.Xml.XmlWriter]::Create($path, $settings)
    $writer.WriteStartDocument()
    $writer.WriteStartElement('opml')
    $writer.WriteAttributeString('version', '2.0')
    $writer.WriteStartElement('head')
    $writer.WriteElementString('title', $title)
    $writer.WriteElementString('dateCreated', (Get-Date -Format 'r'))
    $writer.WriteEndElement()
    $writer.WriteStartElement('body')

    foreach ($category in $categories) {
        $groupItems = @($items | Where-Object { $_.Category -eq $category } | Sort-Object Name)
        if ($groupItems.Count -eq 0) { continue }
        $writer.WriteStartElement('outline')
        $writer.WriteAttributeString('text', $category)
        $writer.WriteAttributeString('title', $category)
        foreach ($item in $groupItems) {
            $writer.WriteStartElement('outline')
            $writer.WriteAttributeString('text', $(if ($item.Text) { $item.Text } else { $item.Name }))
            $writer.WriteAttributeString('title', $(if ($item.Title) { $item.Title } else { $item.Name }))
            $writer.WriteAttributeString('type', 'rss')
            $writer.WriteAttributeString('xmlUrl', $item.XmlUrl)
            if (-not [string]::IsNullOrWhiteSpace($item.HtmlUrl)) {
                $writer.WriteAttributeString('htmlUrl', $item.HtmlUrl)
            }
            $writer.WriteEndElement()
        }
        $writer.WriteEndElement()
    }

    $writer.WriteEndElement()
    $writer.WriteEndElement()
    $writer.WriteEndDocument()
    $writer.Flush()
    $writer.Close()
}

Write-OpmlFile -path $OutputPath -title 'Echorouk Sources Final Categorized' -items $combined -categories $categoryOrder

$strictCategories = @($categoryOrder | Where-Object { $_ -ne 'Uncategorized' })
$strictItems = @($combined | Where-Object { $_.Category -ne 'Uncategorized' })
Write-OpmlFile -path $StrictOutputPath -title 'FreshRSS Master Clean' -items $strictItems -categories $strictCategories

$reviewItems = @($combined | Where-Object { $_.Category -eq 'Uncategorized' })
Write-OpmlFile -path $ReviewOutputPath -title 'Uncategorized Review' -items $reviewItems -categories @('Uncategorized')

Write-Output ('OUT_PATH={0}' -f $OutputPath)
Write-Output ('STRICT_OUT_PATH={0}' -f $StrictOutputPath)
Write-Output ('REVIEW_OUT_PATH={0}' -f $ReviewOutputPath)
Write-Output ('TOTAL={0}' -f $combined.Count)
foreach ($category in $categoryOrder) {
    $count = @($combined | Where-Object { $_.Category -eq $category }).Count
    if ($count -gt 0) {
        Write-Output ('{0}={1}' -f $category, $count)
    }
}
Write-Output ('STRICT_TOTAL={0}' -f $strictItems.Count)
Write-Output ('REVIEW_TOTAL={0}' -f $reviewItems.Count)
