
#    this file sets some environment variables that are needed
#    for finding programs and libraries etc.
#    by Hannah von Reth <vonreth@kde.org>
#    you should copy kdesettings.ini to ..\etc\kdesettings.ini
#    and adapt it to your needs (see that file for more info)

#    this file should contain all path settings - and provide thus an environment
#    to build and run kde programs
#    based on kdeenv.bat

cls


$env:CraftRoot=[System.IO.Path]::GetDirectoryName($myInvocation.MyCommand.Definition)

$CRAFT_ARGUMENTS = $args

&{
[version]$minPythonVersion = 3.6

function findPython([string] $name)
{
    $py = (Get-Command $name -ErrorAction SilentlyContinue)
    if ($py -and ($py | Get-Member Version) -and $py.Version -ge $minPythonVersion) {
        $env:CRAFT_PYTHON=$py.Source
    }
}

findPython("python3")
findPython("python")

function readINI([string] $fileName)
{
   $ini = @{}

  switch -regex -file $fileName {
    "^\[(.+)\]$" {
      $section = $matches[1].Trim()
      $ini[$section] = @{}
    }
    "^\s*([^#].+?)\s*=\s*(.*)" {
      $name,$value = $matches[1..2]
      $ini[$section][$name] = $value.Trim()
    }
  }
  $ini
}



if(test-path -path $env:CraftRoot\..\etc\kdesettings.ini)
{
    $settings = readINI $env:CraftRoot\..\etc\kdesettings.ini
}
else
{
    Write-Error("$env:CraftRoot\..\etc\kdesettings.ini Does not exist")
    break
}
if( $CRAFT_ARGUMENTS[0] -eq "--get")
{
    Write-Host($settings[$CRAFT_ARGUMENTS[1]][$CRAFT_ARGUMENTS[2]])
    break
}


function prependPATH([string] $path)
{
    $env:PATH="$path{0}$env:PATH" -f [IO.Path]::PathSeparator
}


if( -Not $env:CRAFT_PYTHON)
{
    prependPATH $settings["Paths"]["Python"]
    $env:CRAFT_PYTHON=[IO.PATH]::COMBINE($settings["Paths"]["Python"], "python")
}

(& $env:CRAFT_PYTHON ([IO.PATH]::COMBINE("$env:CraftRoot", "bin", "CraftSetupHelper.py")) "--setup") |
foreach {
  if ($_ -match "=") {
    $v = $_.split("=")
    set-item -force -path "ENV:\$($v[0])"  -value "$($v[1])"
    #Write-Host("$v[0]=$v[1]")
  }
}

cd "$env:KDEROOT"
}


function Global:craft() {
    return & $env:CRAFT_PYTHON ([IO.PATH]::COMBINE("$env:CraftRoot", "bin", "craft.py")) $args
}

function Global:cb([string] $package) {
    $dir = craft -q --get "buildDir()" $package
    cd $dir
}

function Global:cs([string] $package) {
    $dir = craft -q --get "sourceDir()" $package
    cd $dir
}
function Global:cr() {
    cd $env:KDEROOT
}


if($args.Length -ne 0)
{
    invoke-expression -command "$args"
}

