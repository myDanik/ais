$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$sourceFont = Join-Path $projectRoot 'assets\fonts\prata\Prata-Regular.ttf'
if (-not (Test-Path -LiteralPath $sourceFont)) { throw 'Download the Prata font first.' }
$fontRoot = Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'Microsoft\Windows\Fonts'
$fontTarget = Join-Path $fontRoot 'Prata-Regular.ttf'
New-Item -ItemType Directory -Path $fontRoot -Force | Out-Null
if (-not (Test-Path -LiteralPath $fontTarget)) { Copy-Item -LiteralPath $sourceFont -Destination $fontTarget }
$fontRegistry = 'HKCU:\Software\Microsoft\Windows NT\CurrentVersion\Fonts'
New-Item -Path $fontRegistry -Force | Out-Null
New-ItemProperty -Path $fontRegistry -Name 'Prata (TrueType)' -Value $fontTarget -PropertyType String -Force | Out-Null
Add-Type @'
using System;
using System.Runtime.InteropServices;
public static class DesignFontRegistration {
    [DllImport("gdi32.dll", CharSet=CharSet.Unicode)]
    public static extern int AddFontResourceEx(string file, uint flags, IntPtr reserved);
    [DllImport("user32.dll", CharSet=CharSet.Unicode, SetLastError=true)]
    public static extern IntPtr SendMessageTimeout(IntPtr window, uint message, IntPtr wparam, IntPtr lparam, uint flags, uint timeout, out IntPtr result);
}
'@
$registeredFonts = [DesignFontRegistration]::AddFontResourceEx($fontTarget, 0, [IntPtr]::Zero)
$broadcastResult = [IntPtr]::Zero
[void][DesignFontRegistration]::SendMessageTimeout([IntPtr]0xffff, 0x001D, [IntPtr]::Zero, [IntPtr]::Zero, 2, 1000, [ref]$broadcastResult)
[PSCustomObject]@{ Font='Prata'; Path=$fontTarget; Registered=$registeredFonts } | ConvertTo-Json -Compress
