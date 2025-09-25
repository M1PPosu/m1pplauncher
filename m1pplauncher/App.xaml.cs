using System.Globalization;
using m1pplauncher.Views;
using Microsoft.UI.Windowing;
using Microsoft.UI.Xaml;

namespace m1pplauncher;

public partial class App : Application
{
  public const string VERSION_BASE = "0.1.0";
  public const string VERSION = VERSION_BASE + VERSION_EXTRA;
#if DEBUG
  private const string VERSION_EXTRA = "-dev";
#else
  private const string VERSION_EXTRA = "";
#endif

  public static MainWindow MainWindow { get; } = new();

  public App()
  {
    InitializeComponent();

    CultureInfo.DefaultThreadCurrentCulture = CultureInfo.InvariantCulture;
  }

  protected override void OnLaunched(LaunchActivatedEventArgs args)
  {
    OverlappedPresenter presenter = (OverlappedPresenter)MainWindow.AppWindow.Presenter;
    presenter.IsMaximizable = false;
    presenter.IsResizable = false;

    MainWindow.Activate();
  }
}
