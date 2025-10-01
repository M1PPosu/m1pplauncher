using System;
using System.Runtime.InteropServices;
using m1pplauncher.Utils;
using Microsoft.UI.Windowing;
using Microsoft.UI.Xaml;
using Windows.Graphics;

namespace m1pplauncher.Views;

public sealed partial class MainWindow : Window
{
  public MainWindow()
  {
    InitializeComponent();

    AppWindow.SetIcon("Assets/LogoSquare.png");
    Title = "M1PP Lazer Launcher";

    ExtendsContentIntoTitleBar = true;
    SetTitleBar(MainPage.AppTitleBar);
    
    DisplayArea displayArea = DisplayArea.GetFromWindowId(AppWindow.Id, DisplayAreaFallback.Primary);
    AppWindow.Move(new PointInt32(displayArea.WorkArea.X + (displayArea.WorkArea.Width - AppWindow.Size.Width) / 2,
      displayArea.WorkArea.Y + (displayArea.WorkArea.Height - AppWindow.Size.Height) / 2));
    double scale = WinApi.GetScreenScaling(this);
    AppWindow.Resize(new((int)Math.Round(500 * scale), (int)Math.Round(258 * scale)));
  }
}
