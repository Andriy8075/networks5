Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32 {
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
  public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }
}
"@
$p = Get-Process Wireshark | Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1
if (-not $p) { throw 'Wireshark window not found' }
[Win32]::ShowWindow($p.MainWindowHandle, 3) | Out-Null
[Win32]::SetForegroundWindow($p.MainWindowHandle) | Out-Null
Start-Sleep -Milliseconds 500
$r = New-Object Win32+RECT
[Win32]::GetWindowRect($p.MainWindowHandle, [ref]$r) | Out-Null
$w = $r.Right - $r.Left; $h = $r.Bottom - $r.Top
$bmp = New-Object System.Drawing.Bitmap $w, $h
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($r.Left, $r.Top, 0, 0, (New-Object System.Drawing.Size($w,$h)))
$out = $args[0]
$bmp.Save($out, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
Write-Host "saved $out ($w x $h)"
