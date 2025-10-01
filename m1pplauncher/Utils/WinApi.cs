using System.Runtime.InteropServices;
using Microsoft.UI.Xaml;
using WinRT.Interop;

namespace m1pplauncher.Utils;

internal static class WinApi
{
  [DllImport("user32.dll")]
  private static extern uint GetDpiForWindow(nint hWnd);

  public static double GetScreenScaling(Window window) => GetDpiForWindow(WindowNative.GetWindowHandle(window)) / 96;
}
