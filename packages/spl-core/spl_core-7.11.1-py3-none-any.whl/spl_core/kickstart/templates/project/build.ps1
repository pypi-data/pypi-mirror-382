﻿<#
.DESCRIPTION
    Wrapper for installing dependencies, running and testing the project
#>

param(
    [Parameter(Mandatory = $false, HelpMessage = 'Install all dependencies required to build. (Switch, default: false)')]
    [switch]$install = $false,
    [Parameter(Mandatory = $false, HelpMessage = 'Install optional dependencies. (Switch, default: false)')]
    [switch]$installOptional = $false,
    [Parameter(Mandatory = $false, HelpMessage = 'Install Visual Studio Code. (Switch, default: false)')]
    [switch]$installVSCode = $false,
    [Parameter(Mandatory = $false, HelpMessage = 'Run all CI tests (python tests with pytest) (Switch, default: false)')]
    [switch]$selftests = $false,
    [Parameter(Mandatory = $false, HelpMessage = 'Build the target.')]
    [switch]$build = $false,
    [Parameter(Mandatory = $false, HelpMessage = 'Start Visual Studio Code. (Switch, default: false)')]
    [switch]$startVSCode = $false,
    [Parameter(Mandatory = $false, HelpMessage = 'Command to be executed (String)')]
    [string]$command = "",
    [Parameter(Mandatory = $false, HelpMessage = 'Clean build, wipe out all build artifacts. (Switch, default: false)')]
    [switch]$clean = $false,
    [Parameter(Mandatory = $false, HelpMessage = 'Build kit to be used. (String: "prod" or "test", default: "prod")')]
    [string]$buildKit = "prod",
    [Parameter(Mandatory = $false, HelpMessage = 'Type of build. (String, default: "Debug")')]
    [string]$buildType = "Debug",
    [Parameter(Mandatory = $false, HelpMessage = 'Target to be built. (String, default: "all")')]
    [string]$target = "all",
    [Parameter(Mandatory = $false, HelpMessage = 'Variants (of the product) to be built. (List of strings, leave empty to be asked or "all" for automatic build of all variants)')]
    [string[]]$variants = $null,
    [Parameter(Mandatory = $false, HelpMessage = 'filter for self tests, e.g. "Disco or test_Disco.py" (see https://docs.pytest.org/en/stable/usage.html).')]
    [string]$filter = "",
    [Parameter(Mandatory = $false, HelpMessage = 'Marker for self tests, e.g. "static_analysis" (see https://docs.pytest.org/en/stable/how-to/mark.html).')]
    [string]$marker = "",
    [Parameter(Mandatory = $false, HelpMessage = 'Additional build arguments for Ninja (e.g., "-d explain -d keepdepfile" for debugging purposes)')]
    [string]$ninjaArgs = "",
    [Parameter(Mandatory = $false, HelpMessage = 'Delete CMake cache and reconfigure. (Switch, default: false)')]
    [switch]$reconfigure = $false,
    [Parameter(Mandatory = $false, HelpMessage = 'Just configure the build and fetch all dependencies. (Switch, default: false)')]
    [switch]$configureOnly = $false,
    [Parameter(Mandatory = $false, HelpMessage = 'Wait for a key press before exiting. (Switch, default: false)')]
    [switch]$waitForKey = $false
)

# Consider CI environment variables (e.g. on Jenkins BRANCH_NAME and CHANGE_TARGET) to filter tests in release branch builds
function Get-ReleaseBranchPytestFilter {
    $ChangeId = $env:CHANGE_ID
    $BranchName = $env:BRANCH_NAME
    $ChangeTarget = $env:CHANGE_TARGET

    $targetBranch = ''

    if (-not $ChangeId -and $BranchName -and $BranchName.StartsWith("release/")) {
        $targetBranch = $BranchName
    }

    if ($ChangeId -and $ChangeTarget -and $ChangeTarget.StartsWith("release/") ) {
        $targetBranch = $ChangeTarget
    }

    $filter = ''
    if ($targetBranch -and ($targetBranch -match 'release/([^/]+/[^/]+)(.*)')) {
        $filter = $Matches[1].Replace('/', ' and ')
    }

    return $filter
}

