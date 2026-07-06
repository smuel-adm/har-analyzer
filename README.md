# har-analyzer

Analyze HAR files for performance metrics

## Prequisites

### Install uv

```shell
winget install --id=astral-sh.uv -e
```

or

```shell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Activate uv

```shell
git clone https://github.com/smuel-adm/har-analyzer.git
cd har-analyzer
uv venv
```

## Usage

```shell
uv run har_report.py <file.har>
```