# Call build system with given parameters
function Invoke-Build-System {
    param (
        [Parameter(Mandatory = $false)]
        [bool]$clean = $false,
        [Parameter(Mandatory = $false)]
        [bool]$build = $false,
        [Parameter(Mandatory = $false)]
        [string]$buildKit = "prod",
        [Parameter(Mandatory = $false)]
        [string]$buildType = "Debug",
        [Parameter(Mandatory = $true)]
        [string]$target = "all",
        [Parameter(Mandatory = $false)]
        [string[]]$variants = $null,
        [Parameter(Mandatory = $false)]
        [string]$ninjaArgs = "",
        [Parameter(Mandatory = $false)]
        [bool]$reconfigure = $false,
        [Parameter(Mandatory = $false)]
        [bool]$configureOnly = $false
    )
    # Determine variants to be built
    $defaultVariantsFolder = ".\variants\"
    if ((-Not $variants) -or ($variants -eq 'all')) {
        $variantConfigs = Get-Childitem -Include config.cmake -Path $defaultVariantsFolder -Recurse | Resolve-Path -Relative
        $variantsList = @()
        Foreach ($variantConfig in $variantConfigs) {
            $variant = ((Get-Item $variantConfig).Directory | Resolve-Path -Relative).Replace($defaultVariantsFolder, "").Replace("\", "/")
            $variantsList += $variant
        }
        $variantsSelected = @()
        if (-Not $variants) {
            # variant selection by user if not specified
            Write-Information -Tags "Info:" -MessageData "no '--variant <variant>' was given, please select from list:"
            Write-Information -Tags "Info:" -MessageData ("(0) all variants")
            Foreach ($variant in $variantsList) {
                Write-Information -Tags "Info:" -MessageData ("(" + ([array]::IndexOf($variantsList, $variant) + 1) + ") " + $variant)
            }
            $selection = [int](Read-Host "Please enter selected variant number")
            if ($selection -eq 0) {
                # build all variants
                $variantsSelected = $variantsList
            }
            else {
                # build selected variant
                $variantsSelected += $variantsList[$selection - 1]
            }
            Write-Information -Tags "Info:" -MessageData "Selected variants: $variantsSelected"
        }
        else {
            # otherwise build all variants
            $variantsSelected = $variantsList
        }
    }
    else {
        $variantsSelected = $Variants.Replace($defaultVariantsFolder, "").Replace("\", "/").Split(',') | ForEach-Object { $_.TrimEnd('/') }
    }

    # Select 'test' build kit based on target
    if ($target.Contains("unittests") -or $target.Contains("reports")) {
        $buildKit = "test"
    }
    # If buildKit is 'test' then buildType is 'Debug'
    if ($buildKit -eq "test") {
        $buildType = "Debug"
    }

    Foreach ($variant in $variantsSelected) {
        $buildFolder = "build\$variant\$buildKit\$buildType".Replace("/", "\")
        # fresh and clean build
        if ($clean) {
            Remove-Path $buildFolder
        }
        New-Directory $buildFolder

        # delete CMake cache and reconfigure
        if ($reconfigure -or $configureOnly) {
            Remove-Path "$buildFolder\CMakeCache.txt"
            Remove-Path "$buildFolder\CMakeFiles"
        }

        if ($build) {
            Write-Output "Building target '$target' with build kit '$buildKit' and build type '$buildType' for variant '$variant' ..."

            # CMake configure
            $additionalConfig = "-DBUILD_KIT='$buildKit'"
            $additionalConfig += " -DBUILD_TYPE='$buildType'"
            if ($buildKit -eq "test") {
                $additionalConfig += " -DCMAKE_TOOLCHAIN_FILE='tools/toolchains/gcc/toolchain.cmake'"
            }

            Invoke-CommandLine -CommandLine "cmake -B '$buildFolder' -G Ninja -DVARIANT='$variant' $additionalConfig"

            if (-Not $configureOnly) {
                $cmd = "cmake --build '$buildFolder' --config '$buildType' --target $target"

                # CMake clean all dead artifacts. Required when running incremented builds to delete obsolete artifacts.
                Invoke-CommandLine -CommandLine "$cmd -- -t cleandead"
                # CMake build
                Invoke-CommandLine -CommandLine "$cmd -- $ninjaArgs"
            }
        }
    }
}

function Invoke-Self-Tests {
    param (
        [Parameter(Mandatory = $false)]
        [bool]$clean = $false,
        [Parameter(Mandatory = $false)]
        [string]$filter = "",
        [Parameter(Mandatory = $false)]
        [string]$marker = ""
    )

    # Run python tests to test all relevant variants and platforms (build kits)
    # (normally run in CI environment/Jenkins)
    Write-Output "Running all self tests ..."

    if ($clean) {
        # Remove all build outputs in one step, this will remove obsolete variants, too.
        Remove-Path "build"
    }

    # Test result of pytest
    $pytestJunitXml = "test/output/test-report.xml"

    # Delete any old pytest result
    Remove-Path $pytestJunitXml

    $pytestArgs = @(
        "--junitxml=$pytestJunitXml"
    )

    # Filter pytest test cases
    $releaseBranchFilter = Get-ReleaseBranchPytestFilter
    if ($releaseBranchFilter) {
        $pytestArgs += "-k '$releaseBranchFilter'"
    }
    # otherwise consider command line option '-filter' if given
    elseif ($filter) {
        $pytestArgs += "-k '$filter'"
    }

    # Execute marker tests
    if ($marker) {
        $pytestArgs += "-m '$marker'"
    }

    # Finally run pytest and ignore return value. Content of test-report.xml will be evaluated by CI system.
    $commandLine = "pytest " + ($pytestArgs -join " ")
    Invoke-CommandLine -CommandLine $commandLine -StopAtError $false
}

function Remove-Path {
    param (
        [Parameter(Mandatory = $true, Position = 0)]
        [string]$path
    )
    if (Test-Path -Path $path -PathType Container) {
        Write-Output "Deleting directory '$path' ..."
        Remove-Item $path -Force -Recurse
    }
    elseif (Test-Path -Path $path -PathType Leaf) {
        Write-Output "Deleting file '$path' ..."
        Remove-Item $path -Force
    }
}

function New-Directory {
    param (
        [Parameter(Mandatory = $true, Position = 0)]
        [string]$dir
    )
    if (-Not (Test-Path -Path $dir)) {
        Write-Output "Creating directory '$dir' ..."
        New-Item -ItemType Directory $dir
    }
}

function Get-User-Menu-Selection {
    Clear-Host
    Write-Information -Tags "Info:" -MessageData "None of the following command line options was given:"
    Write-Information -Tags "Info:" -MessageData ("(1) -install: installation of mandatory dependencies")
    Write-Information -Tags "Info:" -MessageData ("(2) -installOptional: installation of optional dependencies")
    Write-Information -Tags "Info:" -MessageData ("(3) -installVSCode: installation of Visual Studio Code")
    Write-Information -Tags "Info:" -MessageData ("(4) -build: execute CMake build")
    Write-Information -Tags "Info:" -MessageData ("(5) -startVSCode: start Visual Studio Code")
    Write-Information -Tags "Info:" -MessageData ("(6) quit: exit script")
    return(Read-Host "Please make a selection")
}

function Invoke-Bootstrap {
    # Download bootstrap scripts from external repository
    Invoke-RestMethod -Uri https://raw.githubusercontent.com/avengineers/bootstrap-installer/v1.17.1/install.ps1 | Invoke-Expression
    # Execute bootstrap script
    . .\.bootstrap\bootstrap.ps1
}

## start of script
# Always set the $InformationPreference variable to "Continue" globally,
# this way it gets printed on execution and continues execution afterwards.
$InformationPreference = "Continue"

# Stop on first error
$ErrorActionPreference = "Stop"

Push-Location $PSScriptRoot
Write-Output "Running in ${pwd}"

try {
    if ((-Not $install) -and (-Not $installOptional) -and (-Not $installVSCode) -and (-Not $build) -and (-Not $startVSCode) -and (-Not $command) -and (-Not $selftests)) {
        $selectedOption = Get-User-Menu-Selection

        switch ($selectedOption) {
            '1' {
                Write-Information -Tags "Info:" -MessageData "Installing mandatory dependencies ..."
                $install = $true
            }
            '2' {
                Write-Information -Tags "Info:" -MessageData "Installing optional dependencies ..."
                $installOptional = $true
            }
            '3' {
                Write-Information -Tags "Info:" -MessageData "Installing Visual Studio Code ..."
                $installVSCode = $true
            }
            '4' {
                Write-Information -Tags "Info:" -MessageData "Building ..."
                $build = $true
            }
            '5' {
                Write-Information -Tags "Info:" -MessageData "Starting VS Code ..."
                $startVSCode = $true
            }
            default {
                Write-Information -Tags "Info:" -MessageData "Nothing selected."
                exit
            }
        }
    }

    if ($install) {
        if ($clean) {
            Remove-Path ".venv"
        }

        # bootstrap environment
        Invoke-Bootstrap

        Write-Host -ForegroundColor Black -BackgroundColor Blue "For installation changes to take effect, please close and re-open your current terminal."
    }

    # Load bootstrap's utility functions
    . .\.bootstrap\utils.ps1

    Invoke-CommandLine ".venv\Scripts\pypeline run --step GenerateEnvSetupScript"

    # Load environment setup script
    . .\build\env_setup.ps1

    if ($installOptional) {
        Import-ScoopFile "scoopfile-optional.json"
    }

    if ($installVSCode) {
        Invoke-CommandLine "scoop bucket add extras" -StopAtError $false
        Invoke-CommandLine "scoop install vscode"
        Invoke-CommandLine "scoop update vscode" -StopAtError $false
    }

    if ($startVSCode) {
        Write-Output "Starting Visual Studio Code..."
        Invoke-CommandLine "code ." -StopAtError $false
    }

    if ($build) {
        # Call build system to build variant(s)
        Invoke-Build-System `
            -clean $clean `
            -build $build `
            -target $target `
            -buildKit $buildKit `
            -buildType $buildType `
            -variants $variants `
            -reconfigure $reconfigure `
            -configureOnly $configureOnly `
            -ninjaArgs $ninjaArgs
    }

    if ($selftests) {
        Invoke-Self-Tests -clean $clean -filter $filter -marker $marker
    }

    if ($command -ne '') {
        Invoke-Expression "$command"
    }
}
finally {
    Pop-Location
    if (-Not (Test-RunningInCIorTestEnvironment) -and $waitForKey) {
        Read-Host -Prompt "Press Enter to continue ..."
    }
}
## end of script
